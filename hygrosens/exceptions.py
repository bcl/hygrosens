# ------------------------------------------------------------------------
# Error Class for Hygrosens module
# ------------------------------------------------------------------------
class HyException(Exception):
    """
    Base class for the Hygrosens library exceptions
    """

Error           = HyException('Error')
CRCError        = HyException('CRC Error')
