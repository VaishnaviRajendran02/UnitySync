import requests
import threading
from datetime import datetime

url = "http://localhost:5678/webhook/unitysync"

requests_data = [
    {"status":"URGENT","category":"Medical","request":"Elderly chest pain","volunteer":"Anitha"},
    {"status":"URGENT","category":"Repair","request":"Water pipe broken","volunteer":"Selvam"},
    {"status":"NORMAL","category":"Food/Water","request":"Need food packets","volunteer":"Kumar"},
    {"status":"NORMAL","category":"Education","request":"Need study materials","volunteer":"Deepa"},
    {"status":"URGENT","category":"General","request":"Roadside assistance","volunteer":"Rajesh"}
]

def send_req(data):
    data["time"] = str(datetime.now())
    r = requests.post(url, json=data)
    print(data["volunteer"], r.status_code)

threads = []

for item in requests_data:
    t = threading.Thread(target=send_req, args=(item,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("All requests sent.")