from __future__ import annotations

from typing import Any, Optional

from google.cloud import pubsub_v1
from google_mcp_core.auth.manager import AuthManager
from google_mcp_core.config import load_config
from google_mcp_core.errors import handle_google_api_error


class PubSubService:
    def __init__(self, auth_manager: AuthManager, project_id: Optional[str] = None):
        self.auth = auth_manager
        self.config = auth_manager.config
        self.project_id = project_id
        self._publisher = None
        self._subscriber = None

    @classmethod
    def from_config(cls, config_path: Optional[str] = None, project_id: Optional[str] = None) -> PubSubService:
        config = load_config(config_path)
        auth_manager = AuthManager(config)
        return cls(auth_manager, project_id)

    def _get_publisher(self):
        if not self._publisher:
            service_config = self.config.services.get("pubsub")
            scopes = service_config.scopes if service_config else [
                "https://www.googleapis.com/auth/pubsub"
            ]
            creds = self.auth.get_credentials("pubsub", scopes)
            self._publisher = pubsub_v1.PublisherClient(credentials=creds)
        return self._publisher

    def _get_subscriber(self):
        if not self._subscriber:
            service_config = self.config.services.get("pubsub")
            scopes = service_config.scopes if service_config else [
                "https://www.googleapis.com/auth/pubsub"
            ]
            creds = self.auth.get_credentials("pubsub", scopes)
            self._subscriber = pubsub_v1.SubscriberClient(credentials=creds)
        return self._subscriber

    @handle_google_api_error
    def list_topics(self, limit: int = 50) -> dict[str, Any]:
        publisher = self._get_publisher()
        project_path = f"projects/{self.project_id}"
        
        topics = []
        for topic in publisher.list_topics(request={"project": project_path}):
            topics.append({
                "name": topic.name,
                "labels": dict(topic.labels),
            })
            if len(topics) >= limit:
                break
        
        return {"topics": topics}

    @handle_google_api_error
    def get_topic(self, topic_name: str) -> dict[str, Any]:
        publisher = self._get_publisher()
        topic_path = f"projects/{self.project_id}/topics/{topic_name}"
        topic = publisher.get_topic(request={"topic": topic_path})
        
        return {
            "name": topic.name,
            "labels": dict(topic.labels),
        }

    @handle_google_api_error
    def list_subscriptions(self, limit: int = 50) -> dict[str, Any]:
        subscriber = self._get_subscriber()
        project_path = f"projects/{self.project_id}"
        
        subscriptions = []
        for sub in subscriber.list_subscriptions(request={"project": project_path}):
            subscriptions.append({
                "name": sub.name,
                "topic": sub.topic,
                "ack_deadline_seconds": sub.ack_deadline_seconds,
            })
            if len(subscriptions) >= limit:
                break
        
        return {"subscriptions": subscriptions}

    @handle_google_api_error
    def get_subscription(self, subscription_name: str) -> dict[str, Any]:
        subscriber = self._get_subscriber()
        sub_path = f"projects/{self.project_id}/subscriptions/{subscription_name}"
        sub = subscriber.get_subscription(request={"subscription": sub_path})
        
        return {
            "name": sub.name,
            "topic": sub.topic,
            "ack_deadline_seconds": sub.ack_deadline_seconds,
            "message_retention_duration": str(sub.message_retention_duration),
        }
