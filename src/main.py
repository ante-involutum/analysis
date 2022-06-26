from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from influxdb_client import InfluxDBClient
from src.config import TOKEN, HOST, PORT

app = FastAPI(name="analysis")

origins = [
    # "http://localhost",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


client = InfluxDBClient(
    url=f"http://{HOST}:{PORT}", token=TOKEN, org='primary')
query_api = client.query_api()


@app.post("/analysis")
async def file_upload():

    query = f'from(bucket: "primary") \
    |> range(start: -10s) \
    |> filter(fn: (r) => r["_measurement"] == "jmeter") \
    |> filter(fn: (r) => r["_field"] == "avg" or r["_field"] == "count" or r["_field"] == "countError" or r["_field"] == "hit" or r["_field"] == "endedT" or r["_field"] == "max" or r["_field"] == "maxAT" or r["_field"] == "meanAT" or r["_field"] == "minAT" or r["_field"] == "min" or r["_field"] == "pct90.0" or r["_field"] == "pct95.0" or r["_field"] == "rb" or r["_field"] == "pct99.0" or r["_field"] == "startedT" or r["_field"] == "sb") \
    |> filter(fn: (r) => r["application"] == "kakax") \
    |> filter(fn: (r) => r["statut"] == "all") \
    |> filter(fn: (r) => r["transaction"] == "all") \
    |> yield(name: "mean")'

    result = query_api.query(query)

    resp = {}
    for i in result:
        a = i.records[-1].values
        resp[a['_field']] = a['_value']
    print(resp)
    return resp
