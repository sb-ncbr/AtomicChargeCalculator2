from typing import Optional
import os
import subprocess


def prepare_mol2(tmpdir: str, method: str, parameters: Optional[str]):
    calculation = subprocess.run(['obabel', os.path.join(tmpdir, 'structures.sdf'), '-omol2', '--partialcharge',
                                  'none', '-O', os.path.join(tmpdir, 'structures.mol2')])
    print(' '.join(calculation.args))

    charges = {}
    with open(os.path.join(tmpdir, 'charges')) as f:
        for line in f:
            name = line.strip()
            line = next(f)
            charge_values = [float(chg) for chg in line.split()]
            charges[name] = charge_values

    with open(os.path.join(tmpdir, 'structures.mol2')) as f:
        structures = f.read()

    with open(os.path.join(tmpdir, 'charges.mol2'), 'w') as f:
        it = iter(structures.split('\n'))
        for line in it:
            if line == '@<TRIPOS>MOLECULE':
                print(line, file=f)
                line = next(it)
                charge_values = charges[line]
                print(line, file=f)
                # Copy counts line
                line = next(it)
                print(line, file=f)
                # Copy molecule type
                line = next(it)
                print(line, file=f)
                # Replace GASTEIGER with USER_CHARGES
                line = next(it)
                print('USER_CHARGES', file=f)
                # Read optional stars delimiting and add comment
                line = next(it)
                if line == '****':
                    line = next(it)
                print('****', file=f)
                print(f'Partial charges computed by ChargeCompute (method: {method}, parameters: {parameters})', file=f)
                # Copy @<TRIPOS>ATOM
                line = next(it)
                print(line, file=f)

                for val in charge_values:
                    line = next(it)
                    print(f'{line[:-6]}{val:-6.3f}', file=f)
            else:
                print(line, file=f)
