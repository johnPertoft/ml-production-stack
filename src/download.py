import asyncio
import io
import logging

import aiohttp
from PIL import Image
from pydantic import HttpUrl
from starlette.exceptions import HTTPException

from .metrics import ServiceMetrics


logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class DownloadClient:
    def __init__(self, service_metrics: ServiceMetrics):
        self._service_metrics = service_metrics

    async def download_image(self, url: HttpUrl) -> Image:
        # TODO: Add timeout, file size limit.
        # TODO: Add retry functionality.
        # TODO: Add metrics, time to download?

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            try:
                async with session.get(url) as resp:
                    data = await resp.read()
                    img = Image.open(io.BytesIO(data))
                    return img
            except aiohttp.ClientResponseError as e:
                logger.warning(f"Failed to download image {url} with {e}")
                self._service_metrics.increment("download.failures")
                raise HTTPException(400, "Unable to get image")
            except asyncio.TimeoutError as e:
                logger.warning(f"Timeout when downloading image {url}")
                self._service_metrics.increment("download.timeouts")
                raise HTTPException(408, "Timeout getting image")
