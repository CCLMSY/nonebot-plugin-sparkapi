sessions = {} # 会话记录
spname = {} # 选取的prompt
presets = {} # 人物预设列表

# 将预设prompt转化为dict类型
def trans_preset(prompt: str):
    ret = {
        'role': 'system',
        'content': prompt
    }
    return ret

# from pathlib import Path
# import pandas as pd

# PATH = Path(".") / "SparkApi"

# def check_path(path=PATH):
#     # print(path)
#     if not path.exists():
#         path.mkdir(parents=True)

# def save_dict_as_csv(data, filename, path):
#     check_path(path)
#     df = pd.DataFrame(data)
#     df.to_csv(path / (filename + '.csv'), index=True)

# def load_csv_as_dict(filename, path):
#     check_path(path)
#     try:
#         df = pd.read_csv(path / (filename + '.csv'))
#         return df.to_dict(orient='records')
#     except:
#         return None