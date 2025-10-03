import logging

from anyon_condense.core.logging import get_logger


def test_get_logger_writes_to_caplog(caplog):
    caplog.set_level(logging.INFO)
    logger = get_logger("test.logger", level="INFO")
    logger.info("hello-world")

    assert any(
        record.levelname == "INFO"
        and record.name == "test.logger"
        and "hello-world" in record.message
        for record in caplog.records
    )


def test_logger_format_and_single_handler():
    get_logger("a.b.c", level="DEBUG")
    root = logging.getLogger()

    ac_handlers = [
        handler for handler in root.handlers if getattr(handler, "_ac_default", False)
    ]
    assert len(ac_handlers) == 1

    formatter = ac_handlers[0].formatter
    assert formatter is not None
    fmt = formatter._fmt  # type: ignore[attr-defined]
    assert "%(asctime)s" in fmt
    assert "%(levelname)s" in fmt
    assert "%(name)s" in fmt
    assert "%(message)s" in fmt

    get_logger("x.y.z", level="ERROR")
    ac_handlers_again = [
        handler for handler in root.handlers if getattr(handler, "_ac_default", False)
    ]
    assert len(ac_handlers_again) == 1
