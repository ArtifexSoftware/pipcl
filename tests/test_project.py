import os
import sys
import textwrap

g_root = os.path.normpath(f'{__file__}/../..')

import pipcl

pipcl.log(f'{sys.path=}')


def test_project():
    '''
    We create a python project which builds a python extension with a setup.py
    file that uses pipcl, and check that pip installs pipcl in response to the
    pyproject.toml and builds the project.
    '''
    path_test = f'{g_root}/temp_test'
    pipcl.fs_ensure_empty_dir(path_test)
    
    pipcl.log('## Prepare a piprepo containing a pipcl wheel.')
    pipcl.run(f'pip install --upgrade piprepo "setuptools<81"', prefix='pip install piprepo: ')
    newfiles = pipcl.NewFiles(f'{path_test}/wheelhouse/*.whl')
    pipcl.run(f'pip wheel -w {path_test}/wheelhouse {g_root}', prefix='pip wheel pipcl: ')
    path_wheel = newfiles.get_one()
    pipcl.run(f'piprepo build {path_test}/wheelhouse', prefix='piprepo build: ')
    pip_index_url = f'file://{os.path.abspath(path_test)}/wheelhouse/simple'
    pip_index_url = pip_index_url.replace('\\', '/')
    
    
    pipcl.log('## Create package called `foo` that uses pipcl to build.')
    pipcl.run(f'pip uninstall -y foo')
    pipcl.fs_ensure_empty_dir(f'{path_test}/project')
    pipcl.fs_write(
            f'{path_test}/project/setup.py',
            textwrap.dedent('''
                import subprocess
                def run(command):
                    print(f'Running: {command}', flush=1)
                    subprocess.run(command, shell=1, check=1)
                    
                import pipcl
                
                def build():
                    so_leaf = pipcl.build_extension(
                            name = 'pipcl_test_module',
                            path_i = 'foo.i',
                            outdir = 'build',
                            source_extra = 'wibble.c',
                            )
                    return [
                            ('build/pipcl_test_module.py', 'pipcl_test_module/__init__.py'),
                            ('cli.py', 'pipcl_test_module/__main__.py'),
                            (f'build/{so_leaf}', f'pipcl_test_module/'),
                            ('README', '$dist-info/'),
                            (b'Hello world', 'pipcl_test_module/hw.txt'),
                            ]

                def sdist():
                    ret = list()
                    for p in git_items('.'):
                        ret.append(p)
                    return ret

                p = pipcl.Package(
                        name = 'foo',
                        version = '1.2.3',
                        fn_build = build,
                        fn_sdist = sdist,
                        entry_points = (
                            {
                                'console_scripts':
                                [
                                    'foo_cli = foo.__main__:main',
                                ],
                            }
                            ),
                        )

                build_wheel = p.build_wheel
                build_sdist = p.build_sdist

                # Handle old-style setup.py command-line usage:
                if __name__ == '__main__':
                    p.handle_argv(sys.argv)
                '''),
            )
    pipcl.fs_write(
            f'{path_test}/project/pyproject.toml',
            textwrap.dedent('''
                [build-system]
                requires = ["pipcl", "swig"]
                
                # See pep-517.
                build-backend = "setup"
                backend-path = ["."]
                ''')
            )
    pipcl.fs_write(
            f'{path_test}/project/foo.i',
            textwrap.dedent('''
                %include bar.i
                %{
                #include <stdio.h>
                #include <string.h>
                int bar(const char* text)
                {
                    printf("bar(): text: %s\\\\n", text);
                    int len = (int) strlen(text);
                    printf("bar(): len=%i\\\\n", len);
                    fflush(stdout);
                    return len;
                }
                %}
                int bar(const char* text);
                ''')
            )
    pipcl.fs_write(
            f'{path_test}/project/bar.i',
            textwrap.dedent('''
                ''')
            )
    pipcl.fs_write(
            f'{path_test}/project/wibble.c',
            textwrap.dedent('''
                ''')
            )
    pipcl.fs_write(
            f'{path_test}/project/README',
            textwrap.dedent('''
                This is Foo.
                ''')
            )
    pipcl.fs_write(
            f'{path_test}/project/cli.py',
            textwrap.dedent('''
                def main():
                    print('pipcl_test:main().')
                if __name__ == '__main__':
                    main()
                ''')
            )
    
    pipcl.log('## Build project foo, allowing pip to get pipcl from our piprepo\'d wheelhouse.')
    newfiles = pipcl.NewFiles(f'{path_test}/*.whl')
    pipcl.run(f'''
            pip wheel
            -v
            -w {path_test}
            --extra-index-url {pip_index_url}
            {path_test}/project
            ''',
            prefix=f'build {path_test}/project: ',
            )
    
    pipcl.log('## Install project foo')
    path_foo_wheel = newfiles.get_one()
    pipcl.run(f'pip uninstall -y foo')
    pipcl.run(f'pip install {path_foo_wheel}', prefix=f'pip install {path_foo_wheel}: ')
    
    pipcl.log('## Check we can import pipcl_test_module.')
    pipcl.log(f'{sys.path=}')
    import pipcl_test_module


def test_wheel_cr():
    path_test = f'{g_root}/temp_test_wheel_cr'
    pipcl.fs_ensure_empty_dir(path_test)
    
    pipcl.log('## Prepare a piprepo containing a pipcl wheel.')
    pipcl.run(f'pip install --upgrade piprepo "setuptools<81"', prefix='pip install piprepo: ')
    newfiles = pipcl.NewFiles(f'{path_test}/wheelhouse/*.whl')
    pipcl.run(f'pip wheel -w {path_test}/wheelhouse {g_root}', prefix='pip wheel pipcl: ')
    path_wheel = newfiles.get_one()
    pipcl.run(f'piprepo build {path_test}/wheelhouse', prefix='piprepo build: ')
    pip_index_url = f'file://{os.path.abspath(path_test)}/wheelhouse/simple'
    pip_index_url = pip_index_url.replace('\\', '/')
    
    pipcl.fs_ensure_empty_dir(f'{path_test}/project')
    pipcl.fs_write(
            f'{path_test}/project/setup.py',
            textwrap.dedent(f'''
                    import pipcl
                    
                    def build():
                        pipcl.fs_write(f'foo_cr.py', b'print("hello world")\\n', binary=1)
                        return [
                                ('foo_cr.py'),
                                ]
                    
                    p = pipcl.Package(
                            name = 'foo_cr',
                            version = '1.2.3',
                            fn_build = build,
                            )
                    
                    build_wheel = p.build_wheel
                    build_sdist = p.build_sdist
                    '''),
            )
    pipcl.fs_write(
            f'{path_test}/project/pyproject.toml',
            textwrap.dedent('''
                [build-system]
                    requires = ['pipcl']
                    build-backend = 'setup'
                    backend-path = ['.']
                ''')
            )
    
    newfiles = pipcl.NewFiles(f'{path_test}/*.whl')
    pipcl.run(f'''
            pip wheel
            -v
            -w {path_test}
            --extra-index-url {pip_index_url}
            {path_test}/project
            ''',
            prefix=f'build {path_test}/project: ',
            )
    path_foo_wheel = newfiles.get_one()
    
    import zipfile
    with zipfile.ZipFile(path_foo_wheel) as zf:
        zf.extractall(f'{path_test}/extracted')
    st = os.stat(f'{path_test}/extracted/foo_cr.py')
    print(f'{st=}')
    
    pipcl.log('## Install project foo')
    pipcl.run(f'pip uninstall -y foo_cr')
    pipcl.run(f'pip install {path_foo_wheel}', prefix=f'pip install {path_foo_wheel}: ')
    
    pipcl.log('## Check we can import pipcl_test_module.')
    pipcl.log(f'{sys.path=}')
    import foo_cr
    
