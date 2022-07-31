from prometheus_client import CollectorRegistry, Gauge

registry = CollectorRegistry(auto_describe=False)


jmeter = Gauge(
    'jmeter',
    'Jmeter Metrics',
    ['job_type', 'topic', 'key'],
    registry=registry
)
