import transaction

from twisted.python.failure import Failure
from twisted.internet.defer import execute


class FakeThreadPool(object):
    """
    A fake L{twisted.python.threadpool.ThreadPool}, running functions inside
    the main thread instead for easing tests.
    """

    def callInThreadWithCallback(self, onResult, func, *args, **kw):
        success = True
        try:
            result = func(*args, **kw)
        except:
            result = Failure()
            success = False

        onResult(success, result)


class FakeTransactor(object):
    """
    A fake C{Transactor} wrapper that runs the given function in the main
    thread and performs basic checks on its return value.  If it has a
    C{__storm_table__} property a C{RuntimeError} is raised because Storm
    objects cannot be used outside the thread in which they were created.

    @see L{Transactor}.
    """

    def __init__(self, _transaction=None):
        if _transaction is None:
            _transaction = transaction
        self._transaction = _transaction

    def run(self, function, *args, **kwargs):
        return execute(self._wrap, function, *args, **kwargs)

    def _wrap(self, function, *args, **kwargs):
        try:
            result = function(*args, **kwargs)
            if getattr(result, "__storm_table__", None) is not None:
                raise RuntimeError("Attempted to return a Storm object from a "
                                   "transaction")
        except:
            self._transaction.abort()
            raise
        else:
            try:
                self._transaction.commit()
            except:
                self._transaction.abort()
                raise
            return result
