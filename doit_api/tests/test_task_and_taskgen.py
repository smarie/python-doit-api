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

        # shell commands
        yield task(name="echo", actions=["echo hi"], doc="my echo doc", targets=["hoho.txt"])

        # python task - non-decorator style
        def c_():
            """here is a doc"""
            print("hello")
        yield task(c_)

        for i in range(2):
            # python task - decorator style
            @task(name="subtask %i" % i,
                  doc="a subtask %s" % i,
                  title="this is %s running" % i)
            def c_():
                print("hello sub")
            yield c_

            # python task - non-decorator style
            def d_():
                print("hello variant")
            yield task(d_,
                       name="subtask %i variant" % i,
                       doc="a subtask %s variant" % i,
                       title="this is %s running variant" % i)

    # manually check that loading the tasks works
    loader = ModuleTaskLoader(locals())
    loader.setup({})
    config = loader.load_doit_config()
    task_list = loader.load_tasks(Command(), [])
    assert len(task_list) == 9

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
        assert captured.out == """a                     hey
b                     hey!
c                     hey!!!
c:c_                  here is a doc
c:echo                my echo doc
c:subtask 0           a subtask 0
c:subtask 0 variant   a subtask 0 variant
c:subtask 1           a subtask 1
c:subtask 1 variant   a subtask 1 variant
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
        assert captured.out.replace("\r", "") == """hello !
hello !!
Running <Task: c:echo> because one of its targets does not exist anymore: 'hoho.txt'
hi
hello
hello sub
hello variant
hello sub
hello variant
"""

    # formal checks:    equivalent of doit list --all
    output = StringIO()
    cmd_list = CmdFactory(List, outstream=output, task_list=task_list)
    cmd_list._execute(subtasks=True, quiet=False)
    assert output.getvalue() == """a                     hey
b                     hey!
c                     hey!!!
c:c_                  here is a doc
c:echo                my echo doc
c:subtask 0           a subtask 0
c:subtask 0 variant   a subtask 0 variant
c:subtask 1           a subtask 1
c:subtask 1 variant   a subtask 1 variant
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
.  c:subtask 0 => this is 0 running
.  c:subtask 0 variant => this is 0 running variant
.  c:subtask 1 => this is 1 running
.  c:subtask 1 variant => this is 1 running variant
"""
    captured = capsys.readouterr()
    with capsys.disabled():
        assert captured.out.replace("\r", "") == """hello !
hello !!
Running <Task: c:echo> because one of its targets does not exist anymore: 'hoho.txt'
hi
hello
hello sub
hello variant
hello sub
hello variant
"""
