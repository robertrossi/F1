import json
import logging

from f1.logging_config import JsonFormatter, configure_logging


def test_json_formatter_includes_message_extra_and_exception():
    try:
        raise ValueError("bad data")
    except ValueError:
        record = logging.getLogger("f1.test").makeRecord(
            "f1.test",
            logging.ERROR,
            __file__,
            10,
            "Failed %s",
            ("request",),
            __import__("sys").exc_info(),
            extra={"event": "request_failed", "private": "visible"},
        )

    payload = json.loads(JsonFormatter().format(record))

    assert payload["level"] == "ERROR"
    assert payload["logger"] == "f1.test"
    assert payload["message"] == "Failed request"
    assert payload["event"] == "request_failed"
    assert payload["private"] == "visible"
    assert "ValueError: bad data" in payload["exception"]
    assert "timestamp" in payload


def test_configure_logging_adds_json_handler_once(monkeypatch):
    logger = logging.getLogger("f1")
    original_handlers = logger.handlers[:]
    original_level = logger.level
    original_propagate = logger.propagate
    logger.handlers.clear()
    monkeypatch.setattr("f1.logging_config.logging.StreamHandler", logging.NullHandler)
    try:
        configure_logging()
        configured_handler = logger.handlers[0]
        configure_logging()
        assert len(logger.handlers) == 1
        assert isinstance(configured_handler, logging.NullHandler)
        assert isinstance(configured_handler.formatter, JsonFormatter)
        assert logger.level == logging.INFO
        assert logger.propagate is False
    finally:
        logger.handlers.clear()
        logger.handlers.extend(original_handlers)
        logger.setLevel(original_level)
        logger.propagate = original_propagate
