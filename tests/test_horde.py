import os
import pyhorde


class TestHorde:
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def setup_method(self, method):
        pass

    def teardown_method(self, method):
        pass

    def setupHorde(self, h, width, height):
        # Global Horde options.
        h.h3dSetOption(pyhorde.h3dOptions.LoadTextures, 1)
        h.h3dSetOption(pyhorde.h3dOptions.TexCompression, 0)
        h.h3dSetOption(pyhorde.h3dOptions.MaxAnisotropy, 4)
        h.h3dSetOption(pyhorde.h3dOptions.ShadowMapSize, 2048)
        h.h3dSetOption(pyhorde.h3dOptions.FastAnimation, 1)

        # Define the resources that we will load manually.
        rt = pyhorde.h3dResTypes
        res_raw = [
            ('light', rt.Material, 'materials/light.material.xml'),
            ('sky', rt.SceneGraph, 'models/skybox/skybox.scene.xml'),
            ('shader', rt.Pipeline, 'pipelines/forward.pipeline.xml'),
            ('base', rt.SceneGraph, 'models/platform/platform.scene.xml'),
        ]
        del rt

        # Manually load the resources specified above.
        res_path = pyhorde.getResourcePath()
        res_loaded = {}
        for name, rtype, fname in res_raw:
            # Create the resource and load its definition from file.
            res = h.h3dAddResource(rtype, name, 0)
            fname = os.path.join(res_path, fname)
            h.h3dLoadResource(res, open(fname, 'rb').read())

            # We will need the resource later.
            res_loaded[name] = res
            del name, rtype, fname, res
        del res_raw

        # Some resources may list other resources in the XML as path names. We
        # need to load them as well but, fortunately, Horde3D has a convenience
        # function to do the heavy lifting for us here.
        assert h.h3dUtLoadResourcesFromDisk(res_path)
        del res_path

        # Add the platform to the scene.
        base = h.h3dAddNode(pyhorde.h3dRootNode, res_loaded['base'])
        h.h3dSetNodeTransform(base, 0, 1000, 0, 0, 0, 0, 1, 1, 1)
        del base

        # Add the skybox to the scene and scale it.
        s = int(0.9 * 5000 / 1.7)
        skybox = h.h3dAddNode(pyhorde.h3dRootNode, res_loaded['sky'])
        h.h3dSetNodeFlags(skybox, pyhorde.h3dNodeFlags.NoCastShadow, True)
        h.h3dSetNodeTransform(skybox, 0, 0, 0, 0, 0, 0, s, s, s)
        del skybox, s

        # Add camera and point it towards the platform.
        cam = h.h3dAddCameraNode(pyhorde.h3dRootNode, 'Camera', res_loaded['shader'])
        near, far = 0.1, 5000
        h.h3dSetupCameraView(cam, 45, width / height, near, far)
        h.h3dResizePipelineBuffers(res_loaded['shader'], width, height)
        h.h3dSetNodeTransform(cam, 0, 0, 0, 90, 0, 0, 1, 1, 1)

        # Screen size for camera.
        h.h3dSetNodeParamI(cam, pyhorde.h3dCamera.ViewportXI, 0)
        h.h3dSetNodeParamI(cam, pyhorde.h3dCamera.ViewportYI, 0)
        h.h3dSetNodeParamI(cam, pyhorde.h3dCamera.ViewportWidthI, width)
        h.h3dSetNodeParamI(cam, pyhorde.h3dCamera.ViewportHeightI, height)
        h.h3dSetNodeParamI(cam, pyhorde.h3dCamera.OccCullingI, 0)

        # Update Horde's log file.
        h.h3dUtDumpMessages()

        return cam

    def test_create_image(self):
        # Delete any stale screenshot.
        fname = '/tmp/foobar.tga'
        try:
            os.remove(fname)
        except FileNotFoundError:
            pass

        # Instantiate EGL context and Horde.
        width = height = 512
        eglDpy = pyhorde.createEGLContext(width, height)
        h = pyhorde.PyHorde3D(width, height, GLVersion=2)

        # Create screenshot and release EGL context.
        assert not os.path.exists(fname)
        h.h3dScreenshotFile(fname)
        assert os.path.exists(fname)
        pyhorde.releaseEGLContext(eglDpy)

    def test_add_find_resource(self):
        """Add and query a texture resource"""
        # Instantiate EGL context and Horde.
        width = height = 512
        eglDpy = pyhorde.createEGLContext(width, height)
        h = pyhorde.PyHorde3D(width, height, GLVersion=2)

        # Load the texture image.
        res_path = pyhorde.getResourcePath()
        fname = os.path.join(res_path, 'models', 'cube', 'textures', '0.jpg')
        img = open(fname, 'rb').read()

        # Verify that we do not yet have a 'foo' texture.
        rt = pyhorde.h3dResTypes
        assert h.h3dFindResource(rt.Texture, 'foo') == 0

        # Add the texture. Now Horde must find it.
        res = h.h3dAddResource(rt.Texture, 'foo', 0)
        h.h3dLoadResource(res, img)
        assert h.h3dFindResource(rt.Texture, 'foo') == res

        # Horde will return the existing resource if added again.
        assert h.h3dAddResource(rt.Texture, 'foo', 0) == res
        assert h.h3dFindResource(rt.Texture, 'foo') == res

        # Release EGL context.
        pyhorde.releaseEGLContext(eglDpy)

    def test_scene(self):
        """Render a complete scene and save screenshot."""
        # Instantiate EGL context and Horde.
        width = height = 512
        eglDpy = pyhorde.createEGLContext(width, height)
        h = pyhorde.PyHorde3D(width, height, GLVersion=2)

        # Setup the scene.
        cam = self.setupHorde(h, width, height)
        h.h3dRender(cam)
        h.h3dFinalizeFrame()
        h.h3dClearOverlays()
        h.h3dUtDumpMessages()

        # Save screenshot, then release the EGL context.
        h.h3dScreenshotFile('/tmp/foobar2.tga')
        pyhorde.releaseEGLContext(eglDpy)
