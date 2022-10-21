import json 
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.resolve() / 'user_config.json'

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
