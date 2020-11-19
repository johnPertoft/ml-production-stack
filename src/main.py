import logging

from .app import create_application
from .download import DownloadClient
from .events import ServiceEvents
from .metrics import ServiceMetrics
from .model import ModelClient


logging.basicConfig(format="[%(levelname)s] [%(asctime)s] %(message)s")


service_metrics = ServiceMetrics("ml_api_stack")
service_events = ServiceEvents()
download_client = DownloadClient(service_metrics)
model_client = ModelClient(
    host="serving-service.ml-api.svc.cluster.local", grpc_port=8500, http_port=8501
)

app = create_application(
    service_name="ml-api-stack",
    version="1",
    environment="dev",
    api_keys={"test-caller": "12345", "test-caller2": "123456"},
    service_metrics=service_metrics,
    service_events=service_events,
    download_client=download_client,
    model_client=model_client,
)
