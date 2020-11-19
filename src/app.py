import logging
from typing import Mapping
from uuid import uuid4

from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import FastAPI
from fastapi import Header
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from pydantic import Field
from pydantic import HttpUrl
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.requests import Request

from .download import DownloadClient
from .events import ServiceEvents
from .metrics import ServiceMetrics
from .model import ModelClient
from .model import ModelPrediction


logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class PredictionResponse(BaseModel):
    id: str = Field(...)
    prediction: ModelPrediction = Field(...)


class PredictionEvent(BaseModel):
    id: str = Field(...)
    service: str = Field(...)
    environment: str = Field(...)
    caller: str = Field(...)
    image_url: str = Field(...)
    prediction: ModelPrediction = Field(...)


def create_application(
    service_name: str,
    version: str,
    environment: str,
    api_keys: Mapping[str, str],
    service_metrics: ServiceMetrics,
    service_events: ServiceEvents,
    download_client: DownloadClient,
    model_client: ModelClient,
) -> FastAPI:

    app = FastAPI(title=service_name, version=version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
        service_metrics.increment("http_error")
        return JSONResponse(
            {"error": exc.detail, "status": exc.status_code},
            status_code=exc.status_code,
        )

    async def internal_error_handler(_: Request, exc: Exception) -> JSONResponse:
        service_metrics.increment("internal_error")
        return JSONResponse({"error": "internal", "status": 500}, status_code=500)

    app.add_exception_handler(HTTPException, http_error_handler)
    app.add_exception_handler(500, internal_error_handler)

    caller_lookup = {v: k for k, v in api_keys.items()}

    def validate_api_key(x_api_key: str = Header(None)) -> str:
        if x_api_key not in caller_lookup:
            err = {"error": "The API key is invalid"}
            raise HTTPException(401, err)
        return caller_lookup[x_api_key]

    @app.get("/")
    def index() -> str:
        return f"{service_name}-v{version}"

    @app.get("/healthcheck")
    def healthcheck():
        service_metrics.increment("healthcheck")
        logger.info("Received health check!")
        return

    @app.get("/predict", response_model=PredictionResponse)
    async def predict(
        image_url: HttpUrl,
        background_tasks: BackgroundTasks,
        caller: str = Depends(validate_api_key),
    ) -> PredictionResponse:
        img = await download_client.download_image(image_url)
        model_prediction = await model_client.make_prediction(img)

        id = str(uuid4())
        prediction_resp = PredictionResponse(id=id, prediction=model_prediction)
        prediction_event = PredictionEvent(
            id=id,
            service=service_name,
            environment=environment,
            caller=caller,
            image_url=str(image_url),
            prediction=model_prediction,
        )

        background_tasks.add_task(service_events.send_event, prediction_event)

        return prediction_resp

    return app
