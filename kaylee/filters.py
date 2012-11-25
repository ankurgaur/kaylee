from functools import wraps

from .util import encrypt, decrypt
from .errors import ApplicationCompletedError

#  TODO: add link to kl.NO_SOLUTION
#: The { '__kl_result__' : NO_SOLUTION } result returned by the node
#: indicates that no solution was found for the given task. The controller
#: must take this information into account (see :func:`kl_result_filter`)
NO_SOLUTION = 0x2

#: The { '__kl_result__' : NEXT_TASK } solution returned by the node
#: indicates that the current task was simply not solved for some
#: reason, there are no results to accept and the node is asking for
#: the next task.
NEXT_TASK = 0x4

KL_RESULT = '__kl_result__'

SESSION_DATA_ATTRIBUTE = '__kl_tsd__'

def app_completed_guard(f):
    """The filter handles two cases of completed Kaylee application:

    1. First, it checks if the application has already completed and
       in that case immediately throws :exc:`ApplicationCompletedError`.
    2. Second, it wraps ``f`` in ``try..except`` block in order to
       set object's :attr:`Controller.completed` value to ``True``.
       After that :exc:`ApplicationCompletedError` is re-raised.

    *Signature*: ``(self, *args, **kwargs)``
    .. note:: This is a base filter applied to :meth:`Controller.get_task`.
    """
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if self.completed:
            raise ApplicationCompletedError(self.name)

        try:
            return f(self, *args, **kwargs)
        except ApplicationCompletedError as e:
            self.completed = True
            raise e
    return wrapper

def normalize_result_filter(f):
    """The filter normalizes the data before passing it further.

    *Signature*: ``(self, node, data)``
    .. note:: This is a base filter applied to :meth:`
              Controller.accept_result`.
    """
    @wraps(f)
    def wrapper(self, node, data):
        data = self.project.normalize_result(node.task_id, data)
        return f(self, node, data)
    return wrapper

def kl_result_filter(f):
    """The filter is designed to be used in "decision search" projects which
    imply that not every task has a correct solution, or solution exists at
    all.
    The filter searches for ``'__kl_result__'`` key in the result and acts
    according to the bound value:

    * :data:`NO_SOLUTION` : The result passed to the decorated function is
      turned to `None`. It can be ignored by :meth:`Project.store_result`
      routine.

    *Signature*: ``(self, node, data)``
    """
    @wraps(f)
    def wrapper(self, node, data):
        try:
            kl_result = data['__kl_result__']
        except (KeyError, TypeError):
            return f(self, node, data)

        if kl_result == NO_SOLUTION:
            data = None
            return f(self, node, data)
        elif kl_result == NEXT_TASK:
            return

    return wrapper


def ignore_null_result(f):
    """Ignores ``None`` data by **not** calling the wrapped method.

    *Signature*: ``(self, task_id, data)``

    .. note:: This is a base filter applied to :meth:`Project.normalize_result`
              and :meth:`Project.store_result`.
    """
    @wraps(f)
    def wrapper(self, task_id, data):
        if data is not None:
            return f(self, task_id, data)
        return None
    return wrapper


def accepts_session_data(f):
    """Automatically decrypts session data and attaches it to the results.

    The filter can be effectively applied to Project.normalize_result() in
    order to handle the project tasks' session data. The filter works as
    follows:

    1. Get encrypted session data from the incoming results (dict)
    2. Decrypt session data -> dict
    3. Update the results with the session data
    4. Remove the encrypted session data from the results dict.

    *Signature*: ``(self, task_id, data)``
    """
    @wraps(f)
    def wrapper(self, task_id, data):
        if not isinstance(data, dict):
            raise ValueError('Cannot attach session data to a non-dict result')
        sd = decrypt(data[SESSION_DATA_ATTRIBUTE])
        data.update(sd)
        return f(self, task_id, data)
    return wrapper


# def attach_task_id_to_returned_value(f):
#     """TODOC, TODO:TEST"""
#     @wraps(f)
#     def wrapper(self, task_id):
#         res = f(self, task_id)
#         res['id'] = task_id
#         return res
#     return wrapper


def returns_session_data(f):
    """TODOC, TODO:TEST"""
    @wraps(f)
    def wrapper(self, task_id):
        task = f(self, task_id)
        hashed_data = { key : task[key] for key in task
                        if key.startswith('#') }
        # encrypt and attach data to the task
        task[SESSION_DATA_ATTRIBUTE] = encrypt(hashed_data)
        # remove the just encrypted key-value pairs, as they are
        # no longer required
        for key in hashed_data:
            del task[key]
        return task
    return wrapper

