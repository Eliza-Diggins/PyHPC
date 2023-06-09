"""
================
PyHPC Errors
================
The classes included in this area of the module for a core set of specialized error codes which are called
throughout the ``PyHPC`` system in different contexts.
"""
import sys


# -------------------------------------------------------------------------------------------------------------------- #
#  Global Error ====================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
class PyHPC_Error(Exception):
    def __init__(self, message, status=True):
        self.message, self.status = message, status
        super().__init__(self.message)


# -------------------------------------------------------------------------------------------------------------------- #
#  Text / Printing Errors ============================================================================================ #
# -------------------------------------------------------------------------------------------------------------------- #
class Text_Error(PyHPC_Error):
    def __init__(self, message, status=False):
        super().__init__(message, status)


# -------------------------------------------------------------------------------------------------------------------- #
# Execution Errors =================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
class ExecutionError(PyHPC_Error):
    def __init__(self, message, logger=None, exit=False):
        self.message = message
        self.logger = logger

        super().__init__(self.message)

        #  Logging
        # ----------------------------------------------------------------------------------------------------------------- #
        if logger:
            logger.exception(self.message)

        if exit:
            print("[%s] Execution Failed!\n\t\t%s=%s" % (
                "\u001b[31mExecution Error\u001b[0m",
                "\u001b[36mMessage\u001b[0m",
                self.message
            ))
            sys.exit()


