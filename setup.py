import sys

try:
    import pipcl
except ImportError:
    # This only happens if we are run directly without use of pyproject.toml,
    # e.g. setup.py sdist.
    sys.path.insert(0, 'src')
    import pipcl


def build():
    return [
            ('src/pipcl.py', 'pipcl/__init__.py'),
            ('src/wdev.py', 'pipcl/wdev.py'),
            ]


def sdist():
    return pipcl.git_items('.')


p = pipcl.Package(
        'pipcl',
        version = '2',
        pure = True,
        description='README.rst',
        summary='Python packaging operations, including PEP-517 support, for use by a setup.py script.',
        author='Artifex',
        author_email='julian.smith@artifex.com',
        license='GNU AFFERO GPL 3.0',
        project_url=[
                'homepage, https://github.com/ArtifexSoftware/pipcl',
                ],
        fn_build = build,
        fn_sdist = sdist,
        )


build_wheel = p.build_wheel
build_sdist = p.build_sdist


if __name__ == '__main__':
    p.handle_argv(sys.argv)
