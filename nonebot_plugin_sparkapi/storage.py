import pickle
from pathlib import Path
from .funcs import trans_preset

PATH = Path(".") / "SparkApi"

def save_obj(obj, name, path):
    if not path.exists():
        path.mkdir(parents=True)
    with open(path / (name + '.pkl'), 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name, path):
    try:
        with open(path / (name + '.pkl'), 'rb') as f:
            return pickle.load(f)
    except:
        return None


SESSION_PATH = PATH / "sessions"

def f_session_load(session_id):
    pack = load_obj(session_id, SESSION_PATH)
    if pack:
        return pack["session"], pack["spname"]
    else:
        return None, None
    
def f_session_save(session, pname, session_id):
    pack = {"session": session, "spname": pname}
    save_obj(pack, session_id, SESSION_PATH)


PRESET_PATH = PATH / "presets"

def f_preset_load(session_id):
    pack = load_obj(session_id, PRESET_PATH)
    if(pack):
        return pack
    else:
        return {}

def f_preset_create(pname, prompt, session_id):
    pack = f_preset_load(session_id)
    pack[pname]=trans_preset(prompt)
    save_obj(pack,session_id,PRESET_PATH)

def f_preset_delete(pname, session_id):
    pack = f_preset_load(session_id)
    if(pack.get(pname)):
        del pack[pname]
        save_obj(pack,session_id,PRESET_PATH)
        return True
    else:
        return False

def f_preset_check(pname, session_id):
    pack = f_preset_load(session_id)
    if(pack.get(pname)):
        return True
    else:
        return False

