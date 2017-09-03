import os
import pyhorde_cython

__version__ = '0.4.0'


# This is the Cython wrapped engine.
PyHorde3D = pyhorde_cython.Engine

# Create/release EGL context for headless rendering.
createEGLContext = pyhorde_cython.createEGLContext
releaseEGLContext = pyhorde_cython.releaseEGLContext

# Horde3D constants.
h3dCamera = pyhorde_cython.h3dCamera
h3dEmitter = pyhorde_cython.h3dEmitter
h3dLight = pyhorde_cython.h3dLight
h3dModelUpdateFlags = pyhorde_cython.h3dModelUpdateFlags
h3dNodeFlags = pyhorde_cython.h3dNodeFlags
h3dNodeTypes = pyhorde_cython.h3dNodeTypes
h3dOptions = pyhorde_cython.h3dOptions
h3dPartEffRes = pyhorde_cython.h3dPartEffRes
h3dRenderDevice = pyhorde_cython.h3dRenderDevice
h3dResTypes = pyhorde_cython.h3dResTypes
h3dRootNode = pyhorde_cython.h3dRootNode


def getResourcePath():
    """ Return absolute path to default resources.

    The default resources are copies of those that ship with the original
    Horde3D engines. They are useful to build small demos to ensure the engine
    works.
    """
    return os.path.dirname(os.path.abspath(__file__))
