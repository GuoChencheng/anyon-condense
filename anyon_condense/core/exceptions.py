"""Custom exception types used across the core package."""


class SchemaError(Exception):
    """Raised for schema loading/validator building issues."""

    pass


class ValidationError(Exception):
    """Raised when a payload fails JSON Schema validation."""

    pass


class DataIOError(Exception):
    """Raised for filesystem or JSON parsing related IO failures."""

    pass


class CanonicalizationError(Exception):
    """Raised when payload cannot be canonicalized."""

    pass


class HashingError(Exception):
    """Raised when hashing/canonical addressing cannot be completed."""

    pass
