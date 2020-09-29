import os
import json
from collections import defaultdict

from .config import PARAMETERS_DIRECTORY, CHARGEFW2_DIR


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
