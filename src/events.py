import logging

# TODO: pub/sub into big query or something?

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class ServiceEvents:
    def __init__(self):
        pass

    async def send_event(self, event):
        logger.info(f"Storing event\n{event.dict()}")
