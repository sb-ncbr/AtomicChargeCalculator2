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
                name = next(it)
                # Check if we have calculated charges for the molecule
                if name in charges:
                    print(line, file=f)
                    print(name, file=f)
                    charge_values = charges[name]
                else:
                    # Skip the whole record
                    line = next(it)
                    parts = line.split()
                    atom_count, bond_count = int(parts[0]), int(parts[1])
                    for _ in range(3):
                        line = next(it)
                    if line == '****':
                        next(it)
                    for _ in range(atom_count + bond_count + 2):
                        next(it)
                    continue

                # Get counts and copy the line
                line = next(it)
                print(line, file=f)
                parts = line.split()
                atom_count, bond_count = int(parts[0]), int(parts[1])
                if atom_count != len(charge_values):
                    raise ValueError('Charges don\'t match')

                # Copy molecule type
                line = next(it)
                print(line, file=f)

                # Replace GASTEIGER with USER_CHARGES
                next(it)
                print('USER_CHARGES', file=f)

                # Read optional stars delimiting and add comment
                line = next(it)
                if line == '****':
                    next(it)
                print('****', file=f)
                print(f'Partial charges computed by ChargeCompute (method: {method}, parameters: {parameters})', file=f)

                # Copy @<TRIPOS>ATOM
                line = next(it)
                print(line, file=f)

                for val in charge_values:
                    line = next(it)
                    print(f'{line[:-6]}{val:-6.3f}', file=f)

                # Copy @<TRIPOS>BOND
                line = next(it)
                print(line, file=f)
                for _ in range(bond_count):
                    line = next(it)
                    print(line, file=f)
