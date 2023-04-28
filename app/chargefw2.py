import os
import subprocess
from collections import Counter, defaultdict

from .config import CHARGEFW2_DIR, LOG_DIR, PARAMETERS_DIRECTORY
from .method import method_data


def calculate(method_name, parameters_name, input_file, charge_out_dir):
    # setup chargefw2 arguments
    chargefw2_binary = os.path.join(CHARGEFW2_DIR, 'bin', 'chargefw2')
    
    logfile = os.path.join(LOG_DIR, 'computations')
    args = [
            chargefw2_binary,
            '--mode', 'charges',
            '--input-file', input_file,
            '--method', method_name,
            '--chg-out-dir', charge_out_dir,
            '--log-file', logfile,
            '--read-hetatm',
            '--permissive-types'
            ]
    # check if method needs parameters
    if next(m for m in method_data if m['internal_name'] == method_name)['has_parameters']:
        args.extend(['--par-file', os.path.join(PARAMETERS_DIRECTORY, parameters_name)])

    # run chargefw2
    calculation = subprocess.run(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    return calculation


def get_suitable_methods(directory: str):
    suitable_methods = Counter()

    for file in os.listdir(os.path.join(directory, 'input')):
        # setup chargefw2 arguments
        chargefw2_binary = os.path.join(CHARGEFW2_DIR, 'bin', 'chargefw2')
        input_file = os.path.join(directory, 'input', file)
        args = [
                chargefw2_binary,
                '--mode', 'suitable-methods',
                '--input-file', input_file,
                '--read-hetatm',
                '--permissive-types',
                ]
        
        # run chargefw2
        calculation = subprocess.run(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        
        # check if calculation was successful
        if calculation.returncode != 0:
            stderr_output = calculation.stderr.decode('utf-8').strip()
            error = stderr_output.split('\n')[-1]
            raise RuntimeError(error)

        # parse output
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
