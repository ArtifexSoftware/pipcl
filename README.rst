Pipcl
=====

.. contents::
    :backlinks: entry
    :depth: 2


Overview
--------

The ``pipcl`` package provides Python `build backend
<https://packaging.python.org/en/latest/guides/tool-recommendations/#build-backends>`_
operations (including PEP 517 support), for use by a ``setup.py`` script.

* Designed to help build complex Python extension packages.
* Can also be used to build simple pure-python packages.
* Works on Linux, Windows, MacOS and OpenBSD.
* Is a python module, not a framework, so does not impose any restrictions on usage.
* Can be used with any external build system by running commands,
  for example with ``subprocess.run()`` or enhanced wrapper ``pipcl.run()``.

The intention is to allow a ``setup.py`` script to use the full power of Python
to do everything that is specific to the package, without having to worry about
generic Python packaging issues such wheel formats etc (see https://packaging.python.org/en/latest/specifications/).


Basic usage
-----------

To build a pure-python package:

* Create a ``setup.py`` file that imports pipcl and uses it to specify and build a package::

    import pipcl
    
    def build():
        # Creates a module called `mymodule`.
        return [
                ('src/foo.py', 'mymodule/__init__.py'),
                ]
    def sdist():
        return pipcl.git_items('.')
    p = pipcl.Package(
            'mypackage',    # Name of package.
            '1.2.3',        # Package version.
            pure=True,      # Pure python package.
            summary = 'My package',
            description = 'README.md',
            fn_build = build,
            fn_sdist = sdist,
            )
    # PEP 517 support.
    build_wheel = p.build_wheel
    build_sdist = p.build_sdist

* Create a ``pyproject.toml`` that tells pip (and other build frontends) to use setup.py::

    [build-system]
        requires = ['pipcl']
        build-backend = 'setup' # Use setup.py
        backend-path = ['.']    # in top-level of the checkout.

To build a package containing a SWIG extension module, the ``build()`` function
can be modified to use ``pipcl.build_extension()``::

    import pipcl
    
    def build():
        so_leaf = pipcl.build_extension(
                name = 'mymodule',      # Name of extension module.
                path_i = 'src/foo.i',   # SWIG input file.
                outdir = 'build',
                )
        # <so_leaf> will be '_mymodule.so' or similar.
        return [
                ('build/foo.py', 'mymodule/__init__.py'),
                (f'build/{so_leaf}', 'mymodule/'),
                ]        
    def sdist():
        return pipcl.git_items('.')
    p = pipcl.Package(
            'mypackage',    # Name of package.
            '1.2.3',        # Package version.
            summary = 'My package',
            description = 'README.md',
            fn_build = build,
            fn_sdist = sdist,
            )
    # PEP 517 support.
    build_wheel = p.build_wheel
    build_sdist = p.build_sdist

For more details, see doctest examples in file:pipcl.py.


Documentation
-------------

* Detailed documentation is in doc comments in Python code.

  * Convert into HTML with sphinx::
    
      pip install sphinx
      sphinx-build -M html docs docs/_build
    
    View at: file:docs/_build/html/index.html

* Convert ``README.rst`` to html with::

    pip install docutils
    docutils -gdst --halt=3 --pep-references README.rst README.rst.html
  
  View at: file:README.rst.html


API overview
------------

The ``pipcl.Package`` class
...........................

This is similar in approach to setuptools/distutils in that one creates an
instance of the class, passing the package name, version etc.

* Most of the constructor arguments correspond exactly to metadata items in
  https://packaging.python.org/specifications/core-metadata/.

* An explicit function ``fn_build()`` should be provided for building the package.
  This should return a list of files to be included in a wheel or install,
  typically as ``(from, to)`` pairs,
  where ``<from>`` is the path to a file
  and ``<to>`` is the path within a wheel or install.

* An explicit function ``fn_sdist()`` can be provided for building an sdist,
  returning a list of files to include.

* Unlike setuptools, pipcl does not use heuristics for finding files,
  instead everything must be specified exactly.

Other functions and classes
...........................

* ``pipcl.build_extension()`` - build a Python extension using `swig <https://swig.org>`_. Typically
  used by ``pipcl.Package``'s ``fn_build()`` callback.

  * Support for building with the `Limited C API <https://docs.python.org/3/c-api/stable.html#limited-c-api>`_.

* ``pipcl.git_get()``: Create/update a clean git checkout for a particular branch, tag or sha of a remote repository.

* ``pipcl.git_items()``: Get list of files within a git checkout.

* ``pipcl.git_info*()``: Get git information such as sha, comment, diff, branch name, author etc.

* ``pipcl.macos_add_brew_path()``: on MacOS, support for adding package binaries to ``PATH``.

* ``pipcl.macos_patch()``: patching of MacOS shared libraries to avoid use of absolute paths.  

* Class ``pipcl.NewFiles``: Support for simple detection of changed files, for example around running of an external
  command.
  
  This can be useful when building a wheel with ``pip``, as the leafname of the
  wheel is not known in advance.

* ``pipcl.run()``: enhances ``subprocess.run()``,
  providing dynamic output along with capture of output, prefixing of output, timeouts etc.
  
  * Also allows commands to be specified as multiple lines,
    which improves readability in logs.

* ``pipcl.run_if()``: simple dependency checking to only run commands if prerequisites are newer than the output.
  
  * This can use information in Makefile-style ``.d`` dependency files.

* ``pipcl.swig*()``: build and use swig from source;
  this can be useful on MacOS where some swig versions appear to generate incorrect code.

* Class ``pipcl.wdev.WindowsVS``: on Windows, search for specific/latest versions of Visual Studio compiler (cl.exe) and linker (link.exe).
  
  * Has a command string that includes running of an appropriate vcvars, which can be used directly in compile and link command.

Other
.....
* Support for Pyodide.
* Experimental support for Graal.


Changelog
---------

Version 3:

* Avoid unhelpful assert failures on Windows if paths differ only in
  upper/lower case.


Version 2 (2026-04-18):

* Fixed bug in zip file generation on python<3.13.
* Moved Python code into ``src/``.
* Don't attempt to be usable in raw checkout.
* Fixed doctest's to work on Windows.
* Added python_version_tuple().
* Avoid spurious differences between wheels built on different systems:

  * Sort lines in generated RECORD file.
  * Use ``--global core.autocrlf input`` when running ``git clone``.


Version 1 (2026-04-16):

* First release to pypi.org
