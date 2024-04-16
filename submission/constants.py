"""
constants.py

This module contains constants related to possible commands and errors.
"""

COMMANDS = ["itr", "itv", "gtr", "gtv"]

ERRORS = {
    1: "INVALID_MESSAGE_CODE",
    2: "INCORRECT_MESSAGE_LENGTH",
    3: "INVALID_PARAMETER",
    4: "INVALID_SINGLE_TOKEN",
    5: "ASCII_DECODE_ERROR",
}
