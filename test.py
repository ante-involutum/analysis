import redis
from datetime import datetime


from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS, SYNCHRONOUS
from influxdb_client.client.exceptions import InfluxDBError


# redis_client = redis.Redis(
#     host='127.0.0.1',
#     port=6379,
#     decode_responses=True,
#     password='changeme'
# )

# r.set('test', 1)
# r.publish("add", 'demo-1')

# redis_client.lpush("tasks", 'demo-1')
# print(redis_client.lrange('tasks', 0, -1))

class BatchingCallback(object):

    def success(self, conf, data: str):
        print(f"Written batch: {conf}, data: {data}")

    def error(self, conf, data: str, exception: InfluxDBError):
        print(f"Cannot write batch: {conf}, data: {data} due: {exception}")

    def retry(self, conf, data: str, exception: InfluxDBError):
        print(
            f"Retryable error occurs for batch: {conf}, data: {data} retry: {exception}")


token = "changeme"
org = "primary"
bucket = "demo"


with InfluxDBClient(url="http://localhost:8086", token='changeme', org='primary') as client:
    callback = BatchingCallback()

    with client.write_api(
            success_callback=callback.success,
            error_callback=callback.error,
            retry_callback=callback.retry
    ) as write_api:

        dictionary = {
            "measurement": "demo",
            "tags": {"task_name": "1"},
            "fields": {"data": 123, "uuid": 123},
            "time": datetime.utcnow()
        }
        write_api.write(bucket, org, dictionary)
