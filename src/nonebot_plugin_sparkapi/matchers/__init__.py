import importlib
import pathlib

for path in pathlib.Path(__file__).parent.iterdir():
    if path.is_file() and path.suffix == ".py" and not path.stem.startswith("_"):
        importlib.import_module(f".{path.stem}", __name__)
