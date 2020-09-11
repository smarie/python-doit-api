import sys

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

from doit import run
from doit.cmd_base import ModuleTaskLoader, Command
from doit.cmd_list import List
from doit.cmd_run import Run
from doit_api.tests.conftest import CmdFactory

from doit_api import task, taskgen, why_am_i_running


def test_task(monkeypatch, depfile_name, capsys):
    """Tests that our various task generation mechanisms work"""

    @task(title="custom title")
    def a():
        """ hey """
        print("hello !")

    @task(task_dep=[a])
    def b():
        """ hey! """
        print("hello !!")

    @taskgen
    def c():
        """ hey!!! """
        yield task(name="echo", actions=["echo hi"], doc="my echo doc")

        @task
        def c_():
            """here is a doc"""
            print("hello")

        yield c_

    # manually check that loading the tasks works
    loader = ModuleTaskLoader(locals())
    loader.setup({})
    config = loader.load_doit_config()
    task_list = loader.load_tasks(Command(), [])
    assert len(task_list) == 5

    # task a
    assert task_list[0].name == 'a'
    assert task_list[0].doc == a.func.__doc__.strip()
    assert task_list[0].actions[0].py_callable == why_am_i_running
    assert task_list[0].actions[1].py_callable == a.func
    assert task_list[0].title() == 'a => custom title'

    # task b dependency
    assert task_list[1].task_dep == ['a']

    # task c with 2 subtasks
    # todo

    # ---- checks : list
    monkeypatch.setattr(sys, 'argv', ['did', 'list', '--all', '--db-file', depfile_name])
    try:
        # run
        run(locals())
    except SystemExit as err:
        assert err.code == 0, "doit execution error"
    else: # pragma: no cover
        assert False, "Did not receive SystemExit - should not happen"

    captured = capsys.readouterr()
    with capsys.disabled():
        assert captured.out == """a        hey
b        hey!
c        hey!!!
c:c_     here is a doc
c:echo   my echo doc
"""

    # -- checks : execution
    monkeypatch.setattr(sys, 'argv', ['did', '--verbosity', '2', '--db-file', depfile_name])
    try:
        # run
        run(locals())
    except SystemExit as err:
        assert err.code == 0, "doit execution error"
    else:  # pragma: no cover
        assert False, "Did not receive SystemExit - should not happen"

    captured = capsys.readouterr()
    with capsys.disabled():
        assert captured.out == """Running <Task: a> because it declares no mechanism (file_dep or target) to avoid useless executions.
hello !
Running <Task: b> because it declares no mechanism (file_dep or target) to avoid useless executions.
hello !!
Running <Task: c:echo> because it declares no mechanism (file_dep or target) to avoid useless executions.
hi\r
Running <Task: c:c_> because it declares no mechanism (file_dep or target) to avoid useless executions.
hello
"""

    # formal checks:    equivalent of doit list --all
    output = StringIO()
    cmd_list = CmdFactory(List, outstream=output, task_list=task_list)
    cmd_list._execute(subtasks=True, quiet=False)
    assert output.getvalue() == """a        hey
b        hey!
c        hey!!!
c:c_     here is a doc
c:echo   my echo doc
"""

    # formal checks: equivalent of   doit  (execution)
    output = StringIO()
    cmd_run = CmdFactory(Run, backend='dbm', dep_file=depfile_name, task_list=task_list)
    result = cmd_run._execute(output, verbosity=2)
    assert 0 == result
    assert output.getvalue() == """.  a => custom title
.  b => Python: function test_task.<locals>.b
.  c:echo => Cmd: echo hi
.  c:c_ => Python: function test_task.<locals>.c.<locals>.c_
"""
    captured = capsys.readouterr()
    with capsys.disabled():
        assert captured.out == """Running <Task: a> because it declares no mechanism (file_dep or target) to avoid useless executions.
hello !
Running <Task: b> because it declares no mechanism (file_dep or target) to avoid useless executions.
hello !!
Running <Task: c:echo> because it declares no mechanism (file_dep or target) to avoid useless executions.
hi\r
Running <Task: c:c_> because it declares no mechanism (file_dep or target) to avoid useless executions.
hello
"""
