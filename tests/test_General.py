"""
Testing PyHPC
=============

The ``PyHPC`` module relies on a system of unit-tests to establish errors in the development process. They are documented
below
"""
import json
import logging
import os
import pathlib as pt
import shutil
import unittest
import sys
import pytest


class TestCore(unittest.TestCase):
    with open(os.path.join(pt.Path(__file__).parents[0], "pytest_data.json")) as f:
        test_data = json.load(f)["TestCore"]
    def setUp(self) -> None:
        sys.path.append(str(pt.Path(os.path.realpath(__file__)).parents[1]))
    def test_configuration(self):
        """Tests the ``PyHPC.PyHPC_core.configuration`` module."""
        #  Loading Modules
        # ----------------------------------------------------------------------------------------------------------------- #
        try:
            from PyHPC.PyHPC_Core.configuration import read_config
        except ImportError:
            raise AssertionError("Couldn't import PyHPC.PyHPC_Core.configuration")

        CONFIG = read_config()

        assert isinstance(CONFIG, dict)

    @pytest.mark.skipif("runner" in os.getcwd(),reason="remote")
    def test_logging(self):
        """Tests the ``PyHPC.PyHPC_core.log`` module."""
        #  Loading Modules
        # ----------------------------------------------------------------------------------------------------------------- #
        try:
            from PyHPC.PyHPC_Core.log import configure_logging
        except ImportError:
            raise AssertionError("Failed to import PyHPC.PyHPC_Core.log")

        configure_logging(__file__)

        for id, dat in enumerate(zip(self.test_data["test_logging"]["loggers"],
                                     self.test_data["test_logging"]["lengths"])):
            logger, length = dat
            with self.subTest(logger, i=id):
                log = logging.getLogger(logger)

                assert len(log.handlers) == length

    def test_utils_getsystem(self):
        """tests the ``PyHPC.PyHPC_Core.utils.get_system_info`` function"""
        try:
            from PyHPC.PyHPC_Core.utils import get_system_info
        except ImportError:
            raise AssertionError("Failed to import PyHPC.PyHPC_Core.utils")

        get_system_info()

    def test_utils_write_ini(self):
        """tests the ``PyHPC.PyHPC_Core.utils.write_ini`` function."""
        try:
            from PyHPC.PyHPC_Core.utils import write_ini
        except ImportError:
            raise AssertionError("Failed to import PyHPC.PyHPC_Core.utils.")

        with open(os.path.join(pt.Path(__file__).parents[0], "temp.ini"),"w") as f:
            try:
                write_ini(self.test_data["test_utils_write_ini"]["ini_dict"],f)
            except Exception:
                raise AssertionError

        with open(os.path.join(pt.Path(__file__).parents[0], "temp.ini"),"r+") as f:
            d = f.read()

        os.remove(os.path.join(pt.Path(__file__).parents[0], "temp.ini"))
        assert d == self.test_data["test_utils_write_ini"]["ini_dict_val"]