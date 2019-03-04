import os


def parse_sdf(f):
    filename = os.path.basename(f.name)
    d = {}

    it = iter(f)
    try:
        while it:
            name = next(it).strip()
            line = next(it)
            lines = [f'{name}\n', line]
            while line.strip() != '$$$$':
                line = next(it)
                lines.append(line)

            mol_record = ''.join(lines)
            d[f'{filename}:{name}'] = mol_record
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
    return {f'{filename}:{name}': record}


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
    return {f'{filename}:{name}': record}


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
            name = line.strip()

            while line.strip() != '@<TRIPOS>MOLECULE':
                line = next(it)
                lines.append(line)

            mol2_record = ''.join(lines)
            d[f'{filename}: {name}'] = mol2_record

    except StopIteration:
        mol2_record = ''.join(lines)
        d[f'{filename}:{name}'] = mol2_record

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
            d[f'{base}:{name}'] = f'{name}\n' + values
    except StopIteration:
        pass

    return d
