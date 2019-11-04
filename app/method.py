import os
import json
import requests
from collections import defaultdict

from .config import PARAMETERS_DIRECTORY, CHARGEFW2_DIR


def get_publication(doi: str) -> str:
    url = 'https://doi.org/' + doi
    headers = {'Accept': 'text/x-bibliography;style=apa'}
    res = requests.get(url, headers=headers)
    if res.status_code == requests.codes.ok:
        return res.content.decode('utf8').strip()
    else:
        return doi


with open(os.path.join(CHARGEFW2_DIR, 'share', 'methods.json')) as f:
    method_data = json.load(f)

method_data = method_data["methods"]

parameter_data = defaultdict(list)
for parameters in sorted(os.listdir(PARAMETERS_DIRECTORY)):
    with open(os.path.join(PARAMETERS_DIRECTORY, parameters)) as f:
        p_data = json.load(f)
        name = p_data['metadata']['name']
        method = p_data['metadata']['method']
        publication = p_data['metadata']['publication']
        parameter_data[method].append({'name': name, 'publication': publication, 'filename': parameters})

PUBLICATION_CACHE = '/tmp/publication_info.json'
publication_data = {}
try:
    with open(PUBLICATION_CACHE) as f:
        publication_data = json.load(f)
except IOError:
    pass

for method in method_data:
    doi = method['publication']
    if doi is not None and doi not in publication_data:
        publication_data[doi] = get_publication(doi)

for method in parameter_data.values():
    for parameter in method:
        doi = parameter['publication']
        if doi is not None and doi not in publication_data:
            publication_data[doi] = get_publication(doi)

with open(PUBLICATION_CACHE, 'w') as f:
    json.dump(publication_data, f)
