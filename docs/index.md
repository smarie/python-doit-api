# doit-api

*`pydoit` for humans: an API to create `doit` tasks faster and more reliably.*

[![Python versions](https://img.shields.io/pypi/pyversions/doit-api.svg)](https://pypi.python.org/pypi/doit-api/) [![Build Status](https://travis-ci.org/smarie/python-doit-api.svg?branch=master)](https://travis-ci.org/smarie/python-doit-api) [![Tests Status](https://smarie.github.io/python-doit-api/junit/junit-badge.svg?dummy=8484744)](https://smarie.github.io/python-doit-api/junit/report.html) [![codecov](https://codecov.io/gh/smarie/python-doit-api/branch/master/graph/badge.svg)](https://codecov.io/gh/smarie/python-doit-api)

[![Documentation](https://img.shields.io/badge/doc-latest-blue.svg)](https://smarie.github.io/python-doit-api/) [![PyPI](https://img.shields.io/pypi/v/doit-api.svg)](https://pypi.python.org/pypi/doit-api/) [![Downloads](https://pepy.tech/badge/doit-api)](https://pepy.tech/project/doit-api) [![Downloads per week](https://pepy.tech/badge/doit-api/week)](https://pepy.tech/project/doit-api) [![GitHub stars](https://img.shields.io/github/stars/smarie/python-doit-api.svg)](https://github.com/smarie/python-doit-api/stargazers)


[`pydoit`](https://pydoit.org/) is a great automation tool, but it is a bit hard to develop fast with it unless knowing by heart all the naming conventions. Indeed it follows a "no api" philosophy, so you have to remember all names and supported types, going back and forth reading the documentation page.

Inspired by [`letsdoit`](https://pypi.org/project/letsdoit), `doit-api` proposes a few api symbols to help you develop faster and more reliably, thanks to IDE autocompletion, docstring display, and type hinting. 


## Installing

```bash
> pip install doit-api
```

## Usage

### Single task

To create a single task you can use the `task` function or the `@pytask` decorator in your `dodo.py` file:

```python
from doit_api import task, pytask

@pytask
def a():
    """ the doc for a """
    print("hi")

@pytask(targets=["out.txt"])
def b():
    print("hi")

c = task(name="echoer", actions=["echo hi"], doc="the doc for e")
```

Then you can list the tasks as usual :

```bash
>>> doit list
a        the doc for a
b
echoer   the doc for e
```

Execute them:

```bash
>>> doit
.  a => Python: function a
.  b => Python: function b
.  echoer => Cmd: echo hi
```

And use verbosity to display the print messages too:

```bash
>>> doit -v 2
.  a => Python: function a
hi
.  b => Python: function b
Running <Task: b> because one of its targets does not exist: 'out.txt'
hi
.  echoer => Cmd: echo hi
hi
```

Note that on that last command, an additional message is automatically added, explaining why task b was run. You can disable this with `tell_why_am_i_running=False`.

See [API reference](./api_reference/#task-or-task) for details.

### Task generator

Now you may wish to create one task *per* something. This is named a task generator, or task group, creating so-called [sub-tasks](https://pydoit.org/tasks.html#sub-tasks). This can be done very easily by creating a python generator function, and decorating it with `@taskgen`.

#### Example 1

For example this is a task group named `mygroup` with two tasks `mygroup:echo0` and `mygroup:echo1`

```python
from doit_api import taskgen, task

@taskgen
def mygroup():
    """ hey !!! """
    for i in range(2):
        yield task(name="echo%s" % i,
                   actions=["echo hi > hoho%s.txt" % i],
                   uptodate=[True],  # so that a second run skips the task
                   targets=["hoho%s.txt" % i],
                   clean=True,
                   doc="echoes %s" % i)
```

Only the group appears in the tasks list by default, you need to activate the `--all` flag to see all:

```bash
>>> doit list
mygroup   hey !!!

>>> doit list --all
mygroup         hey !!!
mygroup:echo0   echoes 0
mygroup:echo1   echoes 1
```

Running the task creates the files as expected, and running a second time skips the tasks (notice the `--` symbol) since the files already exist and we said `update=[True]`:

```bash
>>> doit 
. mygroup:echo0 => Cmd: echo hi > hoho0.txt
. mygroup:echo1 => Cmd: echo hi > hoho1.txt

>>> doit 
-- mygroup:echo0 => Cmd: echo hi > hoho0.txt
-- mygroup:echo1 => Cmd: echo hi > hoho1.txt
```

Finally we can clean the files:

```bash
>>> doit clean
mygroup:echo1 - removing file 'hoho1.txt'
mygroup:echo0 - removing file 'hoho0.txt'
```

#### Example 2

This is a second example with two python subtasks:

```python
from doit_api import taskgen, pytask

@taskgen
def mygroup():
    """ hey !!! """
    for i in range(2):
        @pytask(name="subtask %s" % i,
                doc="a subtask %s" % i,
                title="this is %s running" % i)
        def c_():
            print("hello sub")
        yield c_
```

```bash
>>> doit list --all
mygroup             hey !!!
mygroup:subtask 0   a subtask 0
mygroup:subtask 1   a subtask 1

>>> doit --verbosity 2
.  mygroup:subtask 0 => this is 0 running
hello sub
.  mygroup:subtask 1 => this is 1 running
hello sub
```

You can leverage [`fprules`](https://smarie.github.io/python-fprules/) to generate `make`-like patterns easily:

```python
from fprules import file_pattern
from doit_api import taskgen, pytask

@taskgen
def mygroup():
    """ hey !!! """
    for fp in file_pattern("**/tests/**/[!_]*.py", "%.txt"):
        @pytask(name=fp.name,
                doc=str(fp),
                file_dep=[fp.src_path],
                targets=[fp.dst_path],
                title=str(fp))
        def c_():
            print(">>> (todo) here you use %r to generate %r\n" 
                  % (fp.src_path, fp.dst_path))
        yield c_
```

```bash
>>> doit list --all
mygroup                                        hey !!!
mygroup:doit_api/tests/conftest                [doit_api/tests/conftest] doit_api/tests/conftest.py -> conftest.txt
mygroup:doit_api/tests/test_config             [doit_api/tests/test_config] doit_api/tests/test_config.py -> test_config.txt
mygroup:doit_api/tests/test_task_and_taskgen   [doit_api/tests/test_task_and_taskgen] doit_api/tests/test_task_and_taskgen.py -> test_task_and_taskgen.txt
```

And when executed:

```bash
.  mygroup:doit_api/tests/conftest => [doit_api/tests/conftest] doit_api/tests/conftest.py -> conftest.txt
Running <Task: mygroup:doit_api/tests/conftest> because one of its targets does not exist: 'conftest.txt'
>>> (todo) here you use WindowsPath('doit_api/tests/core/test_task_and_taskgen.py') to generate WindowsPath('test_task_and_taskgen.txt')

.  mygroup:doit_api/tests/core/test_config => [doit_api/tests/core/test_config] doit_api/tests/core/test_config.py -> test_config.txt
Running <Task: mygroup:doit_api/tests/core/test_config> because one of its targets does not exist: 'test_config.txt'
>>> (todo) here you use WindowsPath('doit_api/tests/core/test_task_and_taskgen.py') to generate WindowsPath('test_task_and_taskgen.txt')

.  mygroup:doit_api/tests/core/test_pickling => [doit_api/tests/core/test_pickling] doit_api/tests/core/test_pickling.py -> test_pickling.txt
Running <Task: mygroup:doit_api/tests/core/test_pickling> because one of its targets does not exist: 'test_pickling.txt'
>>> (todo) here you use WindowsPath('doit_api/tests/core/test_task_and_taskgen.py') to generate WindowsPath('test_task_and_taskgen.txt')

.  mygroup:doit_api/tests/core/test_task_and_taskgen => [doit_api/tests/core/test_task_and_taskgen] doit_api/tests/core/test_task_and_taskgen.py -> test_task_and_taskgen.txt
Running <Task: mygroup:doit_api/tests/core/test_task_and_taskgen> because one of its targets does not exist: 'test_task_and_taskgen.txt'
>>> (todo) here you use WindowsPath('doit_api/tests/core/test_task_and_taskgen.py') to generate WindowsPath('test_task_and_taskgen.txt')
```

### Global configuration

`DOIT_CONFIG` is the standard way to configure global options in `doit`. You can create this object very easily with the `doit_config` helper. For example here we set verbosity to be always 2, and configure `doit` to run on 2 processes:

```python
from doit_api import doit_config, pytask

DOIT_CONFIG = doit_config(verbosity=2,   # always verbose
                          num_process=2  # parallel execution on 2 processes
                          )

@pytask
def a():
    """ the doc for a """
    print("hi")

@pytask
def b():
    """ the doc for b """
    print("hello")
```

## Main features / benefits

 * **Develop `doit` tasks faster and more reliably** thanks to you favourite python IDE's autocompletion and documentation features.

## See Also

 - [doit](https://pydoit.org/) of course
 - [fprules](https://smarie.github.io/python-fprules/) a library to help create `make`-like file pattern rules, quite handy for doit tasks. 
 - [letsdoit](https://pypi.org/project/letsdoit/) the project that inspired `doit-api`
 - other doit plugins: 
 
    - [doit-report](https://github.com/saimn/doit-report)
    - [doit-redis](https://github.com/saimn/doit-redis)
    - [doit-graph](https://github.com/pydoit/doit-graph)
    - [doit-py](https://pythonhosted.org/doit-py/)
    - [doit-cmd](https://pythonhosted.org/doit-cmd/)

 - other task engines:
 
   - [celery](https://docs.celeryproject.org), another task engine, generic and asynchronous
   - [nox](https://nox.thea.codes), another task engine oriented towards build/test
   - [invoke](http://www.pyinvoke.org/)

### Others

*Do you like this library ? You might also like [my other python libraries](https://github.com/smarie/OVERVIEW#python)* 

## Want to contribute ?

Details on the github page: [https://github.com/smarie/python-doit-api](https://github.com/smarie/python-doit-api)
