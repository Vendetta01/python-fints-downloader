class FinTSServiceInteractionRequired(Exception):
    """Raised when an interaction is requried during FinTSService queries"""
    pass  # pylint: disable=unnecessary-pass


class FinTSServiceTANRequired(Exception):
    """Raised when a FinTS request needs a TAN"""
    pass  # pylint: disable=unnecessary-pass


class NoLoginCredentialsInSession(Exception):
    """Raised when we have a pending dialog without login credentials"""
    pass  # pylint: disable=unnecessary-pass


class FinTSImportPostMissingData(Exception):
    """Raised when we miss data in the POST of a FinTS import"""
    pass  # pylint: disable=unnecessary-pass


class FinTSServiceNoneReturnValue(Exception):
    """Raised when the response object of a FinTS call is None (e.g. invalid TAN)"""
    pass  # pylint: disable=unnecessary-pass
