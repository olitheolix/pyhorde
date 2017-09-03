import os
import pyhorde

__version__ = '0.4.0'


# This is the Cython wrapped engine.
PyHorde3D = pyhorde.Engine

createEGLContext = pyhorde.createEGLContext
releaseEGLContext = pyhorde.releaseEGLContext

h3dCamera = pyhorde.h3dCamera
h3dEmitter = pyhorde.h3dEmitter
h3dLight = pyhorde.h3dLight
h3dModelUpdateFlags = pyhorde.h3dModelUpdateFlags
h3dNodeFlags = pyhorde.h3dNodeFlags
h3dNodeTypes = pyhorde.h3dNodeTypes
h3dOptions = pyhorde.h3dOptions
h3dPartEffRes = pyhorde.h3dPartEffRes
h3dRenderDevice = pyhorde.h3dRenderDevice
h3dResTypes = pyhorde.h3dResTypes
h3dRootNode = pyhorde.h3dRootNode


def getResourcePath():
    """ Return absolute path to default resources.

    The default resources are copies of those that ship with the original
    Horde3D engines. They are useful to build small demos to ensure the engine
    works.
    """
    return os.path.dirname(os.path.abspath(__file__))
