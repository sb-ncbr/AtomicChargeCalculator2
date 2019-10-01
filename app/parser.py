import string
import os


__all__ = ['parse_txt', 'parse_cif', 'parse_mol2', 'parse_pdb', 'parse_sdf']


def sanitize_name(name):
    return ''.join(c if c in string.ascii_letters + string.digits else '_' for c in name)


def get_unique_name(name, already_defined):
    count = 0
    new_name = name
    while new_name in already_defined:
        count += 1
        new_name = f'{name}_{count}'

    return new_name


def parse_sdf(f):
    filename = os.path.basename(f.name)
    d = {}

    it = iter(f)
    try:
        while it:
            name = next(it)[:80].strip()
            line = next(it)
            lines = [f'{name}\n', line]
            while line.strip() != '$$$$':
                line = next(it)
                lines.append(line)

            mol_record = ''.join(lines)
            safe_name = sanitize_name(name)
            unique_name = get_unique_name(f'{filename}:{safe_name}', d.keys())
            d[unique_name] = mol_record
    except StopIteration:
        pass

    return d


def parse_cif(f):
    filename = os.path.basename(f.name)
    lines = f.readlines()

    name = ''
    for line in lines:
        if line.startswith('_entry.id'):
            name = line.split()[1]
            break

    record = ''.join(lines)
    return {f'{filename}:{sanitize_name(name)}': record}


def parse_pdb(f):
    filename = os.path.basename(f.name)
    lines = f.readlines()

    name = ''
    for line in lines:
        if line.startswith('HEADER'):
            name = line.split()[-1]
            break
        elif line.startswith('COMPND'):
            name = line.split()[1]
            break
        elif line.startswith('ATOM'):
            # We were unable to find the name
            break

    record = ''.join(lines)
    return {f'{filename}:{sanitize_name(name)}': record}


def parse_mol2(f):
    d = {}
    filename = os.path.basename(f.name)
    lines = []
    name = ''
    try:
        it = iter(f)
        line = next(it)
        while it:
            while line.strip() != '@<TRIPOS>MOLECULE':
                line = next(it)

            lines = [line]
            line = next(it)
            lines.append(line)
            name = line.strip()

            while line.strip() != '@<TRIPOS>MOLECULE':
                line = next(it)
                lines.append(line)

            mol2_record = ''.join(lines)
            safe_name = sanitize_name(name)
            unique_name = get_unique_name(f'{filename}:{safe_name}', d.keys())
            d[unique_name] = mol2_record

    except StopIteration:
        mol2_record = ''.join(lines)
        safe_name = sanitize_name(name)
        unique_name = get_unique_name(f'{filename}:{safe_name}', d.keys())
        d[unique_name] = mol2_record

    return d


def parse_txt(f):
    d = {}
    filename = os.path.basename(f.name)
    base, _ = os.path.splitext(filename)
    it = iter(f)
    try:
        while it:
            name = next(it).strip()
            values = next(it)
            safe_name = sanitize_name(name)
            unique_name = get_unique_name(f'{base}:{safe_name}', d.keys())
            d[unique_name] = f'{name}\n' + values
    except StopIteration:
        pass

    return d
