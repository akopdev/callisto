from callisto import Callisto


def test_single_task():
    """Minimal setup."""
    app = Callisto()

    @app.task
    def get_hundred():
        return 100

    assert app.run() == 100


def test_multiple_tasks_with_labels():
    """Multiple tasks (sync/async), and reference through labels."""

    app = Callisto()

    @app.task(name="hundred")
    def first():
        return 100

    @app.task
    async def final(hundred):
        return hundred * 2

    assert app.run() == 200


def test_runtime_artifacts():
    """Task access runtime artifacts."""

    app = Callisto()

    @app.task
    async def multiply(hundred):
        return hundred * 2

    assert app.run(hundred=100) == 200


def test_multiple_run_with_different_runtime():
    """Different runtime artifacts should lead to different results."""

    app = Callisto()

    @app.task
    async def multiply(hundred):
        return hundred * 2

    assert app.run(hundred=100) == 200
    assert app.run(hundred=200) == 400
