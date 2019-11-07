import subprocess
import os
from collections import Counter, defaultdict

from .method import method_data
from .config import PARAMETERS_DIRECTORY, CHARGEFW2_DIR, LOG_DIR


def calculate(method_name, parameters_name, source, charge_out_dir):
    logfile = os.path.join(LOG_DIR, 'computations')
    args = [os.path.join(CHARGEFW2_DIR, 'bin', 'chargefw2'), '--mode', 'charges', '--method', method_name,
            '--input-file', source, '--chg-out-dir', charge_out_dir, '--read-hetatm', '--log-file', logfile,
            '--permissive-types']
    if next(m for m in method_data if m['internal_name'] == method_name)['has_parameters']:
        args.extend(['--par-file', os.path.join(PARAMETERS_DIRECTORY, parameters_name)])

    calculation = subprocess.run(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    print(' '.join(calculation.args))
    return calculation


def get_suitable_methods(directory: str):
    suitable_methods = Counter()
    for file in os.listdir(os.path.join(directory, 'input')):
        fullname = os.path.join(directory, 'input', file)

        args = [os.path.join(CHARGEFW2_DIR, 'bin', 'chargefw2'), '--mode', 'suitable-methods', '--read-hetatm',
                '--permissive-types', '--input-file', fullname]
        calculation = subprocess.run(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        print(' '.join(calculation.args))
        if calculation.returncode:
            output = calculation.stderr.decode('utf-8').strip()
            print(output)
            error = output.split('\n')[-1]
            raise RuntimeError(error)

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

    # Remove duplicates from methods
    tmp = {}
    for data in all_valid:
        tmp[data[0]] = None
    methods = list(tmp.keys())

    parameters = defaultdict(list)
    for pair in all_valid:
        if len(pair) == 2:
            parameters[pair[0]].append(pair[1])

    return methods, parameters
