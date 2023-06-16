"""
These are standard testing measures used in the PyHPC framework to check for functionality.

Written by: Eliza Diggins
"""
import os
import pathlib as pt
from datetime import datetime
from unittest import TestCase

from PyHPC.PyHPC_Core.configuration import read_config
import logging
from PyHPC.PyHPC_Core.utils import time_function

# -------------------------------------------------------------------------------------------------------------------- #
#  Setup ============================================================================================================= #
# -------------------------------------------------------------------------------------------------------------------- #
_location = "uTests"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s:" % (_location, _filename)
CONFIG = read_config()
modlog = logging.getLogger(__name__)
# Setting up testlogs file #
report_directory = os.path.join(CONFIG["System"]["Directories"]["test_reports"],
                                "Report_%s" % datetime.now().strftime('%m-%d-%Y_%H-%M-%S'))

if not os.path.exists(report_directory):
    pt.Path(report_directory).mkdir(parents=True)


# -------------------------------------------------------------------------------------------------------------------- #
# Standard Tests ===================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
class TestCore(TestCase):
    """
    Test the PyHPC_Core system.
    """

    @time_function
    def test_configuration(self):
        try:
            read_config()
        except Exception as excep:
            raise AssertionError(repr(excep))
