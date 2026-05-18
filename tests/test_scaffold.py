def test_agent_package_importable():
    import agent  # noqa: F401


def test_main_stub_raises():
    import pytest
    from agent.main import main
    with pytest.raises(NotImplementedError):
        main("dummy task")


def test_demos_importable():
    import demos  # noqa: F401
