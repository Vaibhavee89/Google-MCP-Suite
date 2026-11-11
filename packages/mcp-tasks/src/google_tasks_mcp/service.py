from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from google_mcp_core.auth.manager import AuthManager
from google_mcp_core.client_factory import GoogleClientFactory
from google_mcp_core.config import AppConfig, load_config
from google_mcp_core.errors import normalize_google_error
from google_mcp_core.retry import execute_with_retry
from google_mcp_core.pagination import paginate_google_api
from google_mcp_core.safety import require_confirmation


READONLY_SCOPES = ["https://www.googleapis.com/auth/tasks.readonly"]
WRITE_SCOPES = ["https://www.googleapis.com/auth/tasks"]


@dataclass
class TasksService:
    config: AppConfig
    auth_manager: AuthManager
    client_factory: GoogleClientFactory

    @classmethod
    def from_config(cls, config_path: Optional[str] = None) -> "TasksService":
        config = load_config(config_path)
        auth_manager = AuthManager(config)
        client_factory = GoogleClientFactory(auth_manager)
        return cls(config=config, auth_manager=auth_manager, client_factory=client_factory)

    def _tasks_client(self, scopes: list[str]) -> Any:
        return self.client_factory.get_client("tasks", "v1", scopes)

    def _resolve_scopes(self, extra_scopes: Optional[list[str]] = None) -> list[str]:
        return self.auth_manager.resolve_scopes("tasks", extra_scopes=extra_scopes)

    def _execute(self, request: Any) -> Any:
        return execute_with_retry(request.execute)

    def list_task_lists(self, limit: int = 50) -> dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._tasks_client(scopes)
        try:
            results = []
            for item in paginate_google_api(
                client.tasklists().list,
                maxResults=limit,
            ):
                results.append({
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "updated": item.get("updated"),
                })
            return {"task_lists": results[:limit]}
        except Exception as exc:
            raise normalize_google_error(exc)

    def list_tasks(self, tasklist_id: str, limit: int = 100, show_completed: bool = False) -> dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._tasks_client(scopes)
        try:
            results = []
            for item in paginate_google_api(
                client.tasks().list,
                tasklist=tasklist_id,
                maxResults=limit,
                showCompleted=show_completed,
            ):
                results.append({
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "status": item.get("status"),
                    "due": item.get("due"),
                    "notes": item.get("notes"),
                    "updated": item.get("updated"),
                })
            return {
                "tasklist_id": tasklist_id,
                "tasks": results[:limit],
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def get_task(self, tasklist_id: str, task_id: str) -> dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._tasks_client(scopes)
        try:
            request = client.tasks().get(tasklist=tasklist_id, task=task_id)
            result = self._execute(request)
            return {
                "id": result.get("id"),
                "title": result.get("title"),
                "status": result.get("status"),
                "due": result.get("due"),
                "notes": result.get("notes"),
                "updated": result.get("updated"),
                "completed": result.get("completed"),
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def create_task(
        self,
        tasklist_id: str,
        title: str,
        notes: Optional[str] = None,
        due: Optional[str] = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Create a new task in a task list. Requires confirm=True."""
        require_confirmation("tasks_create_task", confirm)
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._tasks_client(scopes)
        try:
            task_body = {"title": title}
            if notes:
                task_body["notes"] = notes
            if due:
                task_body["due"] = due
            
            request = client.tasks().insert(tasklist=tasklist_id, body=task_body)
            result = self._execute(request)
            return {
                "id": result.get("id"),
                "title": result.get("title"),
                "status": result.get("status"),
                "message": "Task created successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def update_task(
        self,
        tasklist_id: str,
        task_id: str,
        title: Optional[str] = None,
        notes: Optional[str] = None,
        due: Optional[str] = None,
        status: Optional[str] = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Update an existing task. Requires confirm=True."""
        require_confirmation("tasks_update_task", confirm)
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._tasks_client(scopes)
        try:
            # Get current task
            request = client.tasks().get(tasklist=tasklist_id, task=task_id)
            task = self._execute(request)
            
            # Update fields
            if title is not None:
                task["title"] = title
            if notes is not None:
                task["notes"] = notes
            if due is not None:
                task["due"] = due
            if status is not None:
                task["status"] = status
            
            request = client.tasks().update(tasklist=tasklist_id, task=task_id, body=task)
            result = self._execute(request)
            return {
                "id": result.get("id"),
                "title": result.get("title"),
                "status": result.get("status"),
                "message": "Task updated successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def delete_task(self, tasklist_id: str, task_id: str, confirm: bool = False) -> dict[str, Any]:
        """Delete a task. Requires confirm=True."""
        require_confirmation("tasks_delete_task", confirm, destructive=True)
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._tasks_client(scopes)
        try:
            request = client.tasks().delete(tasklist=tasklist_id, task=task_id)
            self._execute(request)
            return {
                "tasklist_id": tasklist_id,
                "task_id": task_id,
                "message": "Task deleted successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def complete_task(self, tasklist_id: str, task_id: str, confirm: bool = False) -> dict[str, Any]:
        """Mark a task as completed. Requires confirm=True."""
        require_confirmation("tasks_complete_task", confirm)
        return self.update_task(tasklist_id, task_id, status="completed", confirm=confirm)

    def create_task_list(self, title: str, confirm: bool = False) -> dict[str, Any]:
        """Create a new task list. Requires confirm=True."""
        require_confirmation("tasks_create_task_list", confirm)
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._tasks_client(scopes)
        try:
            request = client.tasklists().insert(body={"title": title})
            result = self._execute(request)
            return {
                "id": result.get("id"),
                "title": result.get("title"),
                "message": "Task list created successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def delete_task_list(self, tasklist_id: str, confirm: bool = False) -> dict[str, Any]:
        """Delete a task list. Requires confirm=True."""
        require_confirmation("tasks_delete_task_list", confirm, destructive=True)
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._tasks_client(scopes)
        try:
            request = client.tasklists().delete(tasklist=tasklist_id)
            self._execute(request)
            return {
                "tasklist_id": tasklist_id,
                "message": "Task list deleted successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def move_task(
        self,
        tasklist_id: str,
        task_id: str,
        parent: Optional[str] = None,
        previous: Optional[str] = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Move a task to a different position. Requires confirm=True."""
        require_confirmation("tasks_move_task", confirm)
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._tasks_client(scopes)
        try:
            request = client.tasks().move(
                tasklist=tasklist_id,
                task=task_id,
                parent=parent,
                previous=previous
            )
            result = self._execute(request)
            return {
                "id": result.get("id"),
                "message": "Task moved successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)
