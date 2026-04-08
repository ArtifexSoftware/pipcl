import subprocess

# Install required packages. There doesn't seem to be any official way for
# us to programmatically specify required test packages in setup.py, or in
# pytest. Doing it here seems to be the least ugly approach.
#
# However our diagnostics do not show up so this can cause an unfortunate pause
# before tests start to run.
#
def install_required_packages():
    packages = 'flake8 codespell'
    command = f'pip install --upgrade {packages}'
    print(f'{__file__}:install_required_packages)(): Running: {command}', flush=1)
    subprocess.run(command, shell=1, check=1)

install_required_packages()
