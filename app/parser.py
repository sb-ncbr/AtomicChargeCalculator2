import os
import string
from typing import IO, Dict, Iterable, List


def sanitize_name(name: str) -> str:
    return ''.join(c.upper() if c in string.ascii_letters + string.digits else '_' for c in name)


def get_unique_name(name: str, already_defined: Iterable[str]) -> str:
    count = 0
    new_name = name
    while new_name in already_defined:
        count += 1
        new_name = f'{name}_{count}'

    return new_name


# This is not necessary (output files are named the same as TXT output molecules)
def parse_cif(f: IO[str]) -> Dict[str, str]:
    filename = os.path.basename(f.name)
    lines = f.readlines()

    name = ''
    for line in lines:
        if line.startswith('_entry.id'):
            name = line.split()[1]
            break

    record = ''.join(lines)
    return {f'{filename}:{sanitize_name(name)}': record}


def parse_txt(f: IO[str]) -> Dict[str, List[float]]:
    name_to_charges: Dict[str, List[float]] = {}
    filename = os.path.basename(f.name)
    base, _ = os.path.splitext(filename)
    it = iter(f)
    try:
        while it:
            name = next(it).strip()
            charges = next(it)
            safe_name = sanitize_name(name)
            unique_name = get_unique_name(f'{base}:{safe_name}', name_to_charges.keys())
            name_to_charges[unique_name] = [float(charge) for charge in charges.split()]
    except StopIteration:
        pass

    return name_to_charges
