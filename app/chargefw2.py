import subprocess
import os
from collections import Counter, defaultdict

from .method import method_data
from .config import MKL_PATH, PARAMETERS_DIRECTORY, CHARGEFW2_DIR


def calculate(method_name, parameters_name, source, charge_out_dir):
    args = [os.path.join(CHARGEFW2_DIR, 'bin', 'chargefw2'), '--mode', 'charges', '--method', method_name,
            '--input-file', source, '--chg-out-dir', charge_out_dir, '--read-hetatm']
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = MKL_PATH
    if next(m for m in method_data if m['internal_name'] == method_name)['has_parameters']:
        if parameters_name != 'default':
            args.extend(['--par-file', os.path.join(PARAMETERS_DIRECTORY, parameters_name)])

    calculation = subprocess.run(args, stderr=subprocess.PIPE, env=env, stdout=subprocess.PIPE)
    print(' '.join(calculation.args))
    return calculation


def get_suitable_methods(directory: str):
    suitable_methods = Counter()
    for file in os.listdir(os.path.join(directory, 'input')):
        fullname = os.path.join(directory, 'input', file)

        env = os.environ.copy()
        env['LD_LIBRARY_PATH'] = MKL_PATH

        args = [os.path.join(CHARGEFW2_DIR, 'bin', 'chargefw2'), '--mode', 'suitable-methods', '--read-hetatm',
                '--input-file', fullname]
        calculation = subprocess.run(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
        print(' '.join(calculation.args))
        if calculation.returncode:
            print(calculation.stderr.decode('utf-8'))
            raise RuntimeError('Cannot get suitable methods')

        for line in calculation.stdout.decode('utf-8').splitlines():
            if not line.strip():
                continue
            method, *parameters = line.strip().split()
            if not parameters:
                suitable_methods[(method,)] += 1
            else:
                for p in parameters:
                    suitable_methods[(method, p)] += 1

    all_valid = [pair for pair in suitable_methods if
                 suitable_methods[pair] == len(os.listdir(os.path.join(directory, 'input')))]

    methods = list({pair[0] for pair in all_valid})
    parameters = defaultdict(list)
    for pair in all_valid:
        if len(pair) == 2:
            parameters[pair[0]].append(pair[1])

    return methods, parameters
