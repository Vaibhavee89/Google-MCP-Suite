from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from google_mcp_core.auth.manager import AuthManager
from google_mcp_core.client_factory import GoogleClientFactory
from google_mcp_core.config import AppConfig, load_config
from google_mcp_core.errors import normalize_google_error
from google_mcp_core.retry import execute_with_retry


READONLY_SCOPES = ["https://www.googleapis.com/auth/forms.responses.readonly"]
BODY_READONLY_SCOPES = ["https://www.googleapis.com/auth/forms.body.readonly"]
WRITE_SCOPES = ["https://www.googleapis.com/auth/forms.body"]


@dataclass
class FormsService:
    config: AppConfig
    auth_manager: AuthManager
    client_factory: GoogleClientFactory

    @classmethod
    def from_config(cls, config_path: Optional[str] = None) -> "FormsService":
        config = load_config(config_path)
        auth_manager = AuthManager(config)
        client_factory = GoogleClientFactory(auth_manager)
        return cls(config=config, auth_manager=auth_manager, client_factory=client_factory)

    def _client(self, scopes: list[str]) -> Any:
        return self.client_factory.get_client("forms", "v1", scopes)

    def _resolve_scopes(self, extra_scopes: Optional[list[str]] = None) -> list[str]:
        return self.auth_manager.resolve_scopes("forms", extra_scopes=extra_scopes)

    def _execute(self, request: Any) -> Any:
        return execute_with_retry(request.execute)

    def get_form(self, form_id: str) -> Dict[str, Any]:
        scopes = self._resolve_scopes(BODY_READONLY_SCOPES)
        client = self._client(scopes)
        try:
            request = client.forms().get(formId=form_id)
            result = self._execute(request)
            return {
                "form_id": result.get("formId"),
                "title": result.get("info", {}).get("title"),
                "description": result.get("info", {}).get("description"),
                "items_count": len(result.get("items", [])),
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def list_responses(self, form_id: str, limit: int = 50) -> Dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._client(scopes)
        try:
            request = client.forms().responses().list(formId=form_id, pageSize=limit)
            result = self._execute(request)
            responses = result.get("responses", [])
            
            return {
                "form_id": form_id,
                "responses_count": len(responses),
                "responses": [
                    {
                        "response_id": r.get("responseId"),
                        "create_time": r.get("createTime"),
                        "last_submitted_time": r.get("lastSubmittedTime"),
                    }
                    for r in responses
                ],
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def get_response(self, form_id: str, response_id: str) -> Dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._client(scopes)
        try:
            request = client.forms().responses().get(formId=form_id, responseId=response_id)
            result = self._execute(request)
            return {
                "response_id": result.get("responseId"),
                "create_time": result.get("createTime"),
                "answers": result.get("answers", {}),
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def create_form(self, title: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new Google Form."""
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            body = {
                "info": {
                    "title": title
                }
            }
            if description:
                body["info"]["description"] = description
            
            request = client.forms().create(body=body)
            result = self._execute(request)
            return {
                "form_id": result.get("formId"),
                "title": result.get("info", {}).get("title"),
                "responder_uri": result.get("responderUri"),
                "message": "Form created successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def add_text_question(
        self,
        form_id: str,
        question: str,
        required: bool = False,
        paragraph: bool = False
    ) -> Dict[str, Any]:
        """Add a text question to a form."""
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            question_item = {
                "title": question,
                "questionItem": {
                    "question": {
                        "required": required,
                        "textQuestion": {
                            "paragraph": paragraph
                        }
                    }
                }
            }
            
            body = {
                "requests": [{
                    "createItem": {
                        "item": question_item,
                        "location": {"index": 0}
                    }
                }]
            }
            
            request = client.forms().batchUpdate(formId=form_id, body=body)
            result = self._execute(request)
            return {
                "form_id": form_id,
                "message": "Text question added successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def add_multiple_choice_question(
        self,
        form_id: str,
        question: str,
        options: list[str],
        required: bool = False
    ) -> Dict[str, Any]:
        """Add a multiple choice question to a form."""
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            question_item = {
                "title": question,
                "questionItem": {
                    "question": {
                        "required": required,
                        "choiceQuestion": {
                            "type": "RADIO",
                            "options": [{"value": opt} for opt in options]
                        }
                    }
                }
            }
            
            body = {
                "requests": [{
                    "createItem": {
                        "item": question_item,
                        "location": {"index": 0}
                    }
                }]
            }
            
            request = client.forms().batchUpdate(formId=form_id, body=body)
            result = self._execute(request)
            return {
                "form_id": form_id,
                "message": "Multiple choice question added successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def add_checkbox_question(
        self,
        form_id: str,
        question: str,
        options: list[str],
        required: bool = False
    ) -> Dict[str, Any]:
        """Add a checkbox question to a form."""
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            question_item = {
                "title": question,
                "questionItem": {
                    "question": {
                        "required": required,
                        "choiceQuestion": {
                            "type": "CHECKBOX",
                            "options": [{"value": opt} for opt in options]
                        }
                    }
                }
            }
            
            body = {
                "requests": [{
                    "createItem": {
                        "item": question_item,
                        "location": {"index": 0}
                    }
                }]
            }
            
            request = client.forms().batchUpdate(formId=form_id, body=body)
            result = self._execute(request)
            return {
                "form_id": form_id,
                "message": "Checkbox question added successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def update_form_info(
        self,
        form_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update form title and description."""
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            requests = []
            
            if title:
                requests.append({
                    "updateFormInfo": {
                        "info": {"title": title},
                        "updateMask": "title"
                    }
                })
            
            if description:
                requests.append({
                    "updateFormInfo": {
                        "info": {"description": description},
                        "updateMask": "description"
                    }
                })
            
            if not requests:
                return {"form_id": form_id, "message": "No updates provided"}
            
            body = {"requests": requests}
            request = client.forms().batchUpdate(formId=form_id, body=body)
            result = self._execute(request)
            return {
                "form_id": form_id,
                "message": "Form info updated successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def delete_item(self, form_id: str, item_id: str) -> Dict[str, Any]:
        """Delete a question/item from a form."""
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            body = {
                "requests": [{
                    "deleteItem": {
                        "location": {"index": 0}
                    }
                }]
            }
            
            request = client.forms().batchUpdate(formId=form_id, body=body)
            result = self._execute(request)
            return {
                "form_id": form_id,
                "message": "Item deleted successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def update_settings(
        self,
        form_id: str,
        collect_email: Optional[bool] = None,
        allow_response_edits: Optional[bool] = None,
        quiz_mode: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Update form settings."""
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            requests = []
            
            if collect_email is not None:
                requests.append({
                    "updateSettings": {
                        "settings": {
                            "quizSettings": {"isQuiz": quiz_mode} if quiz_mode is not None else {}
                        },
                        "updateMask": "quizSettings.isQuiz" if quiz_mode is not None else ""
                    }
                })
            
            if not requests:
                return {"form_id": form_id, "message": "No settings to update"}
            
            body = {"requests": requests}
            request = client.forms().batchUpdate(formId=form_id, body=body)
            result = self._execute(request)
            return {
                "form_id": form_id,
                "message": "Form settings updated successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)
