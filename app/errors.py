"""Application-specific errors."""

from __future__ import annotations


class TernRouteError(Exception):
    """Base class for expected TernRoute failures."""


class ConfigurationError(TernRouteError):
    """Raised when required runtime configuration is invalid."""


class ContractError(TernRouteError):
    """Raised when input or output violates the judging contract."""


class RemoteError(TernRouteError):
    """A bounded Fireworks request failure."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        retryable: bool = False,
        fatal: bool = False,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.retryable = retryable
        self.fatal = fatal
