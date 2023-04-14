from os import environ

import prometheus_client
import requests
import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import Gauge

app = FastAPI()

PUBLIC_RPC = environ.get("PUBLIC_RPC", "http://135.181.118.28:8080/")
# Disable unwanted metrics
environ.setdefault("PROMETHEUS_DISABLE_CREATED_SERIES", "True")


@app.get("/")
def read_root():
    return {"0L": "Exporter"}


NAMESPACE = "ol"
LABELS = ["diem_chain_id", "account"]


def create_registry():
    registry = prometheus_client.CollectorRegistry(auto_describe=True)
    tower_height = Gauge('tower_height', 'Description', labelnames=LABELS, namespace=NAMESPACE, registry=registry)
    proofs_in_epoch = Gauge('proofs_in_epoch', 'Description', labelnames=LABELS, namespace=NAMESPACE, registry=registry)
    latest_epoch_mining = Gauge('latest_epoch_mining', 'Description', labelnames=LABELS, namespace=NAMESPACE,
                                registry=registry)
    main_metrics = [tower_height, proofs_in_epoch, latest_epoch_mining]
    return registry, main_metrics


@app.get("/metrics/tower")
def tower_metrics(account: str):
    # Registry and set of metrics per request
    registry, main_metrics = create_registry()
    tower_height, proofs_in_epoch, latest_epoch_mining = main_metrics

    # Fetch stats from API
    payload = {
        "method": "get_tower_state_view",
        "jsonrpc": "2.0",
        "id": 1,
        "params": [account]
    }
    print(f"Requesting {PUBLIC_RPC=} for {account=}")
    res = requests.post(PUBLIC_RPC, json=payload)
    data = res.json()
    print(f"{data}")
    if res.status_code != 200 or "error" in data:
        print(f"Error {data}")
        return PlainTextResponse("", status_code=400)

    # Create metrics
    labels = {
        "diem_chain_id": data["diem_chain_id"],
        "account": account,
    }
    tower_height.labels(**labels).set(data["result"]["verified_tower_height"])
    proofs_in_epoch.labels(**labels).set(data["result"]["count_proofs_in_epoch"])
    latest_epoch_mining.labels(**labels).set(data["result"]["latest_epoch_mining"])

    return PlainTextResponse(prometheus_client.generate_latest(registry))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
