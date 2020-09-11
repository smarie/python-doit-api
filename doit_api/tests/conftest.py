"""
Copied from doit/tests/conftest.py : utilities to test doit's behaviour
"""
import os
import pytest

from doit.dependency import DbmDB, Dependency, MD5Checker


# fixture for "doit.db". create/remove for every test
def remove_db(filename):
    """remove db file from anydbm"""
    # dbm on some systems add '.db' on others add ('.dir', '.pag')
    extensions = [
        '', #dbhash #gdbm
        '.bak', #dumbdb
        '.dat', #dumbdb
        '.dir', #dumbdb #dbm2
        '.db', #dbm1
        '.pag', #dbm2
    ]
    for ext in extensions:
        if os.path.exists(filename + ext):
            os.remove(filename + ext)


@pytest.fixture
def depfile_name(request, tmp_path_factory):
    """A fixture for a temporary doit database file(s) that will be removed after running"""
    depfile_name = str(tmp_path_factory.mktemp('x', True) / 'testdb')
    def remove_depfile():
        remove_db(depfile_name)
    request.addfinalizer(remove_depfile)

    return depfile_name


def CmdFactory(cls, outstream=None, task_loader=None, dep_file=None,
               backend=None, task_list=None, sel_tasks=None,
               dep_manager=None, config=None, cmds=None):
    """helper for test code, so test can call _execute() directly"""

    # this import does not work in python 2 (doit 0.29)
    from doit.cmd_base import get_loader
    loader = get_loader(config, task_loader, cmds)
    cmd = cls(task_loader=loader, config=config, cmds=cmds)

    if outstream:
        cmd.outstream = outstream
    if backend:
        assert backend == "dbm"  # the only one used on tests
        cmd.dep_manager = Dependency(DbmDB, dep_file, MD5Checker)
    elif dep_manager:
        cmd.dep_manager = dep_manager
    cmd.dep_file = dep_file  # (str) filename usually '.doit.db'
    cmd.task_list = task_list  # list of tasks
    cmd.sel_tasks = sel_tasks  # from command line or default_tasks
    return cmd
