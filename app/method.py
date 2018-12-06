import os
import json
from collections import defaultdict

from config import PARAMETERS_DIRECTORY

with open('app/methods.json') as f:
    method_data = json.load(f)

parameter_data = defaultdict(list)
for parameters in os.listdir(PARAMETERS_DIRECTORY):
    with open(os.path.join(PARAMETERS_DIRECTORY, parameters)) as f:
        p_data = json.load(f)
        name = p_data['metadata']['name']
        method = p_data['metadata']['method']
        publication = p_data['metadata']['publication']
        parameter_data[method].append({'name': name, 'publication': publication, 'filename': parameters})
