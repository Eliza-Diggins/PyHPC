"""
These are standard testing measures used in the PyHPC framework to check for functionality.

Written by: Eliza Diggins
"""
import logging
from unittest import TestCase
import pathlib as pt
import os
from PyHPC_Core.configuration import read_config
from PyHPC_Core.log import set_logging,get_module_logger
from datetime import datetime
# -------------------------------------------------------------------------------------------------------------------- #
#  Setup ============================================================================================================= #
# -------------------------------------------------------------------------------------------------------------------- #
_location = "uTests"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s:" % (_location, _filename)
CONFIG = read_config()


# Setting up testlogs file #
report_directory = os.path.join(CONFIG["System"]["Directories"]["test_reports"],"Report_%s"%datetime.now().strftime('%m-%d-%Y_%H-%M-%S'))

if not os.path.exists(report_directory):
    pt.Path(report_directory).mkdir(parents=True)


# -------------------------------------------------------------------------------------------------------------------- #
# Standard Tests ===================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
class TestCore(TestCase):
    """
    Test the PyHPC_Core system.
    """
    def test_configuration(self):
        try:
            read_config()
        except Exception as excep:
            raise AssertionError(repr(excep))

    def test_logging(self):
        set_logging(_filename)
        logger_root = logging.getLogger()
        logger_mod = get_module_logger(_location,_filename)

        logger_root.info("Running CoreTests.test_logging...")
        logger_mod.info("Running CoreTests.test_logging...")




