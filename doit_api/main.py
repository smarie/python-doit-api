import sys

from inspect import isgeneratorfunction
from os.path import exists

try:
    from typing import Callable, Union, List, Tuple, Dict, Optional, Type, Any
    from pathlib import Path

    DoitAction = Union[str, List, Callable, Tuple[Callable, Tuple, Dict]]
    DoitTask = Union[str, Callable, 'task', 'taskgen']
    DoitPath = Union[str, Path]
except ImportError:
    pass

from doit.action import CmdAction


# --- configuration
def doit_config(
                # execution related
                default_tasks=None,             # type: List[str]
                single=None,                    # type: bool
                continue_=None,                 # type: bool
                always=None,                    # type: bool
                cleanforget=None,               # type: bool
                cleandep=None,                  # type: bool
                dryrun=None,                    # type: bool
                # database
                db_file=None,                   # type: Union[str, Path]
                dep_file=None,                  # type: Union[str, Path]
                backend=None,                   # type: str
                # verbosities
                verbosity=None,                 # type: int
                failure_verbosity=None,         # type: int
                # output and working dir
                outfile=None,                   # type: Union[str, Path]
                reporter=None,                  # type: Union[str, Type]
                dir=None,                       # type: Union[str, Path]
                # parallel processing
                num_process=None,               # type: int
                parallel_type=None,             # type: str
                # misc
                check_file_uptodate=None,       # type: str
                pdb=None,                       # type: bool
                codec_cls=None,                 # type: Type
                minversion=None,                # type: Union[str, Tuple[int, int, int]]
                auto_delayed_regex=None,        # type: bool
                action_string_formatting=None,  # type: str
                ):
    """
    Generates a valid DOIT_CONFIG dictionary, that can contain GLOBAL options. You can use it at the beginning of your
    `dodo.py` file:

    ```python
    from doit_api import doit_config

    DOIT_CONFIG = doit_config(verbosity=2)
    ```

    Almost all command line options can be changed here.
    See https://pydoit.org/configuration.html#configuration-at-dodo-py

    :param default_tasks: The list of tasks to run when no task names are specified in the commandline. By default
        all tasks are run. See https://pydoit.org/tasks.html#task-selection
    :param single: set this to true to execute only specified tasks ignoring their task_dep. Default: False
    :param continue_: by default the execution of tasks is halted on the first task failure or error. You can force it
        to continue execution by setting this to True. See https://pydoit.org/cmd_run.html#continue
    :param always: set this to True to always execute tasks even if up-to-date (default: False)
    :param cleanforget: a boolean, set this to true (default: False) if you like to also make doit forget previous
        execution of cleaned tasks. See https://pydoit.org/cmd_other.html#clean
    :param cleandep: By default if a task contains task-dependencies those are not automatically cleaned too. Set this
        flag to True to do it. Note that if you execute the default tasks, this is set to True by default.
        See https://pydoit.org/cmd_other.html#clean
    :param dryrun: a boolean (default False), telling doit to print actions without really executing them.
        See https://pydoit.org/cmd_other.html#dry-run
    :param db_file: an alias for dep_file
    :param dep_file: sets the name of the file to save the "DB", default is .doit.db. Note that DBM backends might save
        more than one file, in this case the specified name is used as a base name.
        See https://pydoit.org/cmd_run.html#db-file
    :param backend: The backend used by pydoit to store the execution states and results. A string that can be any of
        'dbm' (default), 'json' (slow but good for debugging), 'sqlite3' (supports concurrent access).
        Other choices may be available if you install doit plugins adding backends (e.g. redit...).
        See https://pydoit.org/cmd_run.html#db-backend
    :param verbosity: An integer defining the verbosity level:
        0 capture (do not print) stdout/stderr from task,
        1 capture stdout only,
        2 do not capture anything (print everything immediately).
        Default is 1. See https://pydoit.org/tasks.html#verbosity
    :param failure_verbosity: Option to control if stdout/stderr should be re-displayed in the end of of report. This
        is useful when used in conjunction with the `continue` option. Default: 0
        0 do not show re-display
        1 re-display stderr only
        2 re-display both stderr/stdout
        See https://pydoit.org/cmd_run.html#failure-verbosity
    :param outfile: output file where to write the results to. Default is stdout.
        See https://pydoit.org/cmd_run.html#output-file
    :param reporter: choice of reporter for the console. Can be a string indicating a reporter included in doit, or
        a class. Supported string values are
        'console' (default),
        'executed-only' (Produces zero output if no task is executed),
        'json' (Output results in JSON format)
        'zero' (display only error messages (does not display info on tasks being executed/skipped). This is used when
        you only want to see the output generated by the tasks execution.)
        see https://pydoit.org/cmd_run.html#reporter and https://pydoit.org/cmd_run.html#custom-reporter
    :param dir: By default the directory of the dodo file is used as the "current working directory" on python
        execution. You can specify a different cwd with this argument. See https://pydoit.org/cmd_run.html#dir-cwd
    :param num_process: the number of parallel execution processes to use. Default 1. See
        https://pydoit.org/cmd_run.html#parallel-execution
    :param parallel_type: the type of parallelism mechanism used when process is set to a number larger than 1. A string
        one of 'thread' (uses threads) and 'process' (uses python multiprocessing module, default).
    :param check_file_uptodate: a string indicating how to check if files have been modified. 'md5': use the md5sum
        (default) 'timestamp': use the timestamp. See https://pydoit.org/cmd_run.html#check-file-uptodate
    :param pdb: set this to True to get into PDB (python debugger) post-mortem in case of unhandled exception.
        Default: False. See https://pydoit.org/cmd_run.html#pdb
    :param codec_cls: a class used to serialize and deserialize values returned by python-actions. Default `JSONCodec`.
        See https://pydoit.org/cmd_run.html#codec-cls
    :param minversion: an optional string or a 3-element tuple with integer values indicating the minimum/oldest doit
        version that can be used with a dodo.py file. If specified as a string any part that is not
        a number i.e.(dev0, a2, b4) will be converted to -1. See https://pydoit.org/cmd_run.html#minversion
    :param auto_delayed_regex: set this to True (default False) to use the default regex ".*" for every delayed task
        loader for which no regex was explicitly defined.
        See https://pydoit.org/cmd_run.html#automatic-regex-for-delayed-task-loaders
    :param action_string_formatting: Defines the templating style used by your cmd action strings for automatic variable
        substitution. It is a string that can be 'old' (default), 'new', or 'both'.
        See https://pydoit.org/tasks.html#keywords-on-cmd-action-string
    :return: a configuration dictionary that you can use as the DOIT_CONFIG variable in your dodo.py file
    """
    config_dict = dict()

    # execution related
    if default_tasks is not None:
        # note: yes, not a dash here but an underscore
        config_dict.update(default_tasks=default_tasks)
    if single is not None:
        config_dict.update(single=single)
    if continue_ is not None:
        config_dict['continue'] = continue_
    if always is not None:
        config_dict.update(always=always)
    if cleanforget is not None:
        config_dict.update(cleanforget=cleanforget)
    if cleandep is not None:
        config_dict.update(cleandep=cleandep)
    if dryrun is not None:
        config_dict.update(dryrun=dryrun)

    # database
    if db_file is not None:
        assert dep_file is None, "db_file and dep_file are equivalent, you should not specify both"
        dep_file = db_file
    if dep_file is not None:
        # note: yes, not a dash here but an underscore
        config_dict.update(dep_file=dep_file)
    if backend is not None:
        config_dict.update(backend=backend)

    # verbosities
    if verbosity is not None:
        config_dict.update(verbosity=verbosity)
    if failure_verbosity is not None:
        # confirmed
        config_dict.update(failure_verbosity=failure_verbosity)

    # output, reporter and working dir
    if outfile is not None:
        # yes, short name
        config_dict.update(outfile=outfile)
    if reporter is not None:
        config_dict.update(reporter=reporter)
    if dir is not None:
        config_dict.update(dir=dir)

    # parallel processing
    if num_process is not None:
        config_dict.update(num_process=num_process)
    if parallel_type is not None:
        config_dict.update(par_type=parallel_type)

    # misc
    if check_file_uptodate is not None:
        config_dict.update(check_file_uptodate=check_file_uptodate)
    if pdb is not None:
        config_dict.update(pdb=pdb)
    if codec_cls is not None:
        config_dict.update(codec_cls=codec_cls)
    if minversion is not None:
        config_dict.update(minversion=minversion)
    if auto_delayed_regex is not None:
        config_dict.update(auto_delayed_regex=auto_delayed_regex)
    if action_string_formatting is not None:
        config_dict.update(action_string_formatting=action_string_formatting)

    return config_dict


# --- task utilities


def why_am_i_running(task, changed):
    """
    Goodie: a python action that you can use in any `doit` task, to print the reason why the task is running if the
    task declared a `file_dep`, `task_dep`, `uptodate` or `targets`. Useful for debugging.
    See [this doit conversation](https://github.com/pydoit/doit/issues/277).
    """
    for t in task.targets:
        if not exists(t):
            print("Running %s because one of its targets does not exist: %r" % (task, t))
            return

    if changed is None or len(changed) == 0:
        if len(task.targets) > 0:
            print("Running %s because even though it declares at least a target, it does not have"
                  " explicit `uptodate=True`." % task)
        else:
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
        self.name = name
        self.doc = doc
        self.title=title
        self.actions = None

    def add_default_desc_from_fun(self, func):
        """
        Uses the information from `func` to fill the blanks in name and doc
        :param func:
        :return:
        """
        if self.name is None:
            self.name = func.__name__
        if self.doc is None:
            self.doc = func.__doc__

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
    Creates a doit task.

    ```python
    from doit_api import task

    echoer = task(name="echoer", actions=["echo hi"], doc="the doc for echoer")
    ```

    It signature regroups all options that you usually can set on a `doit` task, with sensible defaults. See constructor
    for details.

    Note: this relies on the `create_doit_tasks` hook, see https://pydoit.org/task_creation.html#custom-task-definition
    """

    def __init__(self,
                 # *,  (support for python 2: no kw only args)
                 # -- task information + what the task is doing when run
                 name,                        # type: str
                 actions,                     # type: List[DoitAction]
                 doc=None,                    # type: str
                 title=title_with_actions,    # type: Union[str, Callable]
                 tell_why_am_i_running=True,  # type: bool
                 # -- preventing useless runs and selecting order
                 targets=None,                # type: List[DoitPath]
                 clean=None,                  # type: Union[bool, List[DoitAction]]
                 file_dep=None,               # type: List[DoitPath]
                 task_dep=None,               # type: List[DoitTask]
                 uptodate=None,               # type: List[Optional[Union[bool, Callable, str]]]
                 # -- advanced
                 setup=None,                  # type: List[DoitTask]
                 teardown=None,               # type: List[DoitAction]
                 getargs=None,                # type: Dict[str, Tuple[str, str]]
                 calc_dep=None,               # type: List[DoitTask]
                 # -- misc
                 verbosity=None,              # type: int
                 ):
        """
        A minimal `doit` task consists of one or several actions. You must provide at least one action in `actions`.
        If `tell_why_i_am_running=True` (default) an additional action will be prepended to print the reason why the
        task is running if the task declared a `file_dep`, `task_dep`, `uptodate` or `targets`.

        All other parameters match those in `doit` conventions (See docstrings below), except

         - `name` that is an intelligent placeholder for `basename` (if a task is a simple task) or `name` (if the task
           is a subtask in a `@taskgen` generator),
         - `title` that adds support for plain strings and by default is `title_with_actions`
         - `task_dep`, `setup` and `calc_dep` where if a task callable (decorated with `@task` or not) is provided, the
           corresponding name will be used.

        Note: the `watch` parameter (Linux and Mac only) is not yet supported.
        See https://pydoit.org/cmd_other.html?highlight=watch#auto-watch

        :param name: a mandatory name for the task. Note that this parameter will intelligently set 'basename' for
            normal tasks or 'name' for subtasks in a task generator (`@taskgen`).
            See https://pydoit.org/tasks.html#task-name
        :param actions: a mandatory list of actions that this task should execute. There are 2 basic kinds of actions:
            cmd-action and python-action. See https://pydoit.org/tasks.html#actions
        :param doc: an optional documentation string for the task. See https://pydoit.org/tasks.html#doc
        :param title: an optional message string or callable generating a message, to print when the task is run. If
            nothing is provided, by default the task name is printed. If a string is provided, the task name will
            automatically be printed before it. If a callable is provided it should receive a single `task` argument
            and return a string. See https://pydoit.org/tasks.html#title
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
        :param clean: an optional boolean or list of tasks indicating if the task should perform some cleaning when
            `doit clean` is executed. `True` means "delete all targets". If there is a folder as a target it will be
            removed if the folder is empty, otherwise it will display a warning message. If you want to clean the
            targets and add some custom clean actions, you can include the doit.task.clean_targets
            See https://pydoit.org/cmd_other.html#clean
        :param setup: tasks to be run before this task but only when it is run.
            See https://pydoit.org/dependencies.html#setup-task
        :param teardown: actions to run once all tasks are completed.
            See https://pydoit.org/dependencies.html#setup-task
        :param getargs: an optional dictionary where the key is the argument name used on actions, and the value is a
            tuple with 2 strings: task name, "value name". getargs provides a way to use values computed from one task
            in another task. See https://pydoit.org/dependencies.html#getargs
        :param calc_dep: See https://pydoit.org/dependencies.html#calculated-dependencies
        :param verbosity: an optional custom verbosity level (0, 1, or 2) for this task:
            0 capture (do not print) stdout/stderr from task,
            1 capture stdout only,
            2 do not capture anything (print everything immediately).
            Default is 1. See https://pydoit.org/tasks.html#verbosity
        """
        # base
        super(task, self).__init__(name=name, doc=doc, title=title)

        # validate all actions
        if actions is None or not isinstance(actions, list):
            raise TypeError("actions should be a list, found: %r" % actions)
        # for a in actions:
        #     validate_action(a)
        self.actions = actions
        self.tell_why_am_i_running = tell_why_am_i_running

        # store other attributes
        self.file_dep = file_dep
        self.task_dep = task_dep
        self.uptodate = uptodate
        self.targets = targets
        self.clean = clean

        # advanced ones
        self.setup = setup
        self.teardown = teardown
        self.getargs = getargs
        self.calc_dep = calc_dep
        self.verbosity = verbosity

        # finally attach the `create_doit_tasks` hook if needed
        self.create_doit_tasks = self._create_doit_tasks_noargs

    def _create_doit_tasks_noargs(self):
        return self._create_doit_tasks()

    def _create_doit_tasks(self, is_subtask=False):
        """Called by doit to know this task's definition, or by `@taskgen`"""

        # first get the base description
        task_dict = self.get_base_desc(is_subtask=is_subtask)

        # actions
        if self.tell_why_am_i_running:
            actions = [why_am_i_running] + self.actions
        else:
            actions = self.actions
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
        if self.clean is not None:
            task_dict.update(clean=self.clean)
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
        self.add_default_desc_from_fun(self.func)
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


def pytask(
           # -- task information
           name=None,                   # type: Union[str, Any]
           doc=None,                    # type: str
           # -- what the task is doing when run
           title=title_with_actions,    # type: Union[str, Callable]
           pre_actions=None,            # type: List[DoitAction]
           post_actions=None,           # type: List[DoitAction]
           tell_why_am_i_running=True,  # type: bool
           # -- preventing useless runs and selecting order
           targets=None,                # type: List[DoitPath]
           clean=None,                  # type: Union[bool, List[DoitAction]]
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
    A decorator to create a task containing a python action (the decorated function), and optional additional actions.

    ```python
    from doit_api import pytask

    @pytask
    def a():
        ''' the doc for a '''
        print("hi")

    @pytask(targets=..., file_deps=..., ...)
    def b():
        print("hi")
    ```

    A minimal `doit` task consists of one or several actions. Here, the main action is a call to the decorated function.
    You can specify actions to be done before and after that/these `actions` in `pre_actions` and `post_actions`.
    If `tell_why_i_am_running=True` (default) an additional action will be prepended to print the reason why the
    task is running if the task declared a `file_dep`, `task_dep`, `uptodate` or `targets`.

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
    :param doc: an optional documentation string for the task. By default, the decorated function docstring will
        be used. See https://pydoit.org/tasks.html#doc
    :param title: an optional message string or callable generating a message, to print when the task is run. If
        nothing is provided, by default the task name is printed. If a string is provided, the task name will
        automatically be printed before it. If a callable is provided it should receive a single `task` argument
        and return a string. See https://pydoit.org/tasks.html#title
    :param pre_actions: an optional list of actions to be executed before the main python action.
        There are 2 basic kinds of actions: cmd-action and python-action. See https://pydoit.org/tasks.html#actions
    :param post_actions: an optional list of actions to be executed after the main python action.
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
    :param clean: an optional boolean or list of tasks indicating if the task should perform some cleaning when
        `doit clean` is executed. `True` means "delete all targets". If there is a folder as a target it will be
        removed if the folder is empty, otherwise it will display a warning message. If you want to clean the
        targets and add some custom clean actions, you can include the doit.task.clean_targets
        See https://pydoit.org/cmd_other.html#clean
    :param setup: tasks to be run before this task but only when it is run.
        See https://pydoit.org/dependencies.html#setup-task
    :param teardown: actions to run once all tasks are completed.
        See https://pydoit.org/dependencies.html#setup-task
    :param getargs: an optional dictionary where the key is the argument name used on actions, and the value is a
        tuple with 2 strings: task name, "value name". getargs provides a way to use values computed from one task
        in another task. See https://pydoit.org/dependencies.html#getargs
    :param calc_dep: See https://pydoit.org/dependencies.html#calculated-dependencies
    :param verbosity: an optional custom verbosity level (0, 1, or 2) for this task:
        0 capture (do not print) stdout/stderr from task,
        1 capture stdout only,
        2 do not capture anything (print everything immediately).
        Default is 1. See https://pydoit.org/tasks.html#verbosity
    """
    # our decorator
    def _decorate(f  # type: Callable
                  ):

        # checks on the decorated function name
        if f.__name__.startswith("task_"):
            raise ValueError("You can not decorate a function named `task_xxx` with `@pytask` ; please remove the "
                             "`task_` prefix.")

        # create the actions: pre + [fun] + post
        actions = []
        for _actions in (pre_actions, [f], post_actions):
            if _actions is None:
                continue
            if not isinstance(_actions, list):
                raise TypeError("pre_actions and post_actions should be lists")
            # for a in _actions:
            #     validate_action(a)
            actions += _actions

        # create the task object
        f_task = task(name=name, doc=doc,
                      title=title, actions=actions,
                      tell_why_am_i_running=tell_why_am_i_running,
                      targets=targets, clean=clean, file_dep=file_dep, task_dep=task_dep, uptodate=uptodate,
                      setup=setup, teardown=teardown, getargs=getargs, calc_dep=calc_dep,
                      verbosity=verbosity)

        # declare the fun
        f_task.add_default_desc_from_fun(f)

        # move the hooks from f_task to f
        f.create_doit_tasks = f_task.create_doit_tasks
        del f_task.create_doit_tasks
        f._create_doit_tasks = f_task._create_doit_tasks

        return f

    if name is not None and callable(name):
        # used without arguments: we have to return a function, not a task ! otherwise pickle wont work
        f = name
        name = None  # important ! indeed it is used in _decorate
        return _decorate(f)
    else:
        # used with arguments: return a decorator
        return _decorate


# python 2 -specific hack to enable pickling task and taskgen objects
# without getting TypeError: can't pickle instancemethod objects
# see https://stackoverflow.com/a/25161919/7262247
if sys.version_info < (3, 0):
    import copy_reg
    import types

    def _pickle_method(m):
        if m.im_self is None:
            return getattr, (m.im_class, m.im_func.func_name)
        else:
            return getattr, (m.im_self, m.im_func.func_name)

    copy_reg.pickle(types.MethodType, _pickle_method)
