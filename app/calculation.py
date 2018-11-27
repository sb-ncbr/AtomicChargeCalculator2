import subprocess

from app.method import method_data

def calculate(method_name, source, charges):
    args = ['./chargefw2', '--mode', 'charges', '--method', method_name.lower(), '--sdf-file', source, '--chg-file', charges]
    for method in method_data:
        if method['name'] == method_name:
            if method['_parameters'] is not None:
               args.extend(['--par-file', f'/home/krab1k/Research/ChargeFW2/test/{method_name.lower()}.json']) 

    calculation = subprocess.run(args, cwd='/tmp/chargefw2/bin', stderr=subprocess.PIPE)
    return calculation

