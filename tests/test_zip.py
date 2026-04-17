import os
import zipfile

import pipcl


def test_zipfile_writestr():
    # Check pipcl.zipfile_writestr() creates file that extracts with correct
    # mode flags.
    root = os.path.normpath(f'{__file__}/../..')
    
    path_zf = f'{root}/tests/zipfile_writestr_test.zip'
    name = 'test_zip_out.txt'
    path_extracted = f'{root}/tests/{name}'
    
    mode = 0o644
    with zipfile.ZipFile(path_zf, 'w') as zf:
        pipcl.zipfile_writestr(zf, name, 'hello world.', 0o644)
    
    pipcl.fs_remove(path_extracted)
    
    with zipfile.ZipFile(path_zf) as zf:
        zf.extractall(f'{root}/tests')
    
    assert os.path.isfile(path_extracted)
    st = os.stat(path_extracted)
    print(f'{st=}')
    if pipcl.windows():
        # We don't expect extracted file to have specified unix permissions.
        pass
    else:
        # Extracted mode is modified by umask.
        assert (st.st_mode & mode) == mode
