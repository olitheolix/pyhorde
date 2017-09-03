#!/usr/bin/env python
import os
import sys
import PyQt5.QtCore
import pyhorde3d

# Necessary to load correct OpenGL library
# See https://github.com/spyder-ide/spyder/issues/3226 for details.
from OpenGL import GL
from PyQt5.QtWidgets import QApplication, QOpenGLWidget


class Horde3DWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.cam = self.horde = None

        self.frameCnt = 0
        self.resources = {}

        # Continue with the initialisation once Qt has created the window.
        self.drawTimer = self.startTimer(0)

    def initializeGL(self):
        self.horde = pyhorde3d.PyHorde3D(width=512, height=512, GLVersion=2)
        self.cam = self.setupHorde(self.horde, 512, 512)

    def paintGL(self):
        self.horde.h3dRender(self.cam)
        self.horde.h3dFinalizeFrame()
        self.horde.h3dClearOverlays()

    def resizeGL(self, width, height):
        cam, horde = self.cam, self.horde
        if horde is not None:
            horde.h3dSetNodeParamI(cam, horde.h3dCamera.ViewportXI, 0)
            horde.h3dSetNodeParamI(cam, horde.h3dCamera.ViewportYI, 0)
            horde.h3dSetNodeParamI(cam, horde.h3dCamera.ViewportWidthI, width)
            horde.h3dSetNodeParamI(cam, horde.h3dCamera.ViewportHeightI, height)
            horde.h3dSetNodeParamI(cam, horde.h3dCamera.OccCullingI, 0)

            # Camera parameters.
            fov, near, far = 45, 0.1, 5000
            horde.h3dSetupCameraView(cam, fov, width / height, near, far)
            horde.h3dResizePipelineBuffers(self.resources['shader'], width, height)

    def setupHorde(self, h, width, height):
        # Global Horde options.
        h.h3dSetOption(h.h3dOptions.LoadTextures, 1)
        h.h3dSetOption(h.h3dOptions.TexCompression, 0)
        h.h3dSetOption(h.h3dOptions.MaxAnisotropy, 4)
        h.h3dSetOption(h.h3dOptions.ShadowMapSize, 2048)
        h.h3dSetOption(h.h3dOptions.FastAnimation, 1)

        # Define the resources that we will load manually.
        rt = h.h3dResTypes
        res_raw = [
            ('light', rt.Material, 'materials/light.material.xml'),
            ('HDR', rt.Material, 'pipelines/postHDR.material.xml'),
            ('sky', rt.SceneGraph, 'models/skybox/skybox.scene.xml'),
            ('shader', rt.Pipeline, 'pipelines/forward.pipeline.xml'),
            ('base', rt.SceneGraph, 'models/platform/platform.scene.xml'),
        ]
        del rt

        # Manually load the resources specified above.
        res_path = pyhorde3d.getResourcePath()
        for name, rtype, fname in res_raw:
            # Create the resource and load its definition from file.
            res = h.h3dAddResource(rtype, name, 0)
            fname = os.path.join(res_path, fname)
            h.h3dLoadResource(res, open(fname, 'rb').read())

            # Store the resource as instance variable.
            self.resources[name] = res
            del name, rtype, fname, res
        del res_raw

        # Some resources may list other resources in the XML as path names. We
        # need to load them as well but, fortunately, Horde3D has a convenience
        # function to do the heavy lifting for us here.
        assert h.h3dUtLoadResourcesFromDisk(res_path)
        del res_path

        # Add the platform.
        base = h.h3dAddNode(h.h3dRootNode, self.resources['base'])
        h.h3dSetNodeTransform(base, 0, 1000, 0, 0, 0, 0, 1, 1, 1)
        del base

        # Add the skybox to the scene and scale it.
        s = int(0.9 * 5000 / 1.7)
        skybox = h.h3dAddNode(h.h3dRootNode, self.resources['sky'])
        h.h3dSetNodeFlags(skybox, h.h3dNodeFlags.NoCastShadow, True)
        h.h3dSetNodeTransform(skybox, 0, 0, 0, 0, 0, 0, s, s, s)
        del skybox, s

        # Configure HDR post processing parameters (has no effect if disabled).
        res = self.resources['HDR']
        h.h3dSetMaterialUniform(res, 'hdrExposure', 2.5, 0, 0, 0)
        h.h3dSetMaterialUniform(res, 'hdrBrightThres', 0.5, 0, 0, 0)
        h.h3dSetMaterialUniform(res, 'hdrBrightOffset', 0.08, 0, 0, 0)

        # Add the camera.
        cam = h.h3dAddCameraNode(h.h3dRootNode, 'Camera', self.resources['shader'])

        # Update Horde's log file.
        h.h3dUtDumpMessages()

        return cam

    def timerEvent(self, event):
        """Trigger redraw."""
        # Acknowledget the timer.
        self.frameCnt += 10

        # Render next frame.
        self.horde.h3dSetNodeTransform(self.cam, *[0, self.frameCnt, 0], *[90, 0, 0], *[1, 1, 1])
        self.update()

        self.killTimer(event.timerId())
        self.drawTimer = self.startTimer(20)


def main():
    app = QApplication(sys.argv)

    w = Horde3DWidget()
    w.resize(640, 480)
    w.move(500, 300)
    w.setWindowTitle(f'Horde3D (PyQt {PyQt5.QtCore.PYQT_VERSION_STR})')
    w.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
