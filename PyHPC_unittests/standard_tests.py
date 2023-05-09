"""
These are standard testing measures used in the PyHPC framework to check for functionality.

Written by: Eliza Diggins
"""
from unittest import TestCase
import pathlib as pt
import os
from PyHPC_Core.configuration import read_config
from datetime import datetime
# -------------------------------------------------------------------------------------------------------------------- #
#  Setup ============================================================================================================= #
# -------------------------------------------------------------------------------------------------------------------- #
_location = "uTests"
_filename = pt.Path(__file__).name.replace(".py", "")
_utest_path = pt.Path(__file__).parents[1]
_dbg_string = "%s:%s:" % (_location, _filename)
CONFIG = read_config()


# Setting up testlogs file #
report_directory = "Report_%s"%datetime.now().strftime('%m-%d-%Y_%H-%M-%S')

if not os.path.exists(os.path.join(_utest_path,"testlogs",report_directory)):
    pt.Path(os.path.join(_utest_path,"testlogs",report_directory)).mkdir(parents=True)


# -------------------------------------------------------------------------------------------------------------------- #
# Standard Tests ===================================================================================================== #
# -------------------------------------------------------------------------------------------------------------------- #
class TestCore(TestCase):
    """
    Test the PyHPC_Core system.
    """
    def test_configuration(self):
        pass


