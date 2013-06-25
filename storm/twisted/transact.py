import time
import random
import transaction

from functools import wraps

from zope.component import getUtility

from storm.zope.interfaces import IZStorm
from storm.exceptions import IntegrityError, DisconnectionError

from twisted.internet.threads import deferToThreadPool


class Transactor(object):
    """Run in a thread code that needs to interact with the database.

    This class makes sure that code interacting with the database is run
    in a separate thread and that the associated transaction is aborted or
    committed in the same thread.

    @param threadpool: The C{ThreadPool} to get threads from.
    @param _transaction: The C{TransactionManager} to use, for test cases only.

    @ivar retries: Maximum number of retries upon retriable exceptions. The
        default is to retry a function up to 2 times upon possibly transient
        or spurious errors like L{IntegrityError} and L{DisconnectionError}.

    @see: C{twisted.python.threadpool.ThreadPool}
    """
    retries = 2

    def __init__(self, threadpool, _transaction=None):
        self._threadpool = threadpool
        if _transaction is None:
            _transaction = transaction
        self._transaction = _transaction
        self._retriable_errors = (DisconnectionError, IntegrityError)
        try:
            from psycopg2.extensions import TransactionRollbackError
            self._retriable_errors += (TransactionRollbackError,)
        except ImportError:
            pass

    def run(self, function, *args, **kwargs):
        """Run C{function} in a thread.

        The function is run in a thread by a function wrapper, which
        commits the transaction if the function runs successfully. If it
        raises an exception the transaction is aborted.

        @param function: The function to run.
        @param args: Positional arguments to pass to C{function}.
        @param kwargs: Keyword arguments to pass to C{function}.
        @return: A C{Deferred} that will fire after the function has been run.
        """
        # Inline the reactor import here for sake of safeness, in case a
        # custom reactor needs to be installed
        from twisted.internet import reactor
        return deferToThreadPool(
            reactor, self._threadpool, self._wrap, function, *args, **kwargs)

    def _wrap(self, function, *args, **kwargs):
        retries = 0
        while True:
            try:
                result = function(*args, **kwargs)
                self._transaction.commit()
            except self._retriable_errors, error:
                if isinstance(error, DisconnectionError):
                    # If we got a disconnection, calling rollback may not be
                    # enough because psycopg2 doesn't necessarily use the
                    # connection, so we call a dummy query to be sure that all
                    # the stores are correct.
                    zstorm = getUtility(IZStorm)
                    for name, store in zstorm.iterstores():
                        try:
                            store.execute("SELECT 1")
                        except DisconnectionError:
                            pass
                self._transaction.abort()
                if retries < self.retries:
                    retries += 1
                    time.sleep(random.uniform(1, 2 ** retries))
                    continue
                else:
                    raise
            except:
                self._transaction.abort()
                raise
            else:
                return result


def transact(method):
    """Decorate L{method} so that it is invoked via L{Transactor.run}.

    @param method: The method to decorate.
    @return: A decorated method.

    @note: The return value of the decorated method should *not* contain
        any reference to Storm objects, because they were retrieved in
        a different thread and cannot be used outside it.

    Example:

    from twisted.python.threadpool import ThreadPool
    from storm.twisted.transact import Transactor, transact

    class Foo(object):

        def __init__(self, transactor):
            self.transactor = transactor

        @transact
        def bar(self):
            # code that uses Storm

    threadpool = ThreadPool(0, 10)
    threadpool.start()
    transactor = Transactor(threadpool)
    foo = Foo(transactor)
    deferred = foo.bar()
    deferred.addCallback(...)
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        return self.transactor.run(method, self, *args, **kwargs)
    return wrapper
