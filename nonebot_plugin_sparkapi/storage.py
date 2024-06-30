import pickle
from pathlib import Path
import pandas as pd

from PIL import Image
from io import BytesIO
import base64

PATH = Path(".") / "SparkApi"

def check_path(path=PATH):
    # print(path)
    if not path.exists():
        path.mkdir(parents=True)
    
# 将预设转化为dict类型
def trans_preset(prompt: str):
    ret = {
        'role': 'system',
        'content': prompt
    }
    return ret

SESSION_PATH = PATH / "sessions"

def save_obj(obj, name, path):
    check_path(path)
    with open(path / (name + '.pkl'), 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name, path):
    check_path(path)
    try:
        with open(path / (name + '.pkl'), 'rb') as f:
            return pickle.load(f)
    except:
        return None

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

IMAGE_PATH = PATH / "images"

# 将base64图片数据保存到本地
def f_image_base64_save(base64_data, filename):
    if not IMAGE_PATH.exists():
        IMAGE_PATH.mkdir(parents=True)
    img_data = base64.b64decode(base64_data) # base64解码
    img = Image.open(BytesIO(img_data)) # 读取图片
    img.save(IMAGE_PATH / filename) # 保存图片
    return IMAGE_PATH / filename

