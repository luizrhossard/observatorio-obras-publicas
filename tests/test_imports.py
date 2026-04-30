def test_import_config():
    from app.config import config  # noqa: F401


def test_import_pipeline_entrypoint():
    import app.main  # noqa: F401

