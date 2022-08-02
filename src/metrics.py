from prometheus_client import CollectorRegistry, Gauge

registry = CollectorRegistry(auto_describe=False)


jmeter = Gauge(
    'jmeter',
    'Jmeter Metrics',
    ['task_type', 'task_name', 'key'],
    registry=registry
)
