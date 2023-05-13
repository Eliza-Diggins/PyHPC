"""
These are standard testing measures used in the PyHPC framework to check for functionality.

Written by: Eliza Diggins
"""
import logging
from unittest import TestCase
import pathlib as pt
import os
from PyHPC_Core.configuration import read_config
from PyHPC_Core.log import get_module_logger
from datetime import datetime
from PyHPC_Core.utils import time_function
from PyHPC_System.file_management import get_all_files,get_all_remote_files,rclone_listdir,send_item_to_rclone,get_item_from_rclone
# -------------------------------------------------------------------------------------------------------------------- #
#  Setup ============================================================================================================= #
# -------------------------------------------------------------------------------------------------------------------- #
_location = "uTests"
_filename = pt.Path(__file__).name.replace(".py", "")
_dbg_string = "%s:%s:" % (_location, _filename)
CONFIG = read_config()
modlog = get_module_logger(_location,_filename)
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
    @time_function
    def test_configuration(self):
        try:
            read_config()
        except Exception as excep:
            raise AssertionError(repr(excep))






