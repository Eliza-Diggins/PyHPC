Module PyHPC.PyHPC_unittests.standard_tests
===========================================
These are standard testing measures used in the PyHPC framework to check for functionality.

Written by: Eliza Diggins

Classes
-------

`TestCore(methodName='runTest')`
:   Test the PyHPC_Core system.
    
    Create an instance of the class that will use the named test
    method when executed. Raises a ValueError if the instance does
    not have a method with the specified name.

    ### Ancestors (in MRO)

    * unittest.case.TestCase

    ### Methods

    `test_configuration(self)`
    :