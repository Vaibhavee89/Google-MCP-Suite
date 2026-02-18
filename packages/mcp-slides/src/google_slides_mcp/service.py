from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from google_mcp_core.auth.manager import AuthManager
from google_mcp_core.client_factory import GoogleClientFactory
from google_mcp_core.config import AppConfig, load_config
from google_mcp_core.errors import normalize_google_error
from google_mcp_core.retry import execute_with_retry


READONLY_SCOPES = ["https://www.googleapis.com/auth/presentations.readonly"]
WRITE_SCOPES = ["https://www.googleapis.com/auth/presentations"]
DRIVE_READONLY_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
DRIVE_WRITE_SCOPES = ["https://www.googleapis.com/auth/drive.file"]


@dataclass
class SlidesService:
    config: AppConfig
    auth_manager: AuthManager
    client_factory: GoogleClientFactory

    @classmethod
    def from_config(cls, config_path: Optional[str] = None) -> "SlidesService":
        config = load_config(config_path)
        auth_manager = AuthManager(config)
        client_factory = GoogleClientFactory(auth_manager)
        return cls(config=config, auth_manager=auth_manager, client_factory=client_factory)

    def _slides_client(self, scopes: list[str]) -> Any:
        return self.client_factory.get_client("slides", "v1", scopes)

    def _drive_client(self, scopes: list[str]) -> Any:
        return self.client_factory.get_client("drive", "v3", scopes)

    def _resolve_scopes(self, extra_scopes: Optional[list[str]] = None) -> list[str]:
        return self.auth_manager.resolve_scopes("slides", extra_scopes=extra_scopes)

    def _execute(self, request: Any) -> Any:
        return execute_with_retry(request.execute)

    def get_presentation(self, presentation_id: str) -> dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._slides_client(scopes)
        try:
            request = client.presentations().get(presentationId=presentation_id)
            result = self._execute(request)
            return {
                "presentation_id": result.get("presentationId"),
                "title": result.get("title"),
                "page_size": result.get("pageSize"),
                "slides_count": len(result.get("slides", [])),
                "slides": [
                    {
                        "object_id": slide.get("objectId"),
                        "page_elements_count": len(slide.get("pageElements", [])),
                    }
                    for slide in result.get("slides", [])
                ],
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def get_slide_content(self, presentation_id: str, slide_id: str) -> dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._slides_client(scopes)
        try:
            request = client.presentations().get(presentationId=presentation_id)
            result = self._execute(request)

            for slide in result.get("slides", []):
                if slide.get("objectId") == slide_id:
                    elements = []
                    for element in slide.get("pageElements", []):
                        if "shape" in element and "text" in element["shape"]:
                            text_elements = element["shape"]["text"].get("textElements", [])
                            text_content = "".join(
                                te.get("textRun", {}).get("content", "")
                                for te in text_elements
                            )
                            elements.append({
                                "type": "text",
                                "content": text_content,
                            })
                        elif "image" in element:
                            elements.append({
                                "type": "image",
                                "content_url": element["image"].get("contentUrl"),
                            })
                    return {
                        "slide_id": slide_id,
                        "elements": elements,
                    }

            return {"error": "Slide not found"}
        except Exception as exc:
            raise normalize_google_error(exc)

    def list_presentations(self, limit: int = 25, page_token: Optional[str] = None) -> dict[str, Any]:
        scopes = self._resolve_scopes(list(dict.fromkeys(READONLY_SCOPES + DRIVE_READONLY_SCOPES)))
        drive_client = self._drive_client(scopes)
        try:
            query = "mimeType='application/vnd.google-apps.presentation'"
            request = drive_client.files().list(
                q=query,
                fields="nextPageToken, files(id, name, createdTime, modifiedTime)",
                pageSize=limit,
                pageToken=page_token,
            )
            result = self._execute(request)
            results = []
            for item in result.get("files", []):
                results.append({
                    "presentation_id": item.get("id"),
                    "name": item.get("name"),
                    "created_time": item.get("createdTime"),
                    "modified_time": item.get("modifiedTime"),
                })
            return {"presentations": results}
        except Exception as exc:
            raise normalize_google_error(exc)

    def extract_text(self, presentation_id: str) -> dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._slides_client(scopes)
        try:
            request = client.presentations().get(presentationId=presentation_id)
            result = self._execute(request)

            all_text = []
            for slide in result.get("slides", []):
                slide_text = []
                for element in slide.get("pageElements", []):
                    if "shape" in element and "text" in element["shape"]:
                        text_elements = element["shape"]["text"].get("textElements", [])
                        text_content = "".join(
                            te.get("textRun", {}).get("content", "")
                            for te in text_elements
                        )
                        if text_content.strip():
                            slide_text.append(text_content.strip())

                if slide_text:
                    all_text.append({
                        "slide_id": slide.get("objectId"),
                        "text": "\n".join(slide_text),
                    })

            return {
                "presentation_id": presentation_id,
                "title": result.get("title"),
                "slides": all_text,
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def create_slide(
        self,
        presentation_id: str,
        title: Optional[str] = None,
        insertion_index: Optional[int] = None,
        layout: str = "BLANK"
    ) -> dict[str, Any]:
        """Create a new slide in a presentation.

        Args:
            presentation_id: The presentation ID
            title: Optional title text for the slide
            insertion_index: Position to insert (None = end)
            layout: Slide layout (BLANK, TITLE, TITLE_AND_BODY, etc.)
        """
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._slides_client(scopes)
        try:
            # First get the presentation to find layout IDs
            request = client.presentations().get(presentationId=presentation_id)
            presentation = self._execute(request)

            # Find the layout master
            layout_id = None
            for master in presentation.get("masters", []):
                for layout_obj in master.get("layouts", []):
                    if layout in layout_obj.get("layoutProperties", {}).get("name", ""):
                        layout_id = layout_obj.get("objectId")
                        break
                if layout_id:
                    break

            # Build requests
            requests = []
            slide_id = f"slide_{len(presentation.get('slides', []))}"

            create_slide_request = {
                "createSlide": {
                    "objectId": slide_id,
                }
            }

            if insertion_index is not None:
                create_slide_request["createSlide"]["insertionIndex"] = insertion_index

            if layout_id:
                create_slide_request["createSlide"]["slideLayoutReference"] = {
                    "layoutId": layout_id
                }

            requests.append(create_slide_request)

            # Add title if provided
            if title:
                text_box_id = f"textbox_{slide_id}"
                requests.extend([
                    {
                        "createShape": {
                            "objectId": text_box_id,
                            "shapeType": "TEXT_BOX",
                            "elementProperties": {
                                "pageObjectId": slide_id,
                                "size": {
                                    "width": {"magnitude": 600, "unit": "PT"},
                                    "height": {"magnitude": 100, "unit": "PT"}
                                },
                                "transform": {
                                    "scaleX": 1,
                                    "scaleY": 1,
                                    "translateX": 50,
                                    "translateY": 50,
                                    "unit": "PT"
                                }
                            }
                        }
                    },
                    {
                        "insertText": {
                            "objectId": text_box_id,
                            "text": title,
                            "insertionIndex": 0
                        }
                    }
                ])

            # Execute batch update
            batch_request = client.presentations().batchUpdate(
                presentationId=presentation_id,
                body={"requests": requests}
            )
            result = self._execute(batch_request)

            return {
                "presentation_id": presentation_id,
                "slide_id": slide_id,
                "message": "Slide created successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def add_text_to_slide(
        self,
        presentation_id: str,
        slide_id: str,
        text: str,
        x: float = 50,
        y: float = 50,
        width: float = 400,
        height: float = 50
    ) -> dict[str, Any]:
        """Add a text box to an existing slide.

        Args:
            presentation_id: The presentation ID
            slide_id: The slide object ID
            text: Text content to add
            x, y: Position in points
            width, height: Size in points
        """
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._slides_client(scopes)
        try:
            text_box_id = f"textbox_{slide_id}_{hash(text) % 10000}"

            requests = [
                {
                    "createShape": {
                        "objectId": text_box_id,
                        "shapeType": "TEXT_BOX",
                        "elementProperties": {
                            "pageObjectId": slide_id,
                            "size": {
                                "width": {"magnitude": width, "unit": "PT"},
                                "height": {"magnitude": height, "unit": "PT"}
                            },
                            "transform": {
                                "scaleX": 1,
                                "scaleY": 1,
                                "translateX": x,
                                "translateY": y,
                                "unit": "PT"
                            }
                        }
                    }
                },
                {
                    "insertText": {
                        "objectId": text_box_id,
                        "text": text,
                        "insertionIndex": 0
                    }
                }
            ]

            batch_request = client.presentations().batchUpdate(
                presentationId=presentation_id,
                body={"requests": requests}
            )
            result = self._execute(batch_request)

            return {
                "presentation_id": presentation_id,
                "slide_id": slide_id,
                "text_box_id": text_box_id,
                "message": "Text added successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def update_text(
        self,
        presentation_id: str,
        shape_id: str,
        new_text: str
    ) -> dict[str, Any]:
        """Update text in an existing text box or shape.

        Args:
            presentation_id: The presentation ID
            shape_id: The shape/text box object ID
            new_text: New text content
        """
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._slides_client(scopes)
        try:
            requests = [
                {
                    "deleteText": {
                        "objectId": shape_id,
                        "textRange": {"type": "ALL"}
                    }
                },
                {
                    "insertText": {
                        "objectId": shape_id,
                        "text": new_text,
                        "insertionIndex": 0
                    }
                }
            ]

            batch_request = client.presentations().batchUpdate(
                presentationId=presentation_id,
                body={"requests": requests}
            )
            result = self._execute(batch_request)

            return {
                "presentation_id": presentation_id,
                "shape_id": shape_id,
                "message": "Text updated successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def delete_slide(
        self,
        presentation_id: str,
        slide_id: str
    ) -> dict[str, Any]:
        """Delete a slide from a presentation.

        Args:
            presentation_id: The presentation ID
            slide_id: The slide object ID to delete
        """
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._slides_client(scopes)
        try:
            requests = [
                {
                    "deleteObject": {
                        "objectId": slide_id
                    }
                }
            ]

            batch_request = client.presentations().batchUpdate(
                presentationId=presentation_id,
                body={"requests": requests}
            )
            result = self._execute(batch_request)

            return {
                "presentation_id": presentation_id,
                "slide_id": slide_id,
                "message": "Slide deleted successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def create_presentation(
        self,
        title: str
    ) -> dict[str, Any]:
        """Create a new presentation.

        Args:
            title: Title for the new presentation
        """
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._slides_client(scopes)
        try:
            presentation = {
                "title": title
            }

            request = client.presentations().create(body=presentation)
            result = self._execute(request)

            return {
                "presentation_id": result.get("presentationId"),
                "title": result.get("title"),
                "url": f"https://docs.google.com/presentation/d/{result.get('presentationId')}/edit",
                "message": "Presentation created successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)
