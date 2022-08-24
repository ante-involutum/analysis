# 创建topic
kafka-topics.sh --create --topic kafka-test --replication-factor 1 --partitions 1 --bootstrap-server middleware-kafka.tink:9092

# 查看topic
kafka-topics.sh --list --bootstrap-server middleware-kafka.tink:9092
kafka-topics.sh --bootstrap-server  middleware-kafka.tink:9092 --topic jmeter-example --describe
kafka-topics.sh --bootstrap-server  middleware-kafka.tink:9092 --topic jmeter-example --delete


# 查看消费组
kafka-consumer-groups.sh --list --bootstrap-server middleware-kafka.tink:9092
kafka-consumer-groups.sh  --bootstrap-server middleware-kafka.tink:9092  --describe --group core-demo
kafka-consumer-groups.sh  --bootstrap-server middleware-kafka.tink:9092  --delete --group core-jmeter  


# 消费
kafka-console-consumer.sh --bootstrap-server middleware-kafka.tink:9092 --topic demo-1-0 --from-beginning

# 生产性能测试
kafka-consumer-perf-test.sh --topic jmx --broker-list middleware-kafka.tink:9092 --messages 1000






# minio
mc share download --json --expire 4h minio/jmx/abc |jq '.url' | xargs wget 

# 查看日志
kubectl get pod  -n tink | grep atop | awk '{print $1}' | xargs -n 1 -i{} kubectl logs {} -n tink -c filebeat

# 创建configMap
kubectl create configmap jmx-file --from-file=jmx=/example.jmx -n tink


kubectl get pod  -n tink | grep testing | awk '{print $1}' | xargs -n 1 -i{} kubectl exec -it {} -n tink -- bash






MIDDLEWARE_MINIO_SERVICE_HOST=git.internal.yunify.com
MIDDLEWARE_MINIO_SERVICE_PORT='gitlab'
MIDDLEWARE_MINIO_ACCESS_KEY=lunzhou
MIDDLEWARE_MINIO_SECRET_KEY=hvHim58GjbFgzMi
BUCKET_NAME=listen
PREFIX=hpc_api_test2

git clone https://$MIDDLEWARE_MINIO_ACCESS_KEY:$MIDDLEWARE_MINIO_SECRET_KEY@$MIDDLEWARE_MINIO_SERVICE_HOST/$BUCKET_NAME/$PREFIX.git




TEST_ENV= local
KUBENETES_ENV = local
NAMESPACE = tink
MIDDLEWARE_MINIO_SERVICE_HOST = 127.0.0.1
MIDDLEWARE_MINIO_SERVICE_PORT = 9000
MIDDLEWARE_MINIO_ACCESS_KEY = admin
MIDDLEWARE_MINIO_SECRET_KEY = changeme
BUCKET_NAME = jmx
PREFIX = demo
