import os
import tempfile

import pipcl


def test_nogit_check():
    '''
    Check pipcl.git_info_py() in a non-git-checkout.
    '''
    GITHUB_ACTIONS = os.environ.get('GITHUB_ACTIONS')
    if GITHUB_ACTIONS == 'true':
        print(f'test_nogit_check(): not running on Github because tempdir is within checkout.')
        return
    with tempfile.TemporaryDirectory() as path:
        try:
            text = pipcl.git_info_py(path)
        except Exception:
            text = None
        else:
            print(f'{text=}')
            assert 0, f'Expected exception for directory: {path}'
    print(f'{text=}')


def test_nogit_nocheck():
    path = tempfile.gettempdir()
    text = pipcl.git_info_py(path, check=0)
    print(f'{text}')
