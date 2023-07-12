class MissingUnitError(ValueError):
    """
    Exception for data missing a unit tag.
    """


class UnitValidationError(ValueError):
    """
    Exception for bad behavior when validating unit-tagged data.
    """


class IncompatibleUnitError(UnitValidationError):
    """
    Exception for attempting to convert between incompatible units.
    """


class UnsupportedExportError(BaseException):
    """
    Exception for attempting to write to an unsupported file format.
    """
