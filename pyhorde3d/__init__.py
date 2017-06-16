import os
import pyhorde

# This is the Cython wrapped engine.
PyHorde3D = pyhorde.PyHorde3D

__version__ = '0.3.0'


def getResourcePath():
    """ Return absolute path to default resources.

    The default resources are copies of those that ship with the original
    Horde3D engines. They are useful to build small demos to ensure the engine
    works.
    """
    return os.path.dirname(os.path.abspath(__file__))
