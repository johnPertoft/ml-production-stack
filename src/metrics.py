import logging

from pydantic import PositiveInt

# TODO: Use google-cloud-monitoring here.
# TODO: time measurements, or can we get this in some other way?

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class ServiceMetrics:
    def __init__(self, metric_namespace: str) -> None:
        self.metric_namespace = metric_namespace

    def increment(self, metric_name: str, value: PositiveInt = 1) -> None:
        logger.info(f"Incrementing {self.metric_namespace}.{metric_name} by {value}")
