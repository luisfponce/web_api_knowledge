"""Generator-specific exception types."""


class GeneratorError(Exception):
    """Base class for expected generator failures."""


class ValidationError(GeneratorError):
    """Raised when a project configuration is invalid."""


class RenderError(GeneratorError):
    """Raised when rendering cannot safely complete."""


class SanityCheckError(GeneratorError):
    """Raised when generated output fails static checks."""
