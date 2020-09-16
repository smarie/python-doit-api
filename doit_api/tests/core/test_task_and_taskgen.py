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

from doit_api import task, taskgen, pytask, why_am_i_running


def test_task(monkeypatch, depfile_name, capsys):
    """Tests that our various task generation mechanisms work"""

    @pytask(title="custom title")
    def a():
        """ hey """
        print("hello !")

    @pytask(task_dep=[a])
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
        yield pytask(c_)

        for i in range(2):
            # python task - decorator style
            @pytask(name="subtask %i" % i,
                    doc="a subtask %s" % i,
                    title="this is %s running" % i)
            def c_():
                print("hello sub")
            yield c_

            # python task - non-decorator style
            def d_():
                print("hello variant")
            yield pytask(name="subtask %i variant" % i,
                         doc="a subtask %s variant" % i,
                         title="this is %s running variant" % i)(d_)

    if sys.version_info < (3, 0):
        # doit version is 0.29 on python 2. Internal api is different.
        pass
    else:
        # manually check that loading the tasks works
        loader = ModuleTaskLoader(locals())
        loader.setup({})
        config = loader.load_doit_config()
        task_list = loader.load_tasks(Command(), [])
        assert len(task_list) == 9

        # Note: unfortunately on python 3.5 and 3.6 the order does not seem guaranteed with this api
        # task a
        task_a = [t for t in task_list if t.name == 'a']
        assert len(task_a) == 1
        task_a = task_a[0]
        assert task_a.name == 'a'
        assert task_a.doc == a.__doc__.strip()
        assert task_a.actions[0].py_callable == why_am_i_running
        assert task_a.actions[1].py_callable == a
        assert task_a.title() == 'a => custom title'

        # task b dependency
        task_b = [t for t in task_list if t.name == 'b']
        assert len(task_b) == 1
        task_b = task_b[0]
        assert task_b.task_dep == ['a']

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
Running <Task: c:echo> because one of its targets does not exist: 'hoho.txt'
hi
hello
hello sub
hello variant
hello sub
hello variant
"""

    if sys.version_info < (3, 0):
        # doit version is 0.29 on python 2. Internal api is different.
        pass
    else:
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
Running <Task: c:echo> because one of its targets does not exist: 'hoho.txt'
hi
hello
hello sub
hello variant
hello sub
hello variant
"""
