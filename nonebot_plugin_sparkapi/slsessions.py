import pickle
from pathlib import Path

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

PATH = Path(".") / "SparkApi"
SESSION_PATH = PATH / "sessions"

def save_session(session, pname, session_id):
    pack = {"session": session, "pname": pname}
    save_obj(pack, session_id, SESSION_PATH)

def load_session(session_id):
    pack = load_obj(session_id, SESSION_PATH)
    if pack:
        return pack["session"], pack["pname"]
    else:
        return None, None