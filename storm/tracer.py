from datetime import datetime
import re
import sys
import threading

# Circular import: imported at the end of the module.
# from storm.database import convert_param_marks
from storm.exceptions import TimeoutError
from storm.expr import Variable


class DebugTracer(object):

    def __init__(self, stream=None):
        if stream is None:
            stream = sys.stderr
        self._stream = stream

    def connection_raw_execute(self, connection, raw_cursor, statement, params):
        time = datetime.now().isoformat()[11:]
        raw_params = []
        for param in params:
            if isinstance(param, Variable):
                raw_params.append(param.get())
            else:
                raw_params.append(param)
        raw_params = tuple(raw_params)
        self._stream.write(
            "[%s] EXECUTE: %r, %r\n" % (time, statement, raw_params))
        self._stream.flush()

    def connection_raw_execute_error(self, connection, raw_cursor,
                                     statement, params, error):
        time = datetime.now().isoformat()[11:]
        self._stream.write("[%s] ERROR: %s\n" % (time, error))
        self._stream.flush()

    def connection_raw_execute_success(self, connection, raw_cursor,
                                       statement, params):
        time = datetime.now().isoformat()[11:]
        self._stream.write("[%s] DONE\n" % time)
        self._stream.flush()


class TimeoutTracer(object):
    """Provide a timeout facility for connections to prevent rogue operations.

    This tracer must be subclassed by backend-specific implementations that
    override C{connection_raw_execute_error}, C{set_statement_timeout} and
    C{get_remaining_time} methods.
    """

    def __init__(self, granularity=5):
        self.granularity = granularity

    def connection_raw_execute(self, connection, raw_cursor, statement,
                               params):
        """Check timeout conditions before a statement is executed.

        @param connection: The L{Connection} to the database.
        @param raw_cursor: A cursor object, specific to the backend being used.
        @param statement: The SQL statement to execute.
        @param params: The parameters to use with C{statement}.
        @raises TimeoutError: Raised if there isn't enough time left to
            execute C{statement}.
        """
        remaining_time = self.get_remaining_time()
        if remaining_time <= 0:
            raise TimeoutError(
                statement, params,
                "%d seconds remaining in time budget" % remaining_time)

        last_remaining_time = getattr(connection,
                                      "_timeout_tracer_remaining_time", 0)
        if (remaining_time > last_remaining_time or
            last_remaining_time - remaining_time >= self.granularity):
            self.set_statement_timeout(raw_cursor, remaining_time)
            connection._timeout_tracer_remaining_time = remaining_time

    def connection_raw_execute_error(self, connection, raw_cursor,
                                     statement, params, error):
        """Raise TimeoutError if the given error was a timeout issue.

        Must be specialized in the backend.
        """
        raise NotImplementedError("%s.connection_raw_execute_error() must be "
                                  "implemented" % self.__class__.__name__)

    def set_statement_timeout(self, raw_cursor, remaining_time):
        """Perform the timeout setup in the raw cursor.

        The database should raise an error if the next statement takes
        more than the number of seconds provided in C{remaining_time}.

        Must be specialized in the backend.
        """
        raise NotImplementedError("%s.set_statement_timeout() must be "
                                  "implemented" % self.__class__.__name__)

    def get_remaining_time(self):
        """Tells how much time the current context (HTTP request, etc) has.

        Must be specialized with application logic.

        @return: Number of seconds allowed for the next statement.
        """
        raise NotImplementedError("%s.get_remaining_time() must be implemented"
                                  % self.__class__.__name__)


class BaseStatementTracer(object):
    """Storm tracer base class that does query interpolation."""

    def connection_raw_execute(self, connection, raw_cursor,
                               statement, params):
        statement_to_log = statement
        if params:
            # There are some bind parameters so we want to insert them into
            # the sql statement so we can log the statement.
            query_params = list(connection.to_database(params))
            if connection.param_mark == '%s':
                # Double the %'s in the string so that python string formatting
                # can restore them to the correct number. Note that %s needs to
                # be preserved as that is where we are substituting values in.
                quoted_statement = re.sub(
                    "%%%", "%%%%", re.sub("%([^s])", r"%%\1", statement))
            else:
                # Double all the %'s in the statement so that python string
                # formatting can restore them to the correct number. Any %s in
                # the string should be preserved because the param_mark is not
                # %s.
                quoted_statement = re.sub("%", "%%", statement)
                quoted_statement = convert_param_marks(
                    quoted_statement, connection.param_mark, "%s")
            # We need to massage the query parameters a little to deal with
            # string parameters which represent encoded binary data.
            render_params = []
            for param in query_params:
                if isinstance(param, unicode):
                    render_params.append(repr(param.encode('utf8')))
                else:
                    render_params.append(repr(param))
            try:
                statement_to_log = quoted_statement % tuple(render_params)
            except TypeError:
                statement_to_log = \
                    "Unformattable query: %r with params %r." % (
                    statement, query_params)
        self._expanded_raw_execute(connection, raw_cursor, statement_to_log)

    def _expanded_raw_execute(self, connection, raw_cursor, statement):
        """Called by connection_raw_execute after parameter substitution."""
        raise NotImplementedError(self._expanded_raw_execute)


class TimelineTracer(BaseStatementTracer):
    """Storm tracer class to insert executed statements into a L{Timeline}.

    For more information on timelines see the module at
    http://pypi.python.org/pypi/timeline.
    
    The timeline to use is obtained by calling the timeline_factory supplied to
    the constructor. This simple function takes no parameters and returns a
    timeline to use. If it returns None, the tracer is bypassed.
    """

    def __init__(self, timeline_factory, prefix='SQL-'):
        """Create a TimelineTracer.

        @param timeline_factory: A factory function to produce the timeline to
            record a query against.
        @param prefix: A prefix to give the connection name when starting an
            action. Connection names are found by trying a getattr for 'name'
            on the connection object. If no name has been assigned, '<unknown>'
            is used instead.
        """
        super(TimelineTracer, self).__init__()
        self.timeline_factory = timeline_factory
        self.prefix = prefix
        # Stores the action in progress in a given thread.
        self.threadinfo = threading.local()

    def _expanded_raw_execute(self, connection, raw_cursor, statement):
        timeline = self.timeline_factory()
        if timeline is None:
            return
        connection_name = getattr(connection, 'name', '<unknown>')
        action = timeline.start(self.prefix + connection_name, statement)
        self.threadinfo.action = action

    def connection_raw_execute_success(self, connection, raw_cursor,
                                       statement, params):
                                       
        # action may be None if the tracer was installed after the statement
        # was submitted.
        action = getattr(self.threadinfo, 'action', None)
        if action is not None:
            action.finish()

    def connection_raw_execute_error(self, connection, raw_cursor,
                                     statement, params, error):
        # Since we are just logging durations, we execute the same
        # hook code for errors as successes.
        self.connection_raw_execute_success(
            connection, raw_cursor, statement, params)


_tracers = []

def trace(name, *args, **kwargs):
    for tracer in _tracers:
        attr = getattr(tracer, name, None)
        if attr:
            attr(*args, **kwargs)

def install_tracer(tracer):
    _tracers.append(tracer)

def get_tracers():
    return _tracers[:]

def remove_all_tracers():
    del _tracers[:]

def remove_tracer_type(tracer_type):
    for i in range(len(_tracers)-1, -1, -1):
        if type(_tracers[i]) is tracer_type:
            del _tracers[i]

def debug(flag, stream=None):
    remove_tracer_type(DebugTracer)
    if flag:
        install_tracer(DebugTracer(stream=stream))

# Deal with circular import.        
from storm.database import convert_param_marks
