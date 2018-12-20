import subprocess
import os

from app.method import method_data
from config import MKL_PATH, PARAMETERS_DIRECTORY, CHARGEFW2_DIR


def calculate(method_name, parameters_name, options, source, charges):
    args = [os.path.join(CHARGEFW2_DIR, 'bin', 'chargefw2'), '--mode', 'charges', '--method', method_name.lower(),
            '--sdf-file', source, '--chg-file', charges]
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = MKL_PATH
    if next(m for m in method_data if m['name'] == method_name)['has_parameters']:
        if parameters_name != 'default':
            args.extend(['--par-file', os.path.join(PARAMETERS_DIRECTORY, parameters_name)])

    for name, value in options.items():
        args.extend([f'--method-{name}', value])

    calculation = subprocess.run(args, stderr=subprocess.PIPE, env=env, stdout=subprocess.PIPE)
    print(' '.join(calculation.args))
    return calculation
