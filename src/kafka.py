import json

from src.env import *

from kafka import KafkaConsumer
from kafka.structs import TopicPartition


servers = f'{MIDDLEWARE_KAFKA_SERVICE_HOST}:{MIDDLEWARE_KAFKA_SERVICE_PORT}'
consumer = KafkaConsumer(
    group_id='analysis',
    bootstrap_servers=servers,
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('UTF-8'))
)

sub = KafkaConsumer(
    group_id='analysis',
    bootstrap_servers=servers,
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('UTF-8'))
)

def get_origin_data_form_kafka(topic, timeout=5000, max_records=1):

    topic_partition = TopicPartition(topic=topic, partition=0)
    consumer.assign([topic_partition])
    msgs = consumer.poll(timeout, max_records)
    result = []
    if msgs == dict():
        result = []
    else:
        for msg in msgs[topic_partition]:
            msg_dict = dict()
            msg_dict['offset'] = msg.offset
            msg_dict['topic'] = msg.topic
            msg_dict['partition'] = msg.partition
            msg_dict['timestamp'] = msg.timestamp
            msg_dict['value'] = msg.value
            msg_dict['timestamp_type'] = msg.timestamp_type
            msg_dict['headers'] = msg.headers
            msg_dict['checksum'] = msg.checksum
            msg_dict['serialized_key_size'] = msg.serialized_key_size
            msg_dict['serialized_value_size'] = msg.serialized_value_size
            msg_dict['serialized_header_size'] = msg.serialized_header_size
            result.append(msg_dict)

    return result


def subscribe_origin_data_form_kafka(timeout=1000, max_records=1):

    sub.subscribe(
        pattern='^test-.*'
    )

    msgs = sub.poll(timeout, max_records)
    result = []
    for msg in msgs.values():
        for _ in msg:
            msg_dict = dict()
            msg_dict['offset'] = _.offset
            msg_dict['topic'] = _.topic
            msg_dict['partition'] = _.partition
            msg_dict['timestamp'] = _.timestamp
            msg_dict['value'] = _.value
            msg_dict['timestamp_type'] = _.timestamp_type
            msg_dict['headers'] = _.headers
            msg_dict['checksum'] = _.checksum
            msg_dict['serialized_key_size'] = _.serialized_key_size
            msg_dict['serialized_value_size'] = _.serialized_value_size
            msg_dict['serialized_header_size'] = _.serialized_header_size
            result.append(msg_dict)

    return result
