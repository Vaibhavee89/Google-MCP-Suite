from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from google_mcp_core.auth.manager import AuthManager
from google_mcp_core.client_factory import GoogleClientFactory
from google_mcp_core.config import AppConfig, load_config
from google_mcp_core.errors import normalize_google_error
from google_mcp_core.retry import execute_with_retry


READONLY_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
WRITE_SCOPES = ["https://www.googleapis.com/auth/calendar"]
EVENTS_SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


@dataclass
class CalendarService:
    config: AppConfig
    auth_manager: AuthManager
    client_factory: GoogleClientFactory

    @classmethod
    def from_config(cls, config_path: Optional[str] = None) -> "CalendarService":
        config = load_config(config_path)
        auth_manager = AuthManager(config)
        client_factory = GoogleClientFactory(auth_manager)
        return cls(config=config, auth_manager=auth_manager, client_factory=client_factory)

    def _client(self, scopes: list[str]) -> Any:
        return self.client_factory.get_client("calendar", "v3", scopes)

    def _resolve_scopes(self, extra_scopes: Optional[list[str]] = None) -> list[str]:
        return self.auth_manager.resolve_scopes("calendar", extra_scopes=extra_scopes)

    def _execute(self, request: Any) -> Any:
        return execute_with_retry(request.execute)

    def search_events(
        self,
        calendar_id: str = "primary",
        query: Optional[str] = None,
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        limit: int = 25,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._client(scopes)
        try:
            request = client.events().list(
                calendarId=calendar_id,
                q=query,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=limit,
                pageToken=page_token,
                singleEvents=True,
                orderBy="startTime",
            )
            response = self._execute(request)
            return {
                "items": response.get("items", []),
                "next_page_token": response.get("nextPageToken"),
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def get_event(self, event_id: str, calendar_id: str = "primary") -> Dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._client(scopes)
        try:
            request = client.events().get(calendarId=calendar_id, eventId=event_id)
            return self._execute(request)
        except Exception as exc:
            raise normalize_google_error(exc)

    def create_event(
        self,
        summary: str,
        start_time: str,
        end_time: str,
        calendar_id: str = "primary",
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[list[str]] = None,
        timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """Create a calendar event."""
        scopes = self._resolve_scopes(EVENTS_SCOPES)
        client = self._client(scopes)
        try:
            event = {
                "summary": summary,
                "start": {"dateTime": start_time, "timeZone": timezone},
                "end": {"dateTime": end_time, "timeZone": timezone},
            }
            if description:
                event["description"] = description
            if location:
                event["location"] = location
            if attendees:
                event["attendees"] = [{"email": email} for email in attendees]
            
            request = client.events().insert(calendarId=calendar_id, body=event)
            result = self._execute(request)
            return {
                "id": result.get("id"),
                "summary": result.get("summary"),
                "start": result.get("start"),
                "end": result.get("end"),
                "html_link": result.get("htmlLink"),
                "message": "Event created successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def update_event(
        self,
        event_id: str,
        calendar_id: str = "primary",
        summary: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """Update an existing calendar event."""
        scopes = self._resolve_scopes(EVENTS_SCOPES)
        client = self._client(scopes)
        try:
            # Get current event
            request = client.events().get(calendarId=calendar_id, eventId=event_id)
            event = self._execute(request)
            
            # Update fields
            if summary is not None:
                event["summary"] = summary
            if description is not None:
                event["description"] = description
            if location is not None:
                event["location"] = location
            if start_time is not None:
                event["start"] = {"dateTime": start_time, "timeZone": timezone}
            if end_time is not None:
                event["end"] = {"dateTime": end_time, "timeZone": timezone}
            
            request = client.events().update(calendarId=calendar_id, eventId=event_id, body=event)
            result = self._execute(request)
            return {
                "id": result.get("id"),
                "summary": result.get("summary"),
                "message": "Event updated successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def delete_event(self, event_id: str, calendar_id: str = "primary") -> Dict[str, Any]:
        """Delete a calendar event."""
        scopes = self._resolve_scopes(EVENTS_SCOPES)
        client = self._client(scopes)
        try:
            request = client.events().delete(calendarId=calendar_id, eventId=event_id)
            self._execute(request)
            return {
                "event_id": event_id,
                "message": "Event deleted successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def list_calendars(self) -> Dict[str, Any]:
        """List all calendars."""
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._client(scopes)
        try:
            request = client.calendarList().list()
            result = self._execute(request)
            return {
                "calendars": [
                    {
                        "id": cal.get("id"),
                        "summary": cal.get("summary"),
                        "description": cal.get("description"),
                        "primary": cal.get("primary", False)
                    }
                    for cal in result.get("items", [])
                ]
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def create_calendar(self, summary: str, description: Optional[str] = None, timezone: str = "UTC") -> Dict[str, Any]:
        """Create a new calendar."""
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            calendar = {
                "summary": summary,
                "timeZone": timezone
            }
            if description:
                calendar["description"] = description
            
            request = client.calendars().insert(body=calendar)
            result = self._execute(request)
            return {
                "id": result.get("id"),
                "summary": result.get("summary"),
                "message": "Calendar created successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def add_attendees(
        self,
        event_id: str,
        attendees: list[str],
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Add attendees to an existing event."""
        scopes = self._resolve_scopes(EVENTS_SCOPES)
        client = self._client(scopes)
        try:
            request = client.events().get(calendarId=calendar_id, eventId=event_id)
            event = self._execute(request)
            
            current_attendees = event.get("attendees", [])
            new_attendees = [{"email": email} for email in attendees]
            event["attendees"] = current_attendees + new_attendees
            
            request = client.events().update(calendarId=calendar_id, eventId=event_id, body=event)
            result = self._execute(request)
            return {
                "id": result.get("id"),
                "attendees": result.get("attendees", []),
                "message": "Attendees added successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def quick_add_event(self, text: str, calendar_id: str = "primary") -> Dict[str, Any]:
        """Quick add event using natural language."""
        scopes = self._resolve_scopes(EVENTS_SCOPES)
        client = self._client(scopes)
        try:
            request = client.events().quickAdd(calendarId=calendar_id, text=text)
            result = self._execute(request)
            return {
                "id": result.get("id"),
                "summary": result.get("summary"),
                "start": result.get("start"),
                "end": result.get("end"),
                "message": "Event created successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)
