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

    query = 'from(bucket: "primary") \
    |> range(start: -420m) \
    |> filter(fn: (r) => r["application"] == "kakax") \
    |> filter(fn: (r) => r["_measurement"] == "events" or r["_measurement"] == "jmeter") \
    |> filter(fn: (r) => r["_field"] == "avg") \
    |> yield(name: "mean")'

    result = query_api.query(query)[0].records[0].values.items()
    return result
