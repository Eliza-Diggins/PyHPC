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
import unittest
import sys

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
