import logging
import re
from typing import Any


class SensitiveDataFilter(logging.Filter):
    """Logging filter that redacts API keys, bearer tokens, credentials, and secrets from all backend log records."""

    SENSITIVE_PARAM_PATTERN = re.compile(
        r"([?&](?:api_key|access_token|token|secret|key|password)=)([^&\s\'\"#]+)",
        re.IGNORECASE,
    )
    BEARER_PATTERN = re.compile(
        r"((?:bearer\s+|authorization[\"\'\s:]+bearer\s+))([a-zA-Z0-9_\-\.]+)",
        re.IGNORECASE,
    )

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """Redact sensitive query parameters and auth tokens from arbitrary text."""
        text = cls.SENSITIVE_PARAM_PATTERN.sub(r"\g<1>***REDACTED***", text)
        text = cls.BEARER_PATTERN.sub(r"\g<1>***REDACTED***", text)
        return text

    @classmethod
    def sanitize_value(cls, val: Any) -> Any:
        """Recursively sanitize strings, URLs, dictionaries, lists, and tuples."""
        if isinstance(val, str):
            return cls.sanitize_text(val)
        elif isinstance(val, dict):
            return {k: cls.sanitize_value(v) for k, v in val.items()}
        elif isinstance(val, tuple):
            return tuple(cls.sanitize_value(v) for v in val)
        elif isinstance(val, list):
            return [cls.sanitize_value(v) for v in val]
        return val

    def filter(self, record: logging.LogRecord) -> bool:
        """Sanitize message and any formatted arguments."""
        if isinstance(record.msg, str):
            record.msg = self.sanitize_text(record.msg)
        if record.args:
            if isinstance(record.args, tuple):
                record.args = tuple(self.sanitize_value(v) for v in record.args)
            elif isinstance(record.args, dict):
                record.args = {k: self.sanitize_value(v) for k, v in record.args.items()}
            else:
                record.args = self.sanitize_value(record.args)
        return True


def setup_backend_logging(level: int = logging.INFO) -> None:
    """Configure backend logging with SensitiveDataFilter installed on all handlers."""
    format_str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(level=level, format=format_str)
    sensitive_filter = SensitiveDataFilter()
    for handler in logging.root.handlers:
        if not any(isinstance(f, SensitiveDataFilter) for f in handler.filters):
            handler.addFilter(sensitive_filter)
