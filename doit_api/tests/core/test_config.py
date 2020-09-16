import json
import os
import platform
import sys

import pytest
from doit import run
from doit.cmd_base import ModuleTaskLoader
from doit.doit_cmd import DoitMain

from doit_api import doit_config, task


@pytest.mark.skipif(sys.version_info < (3, 0), reason="this test does not run on old doit 0.29")
def test_config_simple(capsys):

    DOIT_CONFIG = doit_config(backend='r')

    loader = ModuleTaskLoader(locals())
    loader.setup({})
    config = loader.load_doit_config()

    assert config == {'backend': 'r'}

    res = DoitMain(ModuleTaskLoader(locals())).run(())
    assert res == 3

    captured = capsys.readouterr()
    with capsys.disabled():
        assert "TypeError: 'NoneType' object is not callable" in captured.err


def test_valid_config(monkeypatch, depfile_name):
    monkeypatch.setattr(sys, 'argv', ['did'])

    # create custom config with various settings
    DOIT_CONFIG = doit_config(default_tasks=['a', 'b'],   # task 'ignored' should not be run
                              continue_=True,             # a will fail but b will still run
                              single=True,                # task 'ignored' should not be run even if a dep of a
                              always=True,                # a will run even if it is up to date
                              # database
                              db_file="tmp_db.json",  # the db file will be this one
                              dep_file=None,          # alias for db_file, ok
                              backend="json",         # and it will contain json text
                              # verbosity
                              verbosity=2,            # 'echo hi' should be captured in capsys
                              failure_verbosity=2,    # a report should be issued at the end
                              # output reporter and cwd
                              outfile="tmp_out.txt",   # all output except 'echo hi' should be in that file
                              reporter='console',      # default
                              # dir='./tmp',
                              # parallel
                              num_process=2,            # the output is slightly different in parallel mode we can check this
                              parallel_type='thread',

                              )

    ignored = task(name="ignored", actions=["ignored"])
    a = task(name="a", task_dep=[ignored], actions=["ech hi"], uptodate=[True])
    b = task(name="b", actions=["echo hi"])

    try:
        # run
        run(locals())
    except SystemExit as err:
        # error code seems to be 1 on windows and 2 on linux (travis)
        assert err.code >= 1, "doit execution error"
    else:  # pragma: no cover
        assert False, "Did not receive SystemExit - should not happen"

    # Validate that the outcome takes all config options into account
    with open("tmp_db.json", mode="rt") as f:
        resdict = json.loads(f.read())
    os.remove("tmp_db.json")
    assert len(resdict) == 1
    result_str = resdict['b']['result:']
    if sys.version_info > (3, 0):
        assert isinstance(result_str, str)
    assert len(result_str) > 0

    # Validate output
    with open("tmp_out.txt", mode="rt") as f:
        out_str = f.read()
    os.remove("tmp_out.txt")

    win = platform.system() == "Windows"
    if sys.version_info > (3, 0):
        assert out_str == """.  a => Cmd: ech hi
.  b => Cmd: echo hi
%(failed_type)s - taskid:a
Command %(failed)s: 'ech hi' returned %(failed_code)s

########################################
%(failed_type)s - taskid:a
Command %(failed)s: 'ech hi' returned %(failed_code)s

a <stderr>:
%(errmsg)s

a <stdout>:

""" % dict(failed_type='TaskFailed' if win else 'TaskError',
           failed='failed' if win else 'error',
           failed_code=1 if win else 127,
           errmsg="'ech' is not recognized as an internal or external command,\n"
                  "operable program or batch file." if win else "/bin/sh: 1: ech: not found")
    else:
        assert out_str == """.  a => Cmd: ech hi
.  b => Cmd: echo hi
########################################
%(failed_type)s - taskid:a
Command %(failed)s: 'ech hi' returned %(failed_code)s

%(errmsg)s

""" % dict(failed_type='TaskFailed' if win else 'TaskError',
           failed='failed' if win else 'error',
           failed_code=1 if win else 127,
           errmsg="'ech' is not recognized as an internal or external command, \n"
                  "operable program or batch file." if win else "/bin/sh: 1: ech: not found")
