import os
import platform

import pipcl


def test_visual_studio():
    '''
    This is more a diagnostic tool than a test.
    '''
    print()
    if platform.system() != 'Windows':
        print('test_visual_studio(): not running on non-Windows.')
        return
    vss = pipcl.wdev.windows_vs_multiple()
    print('Visual Studio installations are:')
    for vs in vss:
        print(vs.description_ml(indent='    '))
        d = os.path.dirname(vs.vcvars)
        print(f'    Contents of {d}:')
        for i in os.listdir(d):
            print(f'        {i}')
    
    for year in 2017, 2019, 2022, 2026:
        vs = pipcl.wdev.windows_vs(year=year, check=0)
        print(f'{year=}: {vs=}')
        
