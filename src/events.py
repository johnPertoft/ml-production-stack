from pydantic import BaseModel

from google.cloud import pubsub_v1


class ServiceEvents:
    def __init__(self, topic_name):
        self._topic_name = topic_name
        self._publisher_client = pubsub_v1.PublisherClient()
        # self._publisher_client.create_topic(topic_name)

    async def send_event(self, event: BaseModel):
        self._publisher_client.publish(self._topic_name, event.json().encode("ascii"))
