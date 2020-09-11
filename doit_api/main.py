from inspect import isgeneratorfunction
from os.path import exists

try:
    from typing import Callable, Union, List, Tuple, Dict, Optional
    from pathlib import Path

    DoitAction = Union[str, List, Callable, Tuple[Callable, Tuple, Dict]]
    DoitTask = Union[str, Callable, 'task', 'taskgen']
    DoitPath = Union[str, Path]
except ImportError:
    pass

from doit.action import CmdAction


# --- task utilities


def why_am_i_running(task, changed):
    """
    Goodie: a python action that you can use in any `doit` task, to print the reason why the task is running if the
    task declared a `file_dep`, `task_dep`, `uptodate` or `targets`. Useful for debugging.
    See [this doit conversation](https://github.com/pydoit/doit/issues/277).
    """
    for t in task.targets:
        if not exists(t):
            print("Running %s because one of its targets does not exist anymore: %r" % (task, t))
            return

    if changed is None or len(changed) == 0:
        # silence
        # print("Running %s because it declares no mechanism (file_dep or target) to avoid useless executions." % task)
        pass
    else:
        print("Running %s because the following changed: %r" % (task, changed))


def title_with_actions(task):
    """
    Goodie: an automatic title for doit tasks.
    Same than `doit.title_with_actions` but removes `why_am_i_running` actions if any is present.
    """

    if task.actions:
        title = "\n\t".join([str(action) for action in task.actions
                             if not hasattr(action, 'py_callable') or action.py_callable is not why_am_i_running])
    # A task that contains no actions at all
    # is used as group task
    else:
        title = "Group: %s" % ", ".join(task.task_dep)
    return "%s => %s" % (task.name, title)


# ----------- tasks creators

def validate_action(a):
    """
    Internal helper to validate an action. Validates the conventions in https://pydoit.org/tasks.html#actions

     - a command action = A string (command to be executed with the shell) or a list of strings or pathlib Paths
       (command to be executed without the shell).
       See https://pydoit.org/tasks.html#cmd-action

     - a python action = a python callable or a tuple (callable, *args, **kwargs).
       See https://pydoit.org/tasks.html#python-action

    :param a:
    :return:
    """
    if isinstance(a, str):
        # command action with the shell (Popen argument shell=True)
        pass
    elif isinstance(a, list):
        # command action without the shell (Popen argument shell=False)
        pass
    elif isinstance(a, tuple):
        # python callable with args and kwargs
        # assert len(a) == 3
        # assert callable(a[0])
        pass
    elif callable(a):
        pass
    elif isinstance(a, CmdAction):
        pass
    else:
        raise ValueError("Action %r is not a valid action" % a)


def replace_task_names(list_of_tasks):
    """internal helper to replace tasks with their names in a list"""
    def gen_all():
        for o in list_of_tasks:
            if isinstance(o, task):
                yield o.name
            elif isinstance(o, taskgen):
                yield o.name
            elif callable(o):
                yield o.__name__.replace('task_', '')
            else:
                # a string task name
                yield o
    return list(gen_all())


class taskbase(object):
    """ Base class for `task` and `taskgen`. """
    def __init__(self,
                 name,  # type: str
                 doc,   # type: str
                 title  # type: Union[str, Callable]
                 ):
        """

        :param name: an alternate base name for the task. By default the name of the decorated function is used.
            See https://pydoit.org/tasks.html#task-name
        :param title: an optional message string or callable generating a message, to print when the task is run. If
            nothing is provided, by default the task name is printed. If a string is provided, the task name will
            automatically be printed before it. If a callable is provided it should receive a single `task` argument
            and return a string. See https://pydoit.org/tasks.html#title
        :param doc: an optional documentation string for the task. If `@task` is used as a decorator, the decorated
            function docstring will be used. See https://pydoit.org/tasks.html#doc
        """
        self._name = name
        self.doc = doc
        self.title=title
        self.func = None
        self.actions = None

    @property
    def name(self):
        if self._name is not None:
            return self._name
        elif self.func:
            return self.func.__name__
        else:
            raise ValueError("You must provide a task basename if you do not use task as a decorator. "
                             "Actions: %r" % self.actions)

    def get_base_desc(self, is_subtask=False, **additional_meta):
        task_dict = dict()

        # base name
        if is_subtask:
            task_dict.update(name=self.name)
        else:
            task_dict.update(basename=self.name)

        # doc
        if self.doc is not None:
            task_dict.update(doc=self.doc)
        elif self.func:
            task_dict.update(doc=self.func.__doc__)

        # title
        if self.title is not None:
            if isinstance(self.title, str):
                # a string: doit does not support this, so create a callable with a simple format.
                def make_title(task):
                    return "%s => %s" % (task.name, self.title)

                task_dict.update(title=make_title)
            else:
                # a callable already
                task_dict.update(title=self.title)

        # update with additional meta if provided
        task_dict.update(additional_meta)

        return task_dict


class task(taskbase):
    """
    Creates a doit task. It may be used as a decorator or as a creator:

    ```python
    from doit_api import task

    @task
    def a():
        print("hi")

    @task(targets=..., file_deps=..., ...)
    def b():
        print("hi")

    c = task(actions=["echo hi"])
    ```

    It signature regroups all options that you usually can set on a `doit` task, with sensible defaults. See constructor
    for details.

    Note: this relies on the `create_doit_tasks` hook, see https://pydoit.org/task_creation.html#custom-task-definition
    """

    def __init__(self,
                 _func=None,
                 # *,  (support for python 2: no kw only args)
                 # -- task information
                 name=None,                   # type: str
                 doc=None,                    # type: str
                 # -- what the task is doing when run
                 title=title_with_actions,    # type: Union[str, Callable]
                 pre_actions=None,            # type: List[DoitAction]
                 actions=None,                # type: List[DoitAction]
                 post_actions=None,           # type: List[DoitAction]
                 tell_why_am_i_running=True,  # type: bool
                 # -- preventing useless runs and selecting order
                 targets=None,                # type: List[DoitPath]
                 file_dep=None,               # type: List[DoitPath]
                 task_dep=None,               # type: List[DoitTask]
                 uptodate=None,               # type: List[Optional[Union[bool, Callable, str]]]
                 # -- advanced
                 setup=None,                  # type: List[DoitTask]
                 teardown=None,               # type: List[DoitAction]
                 getargs=None,                # type: Dict[str, Tuple[str, str]]
                 calc_dep=None,               # type: List[DoitTask]
                 # -- misc
                 verbosity=None               # type: int
                 ):
        """
        A minimal `doit` task consists of one or several actions. When `@task` is used as a decorator, the main action
        is a call to the decorated function. Otherwise when `task` is used as a creator, you must provide at least one
        action in `actions`. You can specify actions to be done before and after that/these `actions` in `pre_actions`
        and `post_actions`. If `tell_why_i_am_runnin=True` (default) an additional action will be prepended to print
        the reason why the task is running.

        All other parameters match those in `doit` conventions (See docstrings below), except

         - `name` that is an intelligent placeholder for `basename` (if a task is a simple task) or `name` (if the task
           is a subtask in a `@taskgen` generator),
         - `title` that adds support for plain strings and by default is `title_with_actions`
         - `task_dep`, `setup` and `calc_dep` where if a task callable (decorated with `@task` or not) is provided, the
           corresponding name will be used.

        Note: the `watch` parameter (Linux and Mac only) is not yet supported.
        See https://pydoit.org/cmd_other.html?highlight=watch#auto-watch

        :param name: an alternate name for the task. By default the name of the decorated function is used. Note that
            this parameter will intelligently set 'basename' for normal tasks or 'name' for subtasks in a task
            generator (`@taskgen`). See https://pydoit.org/tasks.html#task-name
        :param doc: an optional documentation string for the task. If `@task` is used as a decorator, the decorated
            function docstring will be used. See https://pydoit.org/tasks.html#doc
        :param title: an optional message string or callable generating a message, to print when the task is run. If
            nothing is provided, by default the task name is printed. If a string is provided, the task name will
            automatically be printed before it. If a callable is provided it should receive a single `task` argument
            and return a string. See https://pydoit.org/tasks.html#title
        :param pre_actions: an optional list of actions to be executed before the main action(s).
            There are 2 basic kinds of actions: cmd-action and python-action. See https://pydoit.org/tasks.html#actions
        :param actions: a list of actions that this task should execute. If `task` is used as a decorator, this
            attribute should not be set, as the action will be a call to the decorated function.
            There are 2 basic kinds of actions: cmd-action and python-action. See https://pydoit.org/tasks.html#actions
        :param post_actions: an optional list of actions to be executed after the main action(s).
            There are 2 basic kinds of actions: cmd-action and python-action. See https://pydoit.org/tasks.html#actions
        :param tell_why_am_i_running: if True (default), an additional `why_am_i_running` action is prepended to the
            list of actions
        :param file_dep: an optional list of strings or instances of any pathlib Path class indicating the files
            required for this task to run. When none of these files are modified, the task will be skipped if already
            run. See https://pydoit.org/tasks.html#file-dep-file-dependency
        :param task_dep: an optional list of tasks (names or callables) that should be run *before* this task. Note
            that this is also a convenient way to create a group of tasks.
            See https://pydoit.org/dependencies.html#task-dependency
        :param uptodate: an optional list where each element can be True (up to date), False (not up to date),
            None (ignored), a callable or a command(string). Many pre-baked callables from `doit.tools` can be used:
            `result_dep` to depend on the result of another task, `run_once` to run only once, `timeout` for time-based
            expiration, `config_changed`for changes in a "configuration" string or dictionary, and more...
            See https://pydoit.org/dependencies.html#uptodate
        :param targets: an optional list of strings or instances of any pathlib Path class indicating the files created
            by the task. They can be any file path (a file or folder). If a target does not exist the task will be
            executed. Two different tasks *can not* have the same target. See https://pydoit.org/tasks.html#targets
        :param setup: tasks to be run before this task but only when it is run.
            See https://pydoit.org/dependencies.html#setup-task
        :param teardown: actions to run once all tasks are completed.
            See https://pydoit.org/dependencies.html#setup-task
        :param getargs: an optional dictionary where the key is the argument name used on actions, and the value is a
            tuple with 2 strings: task name, "value name". getargs provides a way to use values computed from one task
            in another task. See https://pydoit.org/dependencies.html#getargs
        :param calc_dep: See https://pydoit.org/dependencies.html#calculated-dependencies
        :param verbosity: an optional custom verbosity level (0, 1, or 2) for this task.
            See https://pydoit.org/tasks.html#verbosity
        """
        # base
        super(task, self).__init__(name=name, doc=doc, title=title)

        # this will be non-None if @task is used as a decorator without arguments
        self.func = _func

        # validate all actions
        for _actions in (pre_actions, actions, post_actions):
            if _actions is None:
                continue
            if not isinstance(_actions, list):
                raise TypeError("Should be a list")
            for a in _actions:
                validate_action(a)
        self.pre_actions = pre_actions
        self.actions = actions
        self.post_actions = post_actions
        self.tell_why_am_i_running = tell_why_am_i_running

        # store other attributes
        self.file_dep = file_dep
        self.task_dep = task_dep
        self.uptodate = uptodate
        self.targets = targets

        # advanced ones
        self.setup = setup
        self.teardown = teardown
        self.getargs = getargs
        self.calc_dep = calc_dep
        self.verbosity = verbosity

        # late-rename and remove argument so that doit works ok
        def _create():
            return self._create_doit_tasks()
        self.create_doit_tasks = _create

    def __call__(self, func):
        self.func = func  # When instantiated with kwargs & used as a decorator
        return self

    def _create_doit_tasks(self, is_subtask=False):
        """Called by doit to know this task's definition, or by `@taskgen`"""

        task_dict = self.get_base_desc(is_subtask=is_subtask)

        # actions
        actions = []
        if self.tell_why_am_i_running:
            actions.append(why_am_i_running)
        if self.pre_actions is not None:
            actions += self.pre_actions
        if self.actions is not None:
            if self.func:
                raise ValueError("You can not specify `actions` when using @task to decorate a python function. Use "
                                 "`pre_actions` or `post_actions` instead")
            actions += self.actions
        elif self.func:
            actions += [self.func]
        if self.post_actions is not None:
            actions += self.post_actions
        assert len(actions) > 0, "No actions defined in the task"
        task_dict.update(actions=actions)

        # task dep, setup, calc dep: support direct link
        if self.task_dep is not None:
            task_dict.update(task_dep=replace_task_names(self.task_dep))
        if self.setup is not None:
            task_dict.update(setup=replace_task_names(self.setup))
        if self.calc_dep is not None:
            task_dict.update(calc_dep=replace_task_names(self.calc_dep))

        # others: simply use if not none
        if self.file_dep is not None:
            task_dict.update(file_dep=self.file_dep)
        if self.uptodate is not None:
            task_dict.update(uptodate=self.uptodate)
        if self.targets is not None:
            task_dict.update(targets=self.targets)
        if self.teardown is not None:
            task_dict.update(teardown=self.teardown)
        if self.getargs is not None:
            task_dict.update(getargs=self.getargs)
        if self.verbosity is not None:
            task_dict.update(verbosity=self.verbosity)

        return task_dict


class taskgen(taskbase):
    """
    A decorator to create a doit task generator (See https://pydoit.org/tasks.html#sub-tasks).

    Similar to `@task`, you can use it without arguments and it will capture the name and docstring of the decorated
    function. This function needs to be a generator, meaning that it should `yield` tasks. Such tasks can be plain old
    dictionaries as in `doit`, or can be created with `task`.

    For example this is a task group named `mygroup` with two tasks `mygroup:echo0` and `mygroup:echo1`

    ```python
    from doit_api import taskgen, task

    @taskgen
    def mygroup():
        ''' hey!!! '''
        for i in range(2):
            yield task(name="echo%s" % i, actions=["echo hi > hoho%s.txt" % i], targets=["hoho%s.txt" % i])
    ```

    And this is one with two python subtasks:

    ```python
    from doit_api import taskgen, task

    @taskgen
    def mygroup():
        ''' hey!!! '''
        for i in range(2):
            @task(name="subtask %i" % i,
                  doc="a subtask %s" % i,
                  title="this is %s running" % i)
            def c_():
                print("hello sub")
            yield c_
    ```

    `@taskgen` only accepts three optional arguments: `name` (that will be used for the base group name), doc, and
    title.

    """
    def __init__(self,
                 _func=None,
                 # *,  (support for python 2: no kw only args)
                 # -- task information
                 name=None,  # type: str
                 doc=None,   # type: str
                 # -- what the task is doing when run
                 title=None  # type: Union[str, Callable]
                 ):
        """

        :param name: an alternate base name for the task group. By default the name of the decorated function is used.
            See https://pydoit.org/tasks.html#sub-tasks
        :param doc: an optional documentation string for the task group. By default the decorated
            function docstring will be used. See https://pydoit.org/tasks.html#doc
        :param title: an optional message string or callable generating a message, to print when this task group is run.
            If nothing is provided, by default the task name is printed. If a string is provided, the task name will
            automatically be printed before it. If a callable is provided it should receive a single `task` argument
            and return a string. See https://pydoit.org/tasks.html#title
        """
        # base
        super(taskgen, self).__init__(name=name, doc=doc, title=title)

        # this will be non-None if @taskgen is used as a decorator without arguments
        self.func = _func

        # late-rename so that doit doesn't try to call the unbound method.
        self.create_doit_tasks = self._create_doit_tasks

    def __call__(self, func):
        self.func = func  # When instantiated with kwargs & used as a decorator
        return self

    def _create_doit_tasks(self):
        """Called by doit to know this task's definition"""

        # validate decorated function - a generator
        if self.func is None:
            raise TypeError("No task generator function is provided")
        if not isgeneratorfunction(self.func):
            raise TypeError("The decorated function should be a generator")

        # Protect against empty subtasks by yielding a first def with name None, see https://pydoit.org/tasks.html#sub-tasks
        yield self.get_base_desc(name=None)

        for f in self.func():
            if isinstance(f, dict):
                yield f
            else:
                yield f._create_doit_tasks(is_subtask=True)


# class TaskBase(object):
#     todo we could wish to provide the same level of functionality than this letsdoit class, but with fields listed.
#     """Subclass this to define tasks."""
#     @classmethod
#     def create_doit_tasks(cls):
#         if cls is TaskBase:
#             return  # avoid create tasks from base class 'Task'
#         instance = cls()
#         kw = dict((a, getattr(instance, a)) \
#                     for a in dir(instance) if not a.startswith('_'))
#
#         kw.pop('create_doit_tasks')
#         if 'actions' not in kw:
#             kw['actions'] = [kw.pop('run')]
#         if 'doc' not in kw and (cls.__doc__ != TaskBase.__doc__):
#             kw['doc'] = cls.__doc__
#         return kw
