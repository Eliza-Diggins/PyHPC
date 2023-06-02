Module PyHPC.PyHPC_Core.errors
==============================
Error Classes

Classes
-------

`PyHPC_Error(message, status=True)`
:   Common base class for all non-exit exceptions.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

    ### Descendants

    * PyHPC.PyHPC_Core.errors.Text_Error

`Text_Error(message, status=False)`
:   Common base class for all non-exit exceptions.

    ### Ancestors (in MRO)

    * PyHPC.PyHPC_Core.errors.PyHPC_Error
    * builtins.Exception
    * builtins.BaseException