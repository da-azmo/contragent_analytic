import sys
from pathlib import Path
import yaml

configs_path = str(Path(__file__).parent.parent / 'configs')

def get_config(config_file_name: str):
    try:
        config_file_path = configs_path + f"/{config_file_name}.yaml"

        with open(config_file_path) as file:
            config = yaml.safe_load(file)
        return config

    except FileNotFoundError:
        raise ValueError (f"Config file '{config_file_name}' in {configs_path} not found")