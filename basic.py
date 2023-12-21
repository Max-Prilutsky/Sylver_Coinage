import requests
from datetime import date, datetime
import json
endpoint = "http://127.0.0.1:8000"
try:
    print(datetime.now())
    with open("endgame_trial.json", "r") as f:
        data = json.load(f)
    req = requests.get(f"{endpoint}/test", json = data)
    #print(req.json())
except KeyboardInterrupt:
    print(datetime.now())