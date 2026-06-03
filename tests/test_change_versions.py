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
    
    def make_project(name, version, requires_dist=None):
        '''
        Makes minimal project for package <name>, version <version> and
        prerequisites <requires_dist>')
        '''
        requires_dist_str = f'requires_dist = {requires_dist!r},' if requires_dist else ''
        pipcl.fs_ensure_empty_dir(f'{path_test}/{name}')
        pipcl.fs_write(
                f'{path_test}/{name}/setup.py',
                textwrap.dedent(f'''
                    import pipcl
                    def build():
                        return []
                    p = pipcl.Package(
                            name = {name!r},
                            version = {version!r},
                            fn_build = build,
                            {requires_dist_str}
                            )
                    build_wheel = p.build_wheel
                    '''),
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
        pipcl.run(f'pip uninstall -y pipcl_test_foo pipcl_test_bar')
        for p in glob.glob(f'{path_wheelhouse}/pipcl_test_foo-*.whl') + glob.glob('{path_wheelhouse}/pipcl_test_foo-*.whl'):
            os.remove(p)
    
    make_project('pipcl_test_foo', '1.2.3', requires_dist='pipcl_test_bar==4.5.6')
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
        env_extra=dict(PIPCL_CHANGE_VERSIONS='^pipcl_test_bar$ 7.8.9')
        version_bar = build_wheel('pipcl_test_bar', env_extra=env_extra)
        version_foo = build_wheel('pipcl_test_foo', env_extra=env_extra)
        assert version_foo == '1.2.3'
        assert version_bar == '7.8.9'
        install('pipcl_test_foo')
    
    # Check that we get error if we specify different bar versions
    # when building foo vs bar.
    if 1:
        clean()
        env_extra=dict(PIPCL_CHANGE_VERSIONS='^pipcl_test_bar$ 8.9')
        version_bar = build_wheel('pipcl_test_bar', env_extra=env_extra)
        env_extra=dict(PIPCL_CHANGE_VERSIONS='^pipcl_test_bar$ 7.8')
        version_foo = build_wheel('pipcl_test_foo', env_extra=env_extra)
        assert version_foo == '1.2.3'
        assert version_bar == '8.9'
        e = install('pipcl_test_foo', check=0)
        assert e
