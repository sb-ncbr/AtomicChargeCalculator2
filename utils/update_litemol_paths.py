import json
import sys
import os
import subprocess
from glob import glob

manifest_file = sys.argv[1]
deployment_path = sys.argv[2]

with open(manifest_file) as f:
    data = json.load(f)

css = os.path.basename(data['main.css'])
js = os.path.basename(data['main.js'])

args = ['sed', '-i', f's/###litemol.css###/{css}/; s/###litemol.js###/{js}/',
        os.path.join(deployment_path, 'templates', 'results.html')]

print(' '.join(args))
run = subprocess.run(args)
if run.returncode:
    print('HTML update paths not succesfull')

# Update only if litemol changes
if os.path.exists(os.path.join(deployment_path, 'static', 'litemol', 'index.html')):
    os.remove(os.path.join(deployment_path, 'static', 'litemol', 'index.html'))

    g = glob(os.path.join(deployment_path, 'static', 'litemol', 'static', 'css', '*.css'))

    args = ['sed', '-i', '1s#/static/media#/static/litemol/static/media#g', *g]

    print(' '.join(args))
    run = subprocess.run(args)
    if run.returncode:
        print('Litemol css path update not succesfull')
