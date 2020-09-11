# API reference

In general, using `help(symbol)` is the recommended way to get the latest documentation. In addition, this page provides an overview of the various elements in this package.

### `@task` or `task`

Creates a doit task. It may be used as a decorator with or without parameter, or as a creator:

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

It signature regroups all options that you usually can set on a `doit` task, with sensible defaults.
A minimal `doit` task consists of one or several actions. When `@task` is used as a decorator, the main action is a call to the decorated function. Otherwise when `task` is used as a creator, you must provide at least one action in `actions`. You can specify actions to be done before and after that/these `actions` in `pre_actions` and `post_actions`. If `tell_why_i_am_runnin=True` (default) an additional action will be prepended to print the reason why the task is running if the task declared a `file_dep`, `task_dep`, `uptodate` or `targets`.

All other parameters match those in `doit` conventions (See parameters below), except

 - `name` that is an intelligent placeholder for `basename` (if a task is a simple task) or `name` (if the task is a subtask in a `@taskgen` generator),
 - `title` that adds support for plain strings and by default is `title_with_actions`,
 - `task_dep`, `setup` and `calc_dep` where if a task callable (decorated with `@task` or not) is provided, the corresponding name will be used.

Note: the `watch` parameter (Linux and Mac only) is not yet supported.
See [doit doc](https://pydoit.org/cmd_other.html?highlight=watch#auto-watch

```python
def task(
 # -- task information
 name=None,   # type: str
 doc=None,    # type: str
 # -- what the task is doing when run
 title=title_with_actions,    # type: Union[str, Callable]
 pre_actions=None,    # type: List[DoitAction]
 actions=None,        # type: List[DoitAction]
 post_actions=None,   # type: List[DoitAction]
 tell_why_am_i_running=True,  # type: bool
 # -- preventing useless runs and selecting order
 targets=None,        # type: List[DoitPath]
 file_dep=None,       # type: List[DoitPath]
 task_dep=None,       # type: List[DoitTask]
 uptodate=None,       # type: List[Optional[Union[bool, Callable, str]]]
 # -- advanced
 setup=None,  # type: List[DoitTask]
 teardown=None,       # type: List[DoitAction]
 getargs=None,        # type: Dict[str, Tuple[str, str]]
 calc_dep=None,       # type: List[DoitTask]
 # -- misc
 verbosity=None       # type: int
 )
```

**Parameters:**

 * `name`: an alternate name for the task. By default the name of the decorated function is used. Note that this parameter will intelligently set 'basename' for normal tasks or 'name' for subtasks in a task generator (`@taskgen`). See [doit doc](https://pydoit.org/tasks.html#task-name)
 
 * `doc`: an optional documentation string for the task. If `@task` is used as a decorator, the decorated function docstring will be used. See [doit doc](https://pydoit.org/tasks.html#doc)
 
 * `title`: an optional message string or callable generating a message, to print when the task is run. If nothing is provided, by default the task name is printed. If a string is provided, the task name will automatically be printed before it. If a callable is provided it should receive a single `task` argument and return a string. See [doit doc](https://pydoit.org/tasks.html#title)
 
 * `pre_actions`: an optional list of actions to be executed before the main action(s). There are 2 basic kinds of actions: cmd-action and python-action. See [doit doc](https://pydoit.org/tasks.html#actions)
 
 * `actions`: a list of actions that this task should execute. If `task` is used as a decorator, this attribute should not be set, as the action will be a call to the decorated function. There are 2 basic kinds of actions: cmd-action and python-action. See [doit doc](https://pydoit.org/tasks.html#actions)
 
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
