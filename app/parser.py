import string
import os
from typing import IO, Dict, Iterable


__all__ = ['parse_txt', 'parse_cif', 'parse_cif_from_string', 'parse_pdb', 'parse_sdf', 'get_MOL_versions']


def sanitize_name(name: str) -> str:
    return ''.join(c.upper() if c in string.ascii_letters + string.digits else '_' for c in name)


def get_unique_name(name: str, already_defined: Iterable[str]) -> str:
    count = 0
    new_name = name
    while new_name in already_defined:
        count += 1
        new_name = f'{name}_{count}'

    return new_name


def parse_sdf(f: IO[str]) -> Dict[str, str]:
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


def parse_cif_from_string(record: str, filename: str) -> Dict[str, str]:
    name = ''
    for line in record.splitlines():
        if line.startswith('_entry.id'):
            name = line.split()[1]
            break

    return {f'{filename}:{sanitize_name(name)}': record}


def parse_pdb(f: IO[str]) -> Dict[str, str]:
    filename = os.path.basename(f.name)
    lines = f.readlines()

    name, _ = os.path.splitext(filename)
    for line in lines:
        if line.startswith('HEADER'):
            name = line.split()[-1]
            break
        elif line.startswith('ATOM'):
            # We were unable to find the name
            break

    record = ''.join(lines)
    return {f'{filename}:{sanitize_name(name)}': record}


def parse_txt(f: IO[str]) -> Dict[str, str]:
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


def get_MOL_versions(filename: str):
    def get_version(text: str):
        return text[34:39]

    def skip_header(file: IO[str]):
        next(file)
        next(file)
        next(file)

    versions = set()
    f = open(filename)

    skip_header(f)
    versions.add(get_version(next(f)))
    try:
        while True:
            line = next(f)
            while line.strip() != '$$$$':
                line = next(f)
            skip_header(f)
            versions.add(get_version(next(f)))

    except StopIteration:
        pass

    f.close()

    return versions
