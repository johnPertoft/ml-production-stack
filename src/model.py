from typing import List
from typing import Tuple

import grpc
import numpy as np
from PIL import Image
from pydantic import BaseModel
from pydantic import Field
import tensorflow as tf
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc

from .labels import IMAGENET_LABELS


class CategoryPrediction(BaseModel):
    category: str = Field(...)
    probability: float = Field(..., ge=0.0, le=1.0)


class ModelPrediction(BaseModel):
    predictions: List[CategoryPrediction] = Field(
        ...,
        title="Top model predictions.",
        description="List of top model predictions.",
    )


class ModelClient:
    def __init__(self, host: str, grpc_port: int, http_port: int):
        self._host = host
        self._grpc_port = grpc_port
        self._http_port = http_port
        self._timeout = 10

    async def make_prediction(self, img: Image) -> ModelPrediction:
        # Served model: https://tfhub.dev/tensorflow/resnet_50/classification/1

        with grpc.insecure_channel(f"{self._host}:{self._grpc_port}") as channel:
            stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
            request = predict_pb2.PredictRequest()
            request.model_spec.name = "model"
            request.model_spec.signature_name = "serving_default"

            img = img.resize((224, 224))
            img = np.array(img)[..., :3]
            img = img / 255.0
            img = img[None, ...]
            inputs = tf.make_tensor_proto(img, shape=img.shape, dtype=tf.float32)
            request.inputs["input_1"].CopyFrom(inputs)

            result = stub.Predict(request, self._timeout)
            probs = result.outputs["activation_49"].float_val
            probs = np.array(probs)

            k = 3
            top_k = probs.argsort()[-k:][::-1]
            top_k_probs = probs[top_k]

            # TODO: Potentially some mismatch in labels? Adding 1 to class index.
            category_predictions = [
                CategoryPrediction(category=f"{IMAGENET_LABELS[c + 1]}", probability=p)
                for c, p in zip(top_k, top_k_probs)
            ]
            model_prediction = ModelPrediction(predictions=category_predictions)

            return model_prediction
