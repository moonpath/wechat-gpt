import logging
import json


def get_json_field(config_file: str, field_path: str):
    try:
        with open(config_file, "r") as f:
            json_config = json.load(f)
            sub_config = json_config

            fields = field_path.lstrip("$.").split(".")
            for field in fields:
                sub_config = sub_config[field]
    except Exception as e:
        logging.error(f"json: {e}")
    return sub_config