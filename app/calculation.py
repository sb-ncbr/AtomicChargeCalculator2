import subprocess
import os

from app.method import method_data
from config import MKL_PATH, PARAMETERS_DIRECTORY, CHARGEFW2_DIR


def calculate(method_name, parameters_name, source, charges):
    args = [f'{CHARGEFW2_DIR}/bin/chargefw2', '--mode', 'charges', '--method', method_name.lower(), '--sdf-file', source, '--chg-file',
            charges]
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = MKL_PATH
    for method in method_data:
        if method['name'] == method_name:
            if method['has_parameters']:
                if parameters_name != 'default':
                    args.extend(['--par-file', os.path.join(PARAMETERS_DIRECTORY, parameters_name)])

    calculation = subprocess.run(args, stderr=subprocess.PIPE, env=env)
    print(' '.join(calculation.args))
    return calculation
