import pipcl

import tempfile


# Check pipcl.git_info_py() in a non-git-checkout.

def test_nogit_check():
    path = tempfile.gettempdir()
    try:
        text = pipcl.git_info_py(path)
    except Exception:
        text = None
    else:
        assert 0, f'Expected exception for directory: {path}'
    print(f'{text}')


def test_nogit_nocheck():
    path = tempfile.gettempdir()
    text = pipcl.git_info_py(path, check=0)
    print(f'{text}')
