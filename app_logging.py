import logging
import socket
from datetime import UTC, datetime
from pathlib import Path


class SyslogFormatter(logging.Formatter):

    severities = {
        logging.CRITICAL: 2,
        logging.ERROR: 3,
        logging.WARNING: 4,
        logging.INFO: 6,
        logging.DEBUG: 7,
    }

    def format(self, record: logging.LogRecord) -> str:
        severity = self.severities.get(record.levelno, 7)
        priority = 16 * 8 + severity
        timestamp = datetime.fromtimestamp(record.created, UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        app_name = record.name.replace(" ", "_")[:48]
        message = record.getMessage().replace("\r", " ").replace("\n", " ")
        return f"<{priority}>1 {timestamp} {socket.gethostname()} {app_name} {record.process} - - {message}"


class AppLogger:

    def __init__(self, name: str) -> None:
        log_name = name.rsplit(".", maxsplit=1)[-1]
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        if not self.logger.handlers:
            Path("logs").mkdir(exist_ok=True)
            handler = logging.FileHandler(Path("logs") / f"{log_name}.log", encoding="utf-8")
            handler.setFormatter(SyslogFormatter())
            self.logger.addHandler(handler)

    def debug(self, message: str, *args: object) -> None:
        self.logger.debug(message, *args)

    def info(self, message: str, *args: object) -> None:
        self.logger.info(message, *args)

    def warning(self, message: str, *args: object) -> None:
        self.logger.warning(message, *args)

    def error(self, message: str, *args: object) -> None:
        self.logger.error(message, *args)
