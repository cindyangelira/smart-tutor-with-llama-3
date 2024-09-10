import json

with open('config.json', 'r') as f:
    CONFIG = json.load(f)

MODEL_CONFIG = CONFIG
SEED = CONFIG["seed"]
