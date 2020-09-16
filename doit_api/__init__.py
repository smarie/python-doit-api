from .main import why_am_i_running, title_with_actions, task, taskgen, pytask, doit_config

try:
    # -- Distribution mode --
    # import from _version.py generated by setuptools_scm during release
    from ._version import version as __version__
except ImportError:
    # -- Source mode --
    # use setuptools_scm to get the current version from src using git
    from setuptools_scm import get_version as _gv
    from os import path as _path
    __version__ = _gv(_path.join(_path.dirname(__file__), _path.pardir))


__all__ = [
    '__version__',
    # submodules
    'main',
    # symbols
    'task', 'taskgen', 'pytask', 'why_am_i_running', 'doit_config'
]
