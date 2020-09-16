# API reference

In general, using `help(symbol)` is the recommended way to get the latest documentation. In addition, this page provides an overview of the various elements in this package.

### `doit_config`

Generates a valid DOIT_CONFIG dictionary, that can contain GLOBAL options. You can use it at the beginning of your `dodo.py` file:

```python
from doit_api import doit_config

DOIT_CONFIG = doit_config(verbosity=2)
```

Almost all `doit` command line options can be changed here. See https://pydoit.org/configuration.html#configuration-at-dodo-py

```python
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
```

**Parameters**

 - `default_tasks`: The list of tasks to run when no task names are specified in the commandline. By default all tasks are run. See https://pydoit.org/tasks.html#task-selection
 
 - `single`: set this to true to execute only specified tasks ignoring their task_dep. Default: `False`
 
 - `continue_`: by default the execution of tasks is halted on the first task failure or error. You can force it to continue execution by setting this to True. See https://pydoit.org/cmd_run.html#continue

 - `always`: set this to True to always execute tasks even if up-to-date (default: False)

 - `cleanforget`: a boolean, set this to true (default: False) if you like to also make doit forget previous execution of cleaned tasks. See https://pydoit.org/cmd_other.html#clean
 
 - `cleandep`: By default if a task contains task-dependencies those are not automatically cleaned too. Set this flag to True to do it. Note that if you execute the default tasks, this is set to True by default. See https://pydoit.org/cmd_other.html#clean

 - `dryrun`: a boolean (default False), telling doit to print actions without really executing them. See https://pydoit.org/cmd_other.html#dry-run

 - `db_file`: an alias for dep_file
 
 - `dep_file`: sets the name of the file to save the "DB", default is .doit.db. Note that DBM backends might save more than one file, in this case the specified name is used as a base name. See https://pydoit.org/cmd_run.html#db-file

 - `backend`: The backend used by pydoit to store the execution states and results. A string that can be any of 'dbm' (default), 'json' (slow but good for debugging), 'sqlite3' (supports concurrent access). Other choices may be available if you install doit plugins adding backends (e.g. redit...). See https://pydoit.org/cmd_run.html#db-backend

 - `verbosity`: An integer defining the verbosity level. Default is 1. See https://pydoit.org/tasks.html#verbosity
        
     - 0 capture (do not print) stdout/stderr from task,
     - 1 capture stdout only,
     - 2 do not capture anything (print everything immediately).
    
 - `failure_verbosity`: Option to control if stdout/stderr should be re-displayed in the end of of report. This is useful when used in conjunction with the `continue` option. Default: 0. See https://pydoit.org/cmd_run.html#failure-verbosity
 
   - 0 do not show re-display
   - 1 re-display stderr only
   - 2 re-display both stderr/stdout
        
 - `outfile`: output file where to write the results to. Default is stdout. See https://pydoit.org/cmd_run.html#output-file
 
 - `reporter`: choice of reporter for the console. Can be a string indicating a reporter included in doit, or a class. See https://pydoit.org/cmd_run.html#reporter and https://pydoit.org/cmd_run.html#custom-reporter. Supported string values are 
 
   - 'console' (default), 
   - 'executed-only' (Produces zero output if no task is executed),
   - 'json' (Output results in JSON format)
   - 'zero' (display only error messages (does not display info on tasks being executed/skipped). This is used when you only want to see the output generated by the tasks execution.)

 - `dir`: By default the directory of the dodo file is used as the "current working directory" on python execution. You can specify a different cwd with this argument. See https://pydoit.org/cmd_run.html#dir-cwd
        
 - `num_process`: the number of parallel execution processes to use. Default 1. See https://pydoit.org/cmd_run.html#parallel-execution
        
 - `parallel_type`: the type of parallelism mechanism used when process is set to a number larger than 1. A string one of 'thread' (uses threads) and 'process' (uses python multiprocessing module, default).
        
 - `check_file_uptodate`: a string indicating how to check if files have been modified. See https://pydoit.org/cmd_run.html#check-file-uptodate
 
   - 'md5': use the md5sum (default)
   - 'timestamp': use the timestamp. 
 
 - `pdb`: set this to True to get into PDB (python debugger) post-mortem in case of unhandled exception. Default: False. See https://pydoit.org/cmd_run.html#pdb
 
 - `codec_cls`: a class used to serialize and deserialize values returned by python-actions. Default `JSONCodec`. See https://pydoit.org/cmd_run.html#codec-cls
 
 - `minversion`: an optional string or a 3-element tuple with integer values indicating the minimum/oldest doit version that can be used with a dodo.py file. If specified as a string any part that is not a number i.e.(dev0, a2, b4) will be converted to -1. See https://pydoit.org/cmd_run.html#minversion
 
 - `auto_delayed_regex`: set this to True (default False) to use the default regex ".*" for every delayed task loader for which no regex was explicitly defined. See https://pydoit.org/cmd_run.html#automatic-regex-for-delayed-task-loaders
 
 - `action_string_formatting`: Defines the templating style used by your cmd action strings for automatic variable substitution. It is a string that can be 'old' (default), 'new', or 'both'. See https://pydoit.org/tasks.html#keywords-on-cmd-action-string

**Outputs**

`config_dict`: a configuration dictionary that you can use as the DOIT_CONFIG variable in your dodo.py file

### `task`

Creates a doit task.

```python
from doit_api import task

echoer = task(name="echoer", actions=["echo hi"], doc="the doc for echoer")
```

It signature regroups all options that you usually can set on a `doit` task, with sensible defaults. 

A minimal `doit` task consists of one or several actions. You must provide at least one action in `actions`. If `tell_why_i_am_runnin=True` (default) an additional action will be prepended to print the reason why the task is running if the task declared a `file_dep`, `task_dep`, `uptodate` or `targets`.

All other parameters match those in `doit` conventions (See parameters below), except

 - `name` that is an intelligent placeholder for `basename` (if a task is a simple task) or `name` (if the task is a subtask in a `@taskgen` generator),
 - `title` that adds support for plain strings and by default is `title_with_actions`,
 - `task_dep`, `setup` and `calc_dep` where if a task callable (decorated with `@pytask` or not) is provided, the corresponding name will be used.

Note: the `watch` parameter (Linux and Mac only) is not yet supported.
See [doit doc](https://pydoit.org/cmd_other.html?highlight=watch#auto-watch

```python
def task(
     # -- task information + what the task is doing when run
     name,                        # type: str
     actions,                     # type: List[DoitAction]
     doc=None,                    # type: str
     title=title_with_actions,    # type: Union[str, Callable]
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
)
```

**Parameters:**

 * `name`: a mandatory name for the task. Note that this parameter will intelligently set 'basename' for normal tasks or 'name' for subtasks in a task generator (`@taskgen`). See [doit doc](https://pydoit.org/tasks.html#task-name)
 
 * `actions`: a mandatory list of actions that this task should execute. There are 2 basic kinds of actions: cmd-action and python-action. See [doit doc](https://pydoit.org/tasks.html#actions)
 
 * `doc`: an optional documentation string for the task. See [doit doc](https://pydoit.org/tasks.html#doc)
 
 * `title`: an optional message string or callable generating a message, to print when the task is run. If nothing is provided, by default the task name is printed. If a string is provided, the task name will automatically be printed before it. If a callable is provided it should receive a single `task` argument and return a string. See [doit doc](https://pydoit.org/tasks.html#title)
 
 * `tell_why_am_i_running`: if True (default), an additional `why_am_i_running` action is prepended to the list of actions
 
 * `file_dep`: an optional list of strings or instances of any pathlib Path class indicating the files required for this task to run. When none of these files are modified, the task will be skipped if already run. See [doit doc](https://pydoit.org/tasks.html#file-dep-file-dependency)
 
 * `task_dep`: an optional list of tasks (names or callables) that should be run *before* this task. Note that this is also a convenient way to create a group of tasks. See [doit doc](https://pydoit.org/dependencies.html#task-dependency)
 
 * `uptodate`: an optional list where each element can be True (up to date), False (not up to date), None (ignored), a callable or a command(string). Many pre-baked callables from `doit.tools` can be used: `result_dep` to depend on the result of another task, `run_once` to run only once, `timeout` for time-based expiration, `config_changed` for changes in a “configuration” string or dictionary, and more... See [doit doc](https://pydoit.org/dependencies.html#uptodate)
 
 * `targets`: an optional list of strings or instances of any pathlib Path class indicating the files created by the task. They can be any file path (a file or folder). If a target does not exist the task will be executed. Two different tasks *can not* have the same target. See [doit doc](https://pydoit.org/tasks.html#targets)
 
 * `setup`: tasks to be run before this task but only when it is run. See [doit doc](https://pydoit.org/dependencies.html#setup-task)
 
 * `teardown`: actions to run once all tasks are completed. See [doit doc](https://pydoit.org/dependencies.html#setup-task)
 
 * `getargs`: an optional dictionary where the key is the argument name used on actions, and the value is a tuple with 2 strings: task name, “value name”. getargs provides a way to use values computed from one task in another task. See [doit doc](https://pydoit.org/dependencies.html#getargs)
 
 * `calc_dep`: See [doit doc](https://pydoit.org/dependencies.html#calculated-dependencies)
 
 * `verbosity`: an optional custom verbosity level (0, 1, or 2) for this task. See [doit doc](https://pydoit.org/tasks.html#verbosity)

Note: this relies on the `create_doit_tasks` hook, see [here](https://pydoit.org/task_creation.html#custom-task-definition)

### `@pytask`

A decorator to create a task containing a python action (the decorated function), and optional additional actions.

```python
from doit_api import pytask

@pytask
def a():
    """ the doc for a """
    print("hi")

@pytask(targets=..., file_deps=..., ...)
def b():
    print("hi")
```

A minimal `doit` task consists of one or several actions. Here, the main action is a call to the decorated function. You can specify actions to be done before and after that/these `actions` in `pre_actions` and `post_actions`.

If `tell_why_i_am_runnin=True` (default) an additional action will be prepended to print the reason why the task is running if the task declared a `file_dep`, `task_dep`, `uptodate` or `targets`.

All other parameters match those in `doit` conventions (See parameters below), except

 - `name` that is an intelligent placeholder for `basename` (if a task is a simple task) or `name` (if the task is a subtask in a `@taskgen` generator),
 - `title` that adds support for plain strings and by default is `title_with_actions`,
 - `task_dep`, `setup` and `calc_dep` where if a task callable (decorated with `@pytask` or not) is provided, the corresponding name will be used.

Note: the `watch` parameter (Linux and Mac only) is not yet supported.
See [doit doc](https://pydoit.org/cmd_other.html?highlight=watch#auto-watch

```python
def pytask(
     # -- task information
     name=None,                   # type: str
     doc=None,                    # type: str
     # -- what the task is doing when run
     title=title_with_actions,    # type: Union[str, Callable]
     pre_actions=None,            # type: List[DoitAction]
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
)
```

**Parameters:**

 * `name`: an alternate name for the task. By default the name of the decorated function is used. Note that this parameter will intelligently set 'basename' for normal tasks or 'name' for subtasks in a task generator (`@taskgen`). See [doit doc](https://pydoit.org/tasks.html#task-name)
 
 * `doc`: an optional documentation string for the task. By default, the decorated function docstring will be used. See [doit doc](https://pydoit.org/tasks.html#doc)
 
 * `title`: an optional message string or callable generating a message, to print when the task is run. If nothing is provided, by default the task name is printed. If a string is provided, the task name will automatically be printed before it. If a callable is provided it should receive a single `task` argument and return a string. See [doit doc](https://pydoit.org/tasks.html#title)

 * `pre_actions`: an optional list of actions to be executed before the main action(s). There are 2 basic kinds of actions: cmd-action and python-action. See [doit doc](https://pydoit.org/tasks.html#actions)
 
 * `post_actions`: an optional list of actions to be executed after the main action(s). There are 2 basic kinds of actions: cmd-action and python-action. See [doit doc](https://pydoit.org/tasks.html#actions)
 
 * `tell_why_am_i_running`: if True (default), an additional `why_am_i_running` action is prepended to the list of actions
 
 * `file_dep`: an optional list of strings or instances of any pathlib Path class indicating the files required for this task to run. When none of these files are modified, the task will be skipped if already run. See [doit doc](https://pydoit.org/tasks.html#file-dep-file-dependency)
 
 * `task_dep`: an optional list of tasks (names or callables) that should be run *before* this task. Note that this is also a convenient way to create a group of tasks. See [doit doc](https://pydoit.org/dependencies.html#task-dependency)
 
 * `uptodate`: an optional list where each element can be True (up to date), False (not up to date), None (ignored), a callable or a command(string). Many pre-baked callables from `doit.tools` can be used: `result_dep` to depend on the result of another task, `run_once` to run only once, `timeout` for time-based expiration, `config_changed` for changes in a “configuration” string or dictionary, and more... See [doit doc](https://pydoit.org/dependencies.html#uptodate)
 
 * `targets`: an optional list of strings or instances of any pathlib Path class indicating the files created by the task. They can be any file path (a file or folder). If a target does not exist the task will be executed. Two different tasks *can not* have the same target. See [doit doc](https://pydoit.org/tasks.html#targets)
 
 * `setup`: tasks to be run before this task but only when it is run. See [doit doc](https://pydoit.org/dependencies.html#setup-task)
 
 * `teardown`: actions to run once all tasks are completed. See [doit doc](https://pydoit.org/dependencies.html#setup-task)
 
 * `getargs`: an optional dictionary where the key is the argument name used on actions, and the value is a tuple with 2 strings: task name, “value name”. getargs provides a way to use values computed from one task in another task. See [doit doc](https://pydoit.org/dependencies.html#getargs)
 
 * `calc_dep`: See [doit doc](https://pydoit.org/dependencies.html#calculated-dependencies)
 
 * `verbosity`: an optional custom verbosity level (0, 1, or 2) for this task. See [doit doc](https://pydoit.org/tasks.html#verbosity)

Note: this relies on the `create_doit_tasks` hook, see [here](https://pydoit.org/task_creation.html#custom-task-definition)


### `@taskgen`

A decorator to create a task generator (See [doit subtasks](https://pydoit.org/tasks.html#sub-tasks)).

Similar to `@task`, you can use it without arguments and it will capture the name and docstring of the decorated function. This function needs to be a generator, meaning that it should `yield` tasks. Such tasks can be plain old dictionaries as in `doit`, or can be created with `task`.

For example this is a task group named `mygroup` with two tasks `mygroup:echo0` and `mygroup:echo1`

```python
from doit_api import taskgen, task

@taskgen
def mygroup():
    """ hey !!! """
    for i in range(2):
        yield task(name="echo%s" % i, 
                   actions=["echo hi > hoho%s.txt" % i], 
                   targets=["hoho%s.txt" % i])
```

And this is one with two python subtasks:

```python
from doit_api import taskgen, task

@taskgen
def mygroup():
    """ hey !!! """
    for i in range(2):
        @task(name="subtask %i" % i,
              doc="a subtask %s" % i,
              title="this is %s running" % i)
        def c_():
            print("hello sub")
        yield c_
```

`@taskgen` only accepts three optional arguments: `name` (that will be used for the base group name), `doc`, and `title`.

**Parameters:**

 * `name`: an alternate base name for the task group. By default the name of the decorated function is used. See [doit doc](https://pydoit.org/tasks.html#sub-tasks)
 
 * `doc`: an optional documentation string for the task group. By default the decorated function docstring will be used. See [doit doc](https://pydoit.org/tasks.html#doc)
 
 * `title`: an optional message string or callable generating a message, to print when this task group is run. If nothing is provided, by default the task name is printed. If a string is provided, the task name will automatically be printed before it. If a callable is provided it should receive a single `task` argument and return a string. See [doit doc](https://pydoit.org/tasks.html#title)


### `why_am_i_running`

Goodie: a python action that you can use in any `doit` task, to print the reason why the task is running if the task declared a `file_dep`, `task_dep`, `uptodate` or `targets`. Useful for debugging. See [this doit conversation](https://github.com/pydoit/doit/issues/277).

### `title_with_actions`

Goodie: an automatic title for doit tasks. Same than [`doit.title_with_actions`](https://pydoit.org/tools.html#title-with-actions-title) but removes [`why_am_i_running`](#why_am_i_running) actions if any is present.
