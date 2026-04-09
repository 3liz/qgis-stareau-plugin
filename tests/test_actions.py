import pytest

from stareau.actions import runner


def test_action_run():
    """Test that action is indeed run"""
    runner.run("noop_action", a="hello", b=1,  c=True)

    with pytest.raises(runner.InvalidArgumentError):
        raise runner.run("noop_action", a="hello", b="world", c=True)

    with pytest.raises(runner.MissingParameterError):
        raise runner.run("noop_action", a="hello", c=True)

    with pytest.raises(runner.MethodNotFoundError):
        raise runner.run("i_do_not_exists")
