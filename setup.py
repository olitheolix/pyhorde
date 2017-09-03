import os
import sys
import distutils.ccompiler
import multiprocessing.pool

from setuptools import setup
from distutils.extension import Extension
from distutils.sysconfig import customize_compiler
from Cython.Build import cythonize
from Cython.Distutils import build_ext


def parallelCCompile(self, sources, output_dir=None, macros=None,
                     include_dirs=None, debug=0, extra_preargs=None,
                     extra_postargs=None, depends=None):
    """ Compile the C++ files in parallel.

    This "trick" is from here
    https://stackoverflow.com/questions/11013851/speeding-up-build-process-with-distutils
    """
    # Those lines are copied from distutils.ccompiler.CCompiler directly
    macros, objects, extra_postargs, pp_opts, build = self._setup_compile(
        output_dir, macros, include_dirs, sources, depends, extra_postargs)
    cc_args = self._get_cc_args(pp_opts, debug, extra_preargs)

    def _single_compile(obj):
        try:
            src, ext = build[obj]
        except KeyError:
            return
        self._compile(obj, src, ext, cc_args, extra_postargs, pp_opts)

    # Convert to list, imap is evaluated on-demand.
    thread_pool = multiprocessing.pool.ThreadPool(multiprocessing.cpu_count())
    tasks = thread_pool.imap(_single_compile, objects)

    # Tasks will not run until evaluated.
    list(tasks)
    return objects


class my_build_ext(build_ext):
    """Custom extension builder to override compiler flags.

    The main purpose of this class is to remove the pesky -Wstrict-prototypes
    argument. This flag trigggers a harmless compiler warning to state that it
    is not supported for C++, which is why we will remove it in the first place
    now.
    """
    def build_extensions(self):
        customize_compiler(self.compiler)
        try:
            self.compiler.compiler_so.remove("-Wstrict-prototypes")
        except (AttributeError, ValueError):
            pass
        build_ext.build_extensions(self)


def isHordeInstalled():
    fnames = [
        'lib/libHorde3D.so', 'lib/libHorde3DUtils.so',
        'include/horde3d',
        'include/horde3d/Horde3D.h',
        'include/horde3d/Horde3DUtils.h',
    ]

    ok = True
    for fname in fnames:
        if not os.path.exists(os.path.join(sys.prefix, fname)):
            print(f'Error: cannot find {fname}')
            ok = False
    return ok


def main():
    # Monkey patch the setup tools to compile in parallel.
    distutils.ccompiler.CCompiler.compile = parallelCCompile

    if not isHordeInstalled():
        print('\n' + '-' * 80)
        print(f'Error: Cannot find Horde3D libraries. Install them as follows:\n')
        print(f' $ git clone https://github.com/horde3d/Horde3D.git')
        print(f' $ mkdir -p Horde3D/build')
        print(f' $ cd Horde3D/build')
        print(f' $ git checkout 8b17e8bc6f0169303ee5a1021aaee072a76db180')
        print(f' $ cmake .. -DCMAKE_BUILD_TYPE=RELEASE -DCMAKE_INSTALL_PREFIX={sys.prefix}')
        print(f' $ make install')
        print(f'\n' + '-' * 80 + '\n')
        sys.exit(1)

    ext_modules = [
        Extension(
            name='pyhorde',
            sources=['cython/pyhorde.pyx', 'cython/glutils.cpp'],
            include_dirs=[os.path.join(sys.prefix, 'include')],
            library_dirs=[os.path.join(sys.prefix, 'lib')],
            libraries=['Horde3D', 'Horde3DUtils', 'EGL'],
            language='c++',
            extra_compile_args=['-std=c++14'],
            extra_objects=[],
        )
    ]

    setup(
        name='pyhorde',
        version='0.3.0',
        description="Wrapper for Horde3D",
        long_description="",
        author="Oliver Nagy",
        author_email='olitheolix@gmail.com',
        url='https://github.com/olitheolix/pyhorde',
        packages=['pyhorde3d'],
        include_package_data=True,
        scripts=['scripts/ds2render'],
        license='Apache Software License 2.0',
        keywords=['Python', 'Horde3D', 'DS2', 'DS2Server'],
        platforms=['Linux'],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'Intended Audience :: Science/Research',
            'Topic :: Multimedia :: Graphics :: 3D Rendering',
            'License :: OSI Approved :: Apache Software License',
            'Natural Language :: English',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: C++',
            'Programming Language :: Cython',
        ],
        cmdclass={'build_ext': my_build_ext},
        ext_modules=cythonize(ext_modules)
    )


if __name__ == '__main__':
    main()
