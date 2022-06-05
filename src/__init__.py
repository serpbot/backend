import os
import yaml
import logging.config

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logging.yaml"), "r") as f:
    log_cfg = yaml.safe_load(f.read())
    logging.config.dictConfig(log_cfg)