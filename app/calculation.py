import subprocess

from app.method import method_data


def calculate(method_name, parameters_name, source, charges):
    args = ['./chargefw2', '--mode', 'charges', '--method', method_name.lower(), '--sdf-file', source, '--chg-file',
            charges]
    for method in method_data:
        if method['name'] == method_name:
            if method['has_parameters']:
                if parameters_name == 'default':
                    args.extend(['--par-file', f'/home/krab1k/Research/ChargeFW2/test/{method_name.lower()}.json'])
                else:
                    args.extend(['--par-file', f'/home/krab1k/Research/ChargeFW2/test/{parameters_name}'])

    calculation = subprocess.run(args, cwd='/tmp/chargefw2/bin', stderr=subprocess.PIPE)
    print(' '.join(calculation.args))
    return calculation
