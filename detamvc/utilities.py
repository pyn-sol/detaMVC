import json 
from pathlib import Path
import os

CONFIG_PATH = Path(__file__).parent.resolve() / 'user_config.json'

STYLES = {'BOOTSTRAP', 'MKDOCS'}

def __fetch_config():
    with open(CONFIG_PATH, 'r') as j:
        return json.loads(j.read())

def set_project_key(project_key: str):
    conf = __fetch_config()
    conf['project_key'] = project_key 
    with open(CONFIG_PATH, 'w') as j:
        j.write(json.dumps(conf, indent=4))

def clear_project_key():
    set_project_key("")

def config(key: str or None = None):
    if key:
        return __fetch_config().get(key)
    return __fetch_config()

def valid_style(style: str):
    if style.upper() in STYLES:
        return style.upper()
    else:
        return None

def run_server():
    server_cmd = "uvicorn main:app --reload"
    if check_project_type() == "MKDOCS":
        server_cmd = "mkdocs serve"
    os.system(server_cmd)

def check_project_type():
    project_type = "BOOTSTRAP"
    for (_, _, filenames) in os.walk(os.curdir):
        for fn in filenames:
            if 'mkdocs.yml' in fn:
                project_type = "MKDOCS"
    return project_type
