"""The command enum definition"""

from enum import Enum


class Command(Enum):
    """All possible commands"""

    ITR = "itr"
    ITV = "itv"
    GTR = "gtr"
    GTV = "gtv"

    @staticmethod
    def list():
        """Return an list with all enum values"""
        return list(map(lambda c: c.value, Command))
