import os
import pytest
import pyhorde3d


# Will only be True if the `SkipHordeTests` environment variable exists and
# is set to 1. This covers local testing and CI and AWS. Locally, because the
# variable will not be set, and on AWS the CI script will set the environment
# variable in the Docker container. This is useful if the CI instance has no
# GPU, as the tests would otherwise fail.
skipHorde = os.getenv('SkipHordeTests', '0') == '1'


@pytest.mark.skipif(skipHorde, reason="Instance has no GPU")
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

    def test_create_image(self):
        # Delete stale screenshot.
        fname = '/tmp/foobar.tga'
        try:
            os.remove(fname)
        except FileNotFoundError:
            pass

        # Instantiate Horde and EGL context.
        h = pyhorde3d.PyHorde3D()

        # Create screenshot.
        assert not os.path.exists(fname)
        h.h3dScreenshotFile(fname)
        assert os.path.exists(fname)

    def test_add_find_resource(self):
        """Add and query a texture resource"""
        # Instantiate Horde and EGL context.
        h = pyhorde3d.PyHorde3D()

        # Load the image.
        res_path = pyhorde3d.getResourceFolder()
        fname = os.path.join(res_path, 'models', 'cube', 'number.jpg')
        img = open(fname, 'rb').read()

        # Verify that we do not yet have a 'foo' texture.
        rt = h.h3dResTypes
        assert h.h3dFindResource(rt.Texture, 'foo') == 0

        # Add the texture. Now Horde must find it.
        res = h.h3dAddResource(rt.Texture, 'foo', 0)
        h.h3dLoadResource(res, img)
        assert h.h3dFindResource(rt.Texture, 'foo') == res

        # Horde will return the existing resource if added again.
        assert h.h3dAddResource(rt.Texture, 'foo', 0) == res
        assert h.h3dFindResource(rt.Texture, 'foo') == res
