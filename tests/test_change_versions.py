import glob
import os
import re
import textwrap

import pipcl


g_root = os.path.normpath(f'{__file__}/../..')


def test_change_versions():
    '''
    Check handling of PIPCL_CHANGE_VERSIONS.
    '''
    path_test = f'{g_root}/temp_test_change_version'
    path_wheelhouse = f'{path_test}/wheelhouse'
    pipcl.fs_ensure_empty_dir(path_test)
    
    # Prepare a pip repo.
    pipcl.run(f'pip install --upgrade piprepo "setuptools<81"', prefix='pip install piprepo: ')
    pip_index_url = f'file://{os.path.abspath(path_wheelhouse)}/simple'
    pip_index_url = pip_index_url.replace('\\', '/')
    
    # Add pipcl wheel to pip repo.
    pipcl.run(f'pip wheel -w {path_wheelhouse} {g_root}', prefix='pip wheel pipcl: ')
    pipcl.run(f'piprepo build {path_wheelhouse}', prefix='piprepo build: ')
    
    def make_project(name, version, requires_dist=None, grfbw_version=None):
        '''
        Makes minimal project for package <name>, version <version> and
        prerequisites <requires_dist>'.
        
        If <grfbw_version> is specified:
        
            We also create a get_requires_for_build_wheel() fn that returns
            'example-package-NAME==<grfbw_version>' (`example-package-NAME` is
            a dummy package on pypi.prg for which versions 0.0.1 and 0.0.3 are
            available).

            And at runtime our `build()` function asserts that the specified
            version of `example-package-NAME` is installed. Except if
            example_package_NAME_OVERRIDE is set, it asserts that version
            instead.
        
        This allow us to test that PIPCL_CHANGE_VERSIONS overrides
        get_requires_for_build_wheel() correctly.
        '''
        requires_dist_str = f'requires_dist = {requires_dist!r},' if requires_dist else ''
        pipcl.fs_ensure_empty_dir(f'{path_test}/{name}')
        
        setup_py = ''
        setup_py += textwrap.dedent(f'''
                import pipcl
                ''')
        if name == 'pipcl_test_foo' and grfbw_version:
            setup_py += textwrap.dedent(f'''
                    import importlib.metadata
                    import os
                    def build():
                        example_package_NAME_version = importlib.metadata.version('example-package-NAME')
                        example_package_NAME_OVERRIDE = os.environ.get('example_package_NAME_OVERRIDE')
                        if example_package_NAME_OVERRIDE:
                            pipcl.log(f'Asserting that {{example_package_NAME_version=}} == {{example_package_NAME_OVERRIDE=}}.')
                            assert example_package_NAME_version == example_package_NAME_OVERRIDE, (
                                    f'{{example_package_NAME_version=}} should be {{example_package_NAME_OVERRIDE=}}.'
                                    )
                        else:
                            grfbw_version = {grfbw_version!r}
                            pipcl.log(f'Asserting that {{example_package_NAME_version=}} == {{grfbw_version=}}.')
                            assert example_package_NAME_version == {grfbw_version!r}, (
                                    f'{{example_package_NAME_version=}} should be {{grfbw_version=}}.'
                                    )
                        return []
                    ''')
        else:
            setup_py += textwrap.dedent(f'''
                    def build():
                        return []
                    ''')
        if grfbw_version:
            setup_py += textwrap.dedent(f'''
                    def get_requires_for_build_wheel(config_settings=None):
                        ret = ['example-package-NAME=={grfbw_version}']
                        pipcl.log(f'get_requires_for_build_wheel(): Returning {{ret=}}.')
                        return ret
                    ''')
                    
        setup_py += textwrap.dedent(f'''
                p = pipcl.Package(
                        name = {name!r},
                        version = {version!r},
                        fn_build = build,
                        {requires_dist_str}
                        )
                build_wheel = p.build_wheel
                ''')
        pipcl.fs_write(
                f'{path_test}/{name}/setup.py',
                setup_py,
                )

        pipcl.fs_write(
                f'{path_test}/{name}/pyproject.toml',
                textwrap.dedent('''
                    [build-system]
                        requires = ['pipcl']
                        build-backend = 'setup'
                        backend-path = ['.']
                    ''')
                )
    
    def build_wheel(name, env_extra=None):
        '''
        Build wheel and add it to pip repo. We return the wheel version.
        '''
        newfiles = pipcl.NewFiles(f'{path_wheelhouse}/*.whl')
        # We use --no-deps to avoid pip installing prerequisite packages -
        # i'm not sure why pip does this when merely building a wheel, but it
        # messes up our attempt to check that installing fails if we have used
        # PIPCL_CHANGE_VERSIONS to make wheels incompatible.
        pipcl.run(
                f'''
                    pip wheel
                    -v
                    --no-deps
                    -w {path_wheelhouse}
                    --extra-index-url {pip_index_url}
                    {path_test}/{name}
                    ''',
                prefix=f'build {path_test}/{name}: ',
                env_extra=env_extra,
                )
        wheel = newfiles.get_one()
        pipcl.log(f'{wheel=}')
        wheel_leaf = os.path.basename(wheel)
        m = re.match(f'{name}-([^-]+)-.*.whl', wheel_leaf)
        wheel_version = m.group(1)
        pipcl.run(f'piprepo build {path_wheelhouse}', prefix='piprepo build: ')
        return wheel_version
    
    def install(name, check=1):
        '''
        Install package using pip repo.
        '''
        return pipcl.run(f'''
                pip install
                -v
                --extra-index-url {pip_index_url}
                {name}
                ''',
                check=check,
                )
    
    def clean():
        pipcl.run(f'pip uninstall -y pipcl_test_foo pipcl_test_bar example-package-NAME')
        for p in ([]
                + glob.glob(f'{path_wheelhouse}/pipcl_test_*.whl')
                + glob.glob(f'{path_wheelhouse}/example_package_NAME*.whl')
                ):
            os.remove(p)
    
    make_project('pipcl_test_foo', '1.2.3', requires_dist='pipcl_test_bar==4.5.6', grfbw_version='0.0.3')
    make_project('pipcl_test_bar', '4.5.6')
    
    # Check operation without PIPCL_CHANGE_VERSIONS.
    if 1:
        clean()
        version_bar = build_wheel('pipcl_test_bar')
        version_foo = build_wheel('pipcl_test_foo')
        assert version_foo == '1.2.3'
        assert version_bar == '4.5.6'
        install('pipcl_test_foo')
    
    # Check PIPCL_CHANGE_VERSIONS changes version and requires_dist correctly.
    if 1:
        clean()
        env_extra=dict(
                PIPCL_CHANGE_VERSIONS=textwrap.dedent('''
                    ^pipcl_test_bar$ ==7.8.9
                    example-package-NAME ==0.0.1
                    '''),
                example_package_NAME_OVERRIDE='0.0.1',
                )
        version_bar = build_wheel('pipcl_test_bar', env_extra=env_extra)
        version_foo = build_wheel('pipcl_test_foo', env_extra=env_extra)
        assert version_foo == '1.2.3'
        assert version_bar == '7.8.9'
        install('pipcl_test_foo')
    
    # Check that we get error if we specify different bar versions
    # when building foo vs bar.
    if 1:
        clean()
        env_extra=dict(PIPCL_CHANGE_VERSIONS='^pipcl_test_bar$ ==8.9')
        version_bar = build_wheel('pipcl_test_bar', env_extra=env_extra)
        env_extra=dict(PIPCL_CHANGE_VERSIONS='^pipcl_test_bar$ ==7.8')
        version_foo = build_wheel('pipcl_test_foo', env_extra=env_extra)
        assert version_foo == '1.2.3'
        assert version_bar == '8.9'
        e = install('pipcl_test_foo', check=0)
        assert e
