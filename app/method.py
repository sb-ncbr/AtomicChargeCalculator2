import json

with open('app/methods.json') as f:
    method_data = json.load(f)

with open('app/parameters.json') as f:
    parameter_data = json.load(f)
