import pickle

from doit_api import task, pytask


def test_pickle_simple():
    """ Make sure that a `task` can be pickled"""
    t = task(actions=["echo"], name="t")
    pkl = pickle.dumps(t)
    t2 = pickle.loads(pkl)
    assert t2.actions == ["echo"]


@pytask
def mytask():
    """ hello """
    print("hi")


def test_pickle_simple_decorator():
    """ Make sure that a function decorated with `@pytask` can be pickled """

    # this needs to be executed first to simulate what doit is doing
    mytask.create_doit_tasks()
    pkl = pickle.dumps(mytask)
    t2 = pickle.loads(pkl)
    assert t2.create_doit_tasks()['actions'][1] == mytask
