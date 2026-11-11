from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from google_mcp_core.auth.manager import AuthManager
from google_mcp_core.client_factory import GoogleClientFactory
from google_mcp_core.config import AppConfig, load_config
from google_mcp_core.errors import normalize_google_error
from google_mcp_core.retry import execute_with_retry
from google_mcp_core.pagination import paginate_google_api
from google_mcp_core.safety import require_confirmation


READONLY_SCOPES = ["https://www.googleapis.com/auth/contacts.readonly"]
WRITE_SCOPES = ["https://www.googleapis.com/auth/contacts"]


@dataclass
class PeopleService:
    config: AppConfig
    auth_manager: AuthManager
    client_factory: GoogleClientFactory

    @classmethod
    def from_config(cls, config_path: Optional[str] = None) -> "PeopleService":
        config = load_config(config_path)
        auth_manager = AuthManager(config)
        client_factory = GoogleClientFactory(auth_manager)
        return cls(config=config, auth_manager=auth_manager, client_factory=client_factory)

    def _client(self, scopes: list[str]) -> Any:
        return self.client_factory.get_client("people", "v1", scopes)

    def _resolve_scopes(self, extra_scopes: Optional[list[str]] = None) -> list[str]:
        return self.auth_manager.resolve_scopes("people", extra_scopes=extra_scopes)

    def _execute(self, request: Any) -> Any:
        return execute_with_retry(request.execute)

    def list_contacts(self, limit: int = 100, page_token: Optional[str] = None) -> Dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._client(scopes)
        try:
            results = []
            
            for item in paginate_google_api(
                client.people().connections().list,
                resourceName="people/me",
                personFields="names,emailAddresses,phoneNumbers,organizations",
                pageSize=min(limit, 1000),
                pageToken=page_token,
            ):
                contact = {
                    "resource_name": item.get("resourceName"),
                }
                
                if "names" in item:
                    contact["name"] = item["names"][0].get("displayName")
                
                if "emailAddresses" in item:
                    contact["emails"] = [e.get("value") for e in item["emailAddresses"]]
                
                if "phoneNumbers" in item:
                    contact["phones"] = [p.get("value") for p in item["phoneNumbers"]]
                
                if "organizations" in item:
                    contact["organizations"] = [o.get("name") for o in item["organizations"]]
                
                results.append(contact)
            
            return {"contacts": results[:limit]}
        except Exception as exc:
            raise normalize_google_error(exc)

    def get_contact(self, resource_name: str) -> Dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._client(scopes)
        try:
            request = client.people().get(
                resourceName=resource_name,
                personFields="names,emailAddresses,phoneNumbers,addresses,organizations,biographies"
            )
            result = self._execute(request)
            
            contact = {
                "resource_name": result.get("resourceName"),
            }
            
            if "names" in result:
                contact["names"] = [n.get("displayName") for n in result["names"]]
            
            if "emailAddresses" in result:
                contact["emails"] = [e.get("value") for e in result["emailAddresses"]]
            
            if "phoneNumbers" in result:
                contact["phones"] = [p.get("value") for p in result["phoneNumbers"]]
            
            if "addresses" in result:
                contact["addresses"] = [a.get("formattedValue") for a in result["addresses"]]
            
            if "organizations" in result:
                contact["organizations"] = [
                    {"name": o.get("name"), "title": o.get("title")}
                    for o in result["organizations"]
                ]
            
            if "biographies" in result:
                contact["biography"] = result["biographies"][0].get("value")
            
            return contact
        except Exception as exc:
            raise normalize_google_error(exc)

    def search_contacts(self, query: str, limit: int = 25) -> Dict[str, Any]:
        scopes = self._resolve_scopes(READONLY_SCOPES)
        client = self._client(scopes)
        try:
            request = client.people().searchContacts(
                query=query,
                readMask="names,emailAddresses,phoneNumbers",
                pageSize=limit,
            )
            result = self._execute(request)
            
            contacts = []
            for item in result.get("results", []):
                person = item.get("person", {})
                contact = {
                    "resource_name": person.get("resourceName"),
                }
                
                if "names" in person:
                    contact["name"] = person["names"][0].get("displayName")
                
                if "emailAddresses" in person:
                    contact["emails"] = [e.get("value") for e in person["emailAddresses"]]
                
                if "phoneNumbers" in person:
                    contact["phones"] = [p.get("value") for p in person["phoneNumbers"]]
                
                contacts.append(contact)
            
            return {"contacts": contacts}
        except Exception as exc:
            raise normalize_google_error(exc)

    def create_contact(
        self,
        given_name: str,
        family_name: Optional[str] = None,
        emails: Optional[list[str]] = None,
        phones: Optional[list[str]] = None,
        confirm: bool = False,
    ) -> Dict[str, Any]:
        """Create a new contact. Requires confirm=True."""
        require_confirmation("people_create_contact", confirm)
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            contact = {}
            
            # Add name
            names = [{"givenName": given_name}]
            if family_name:
                names[0]["familyName"] = family_name
            contact["names"] = names
            
            # Add emails
            if emails:
                contact["emailAddresses"] = [{"value": email} for email in emails]
            
            # Add phones
            if phones:
                contact["phoneNumbers"] = [{"value": phone} for phone in phones]
            
            request = client.people().createContact(body=contact)
            result = self._execute(request)
            return {
                "resource_name": result.get("resourceName"),
                "message": "Contact created successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def update_contact(
        self,
        resource_name: str,
        given_name: Optional[str] = None,
        family_name: Optional[str] = None,
        emails: Optional[list[str]] = None,
        phones: Optional[list[str]] = None,
        confirm: bool = False,
    ) -> Dict[str, Any]:
        """Update an existing contact. Requires confirm=True."""
        require_confirmation("people_update_contact", confirm)
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            # Get current contact
            request = client.people().get(
                resourceName=resource_name,
                personFields="names,emailAddresses,phoneNumbers,etag"
            )
            current = self._execute(request)
            
            contact = {"etag": current.get("etag")}
            update_mask = []
            
            # Update name
            if given_name or family_name:
                names = current.get("names", [{}])[0].copy()
                if given_name:
                    names["givenName"] = given_name
                if family_name:
                    names["familyName"] = family_name
                contact["names"] = [names]
                update_mask.append("names")
            
            # Update emails
            if emails:
                contact["emailAddresses"] = [{"value": email} for email in emails]
                update_mask.append("emailAddresses")
            
            # Update phones
            if phones:
                contact["phoneNumbers"] = [{"value": phone} for phone in phones]
                update_mask.append("phoneNumbers")
            
            if not update_mask:
                return {"resource_name": resource_name, "message": "No updates provided"}
            
            request = client.people().updateContact(
                resourceName=resource_name,
                updatePersonFields=",".join(update_mask),
                body=contact
            )
            result = self._execute(request)
            return {
                "resource_name": result.get("resourceName"),
                "message": "Contact updated successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def delete_contact(self, resource_name: str, confirm: bool = False) -> Dict[str, Any]:
        """Delete a contact. Requires confirm=True."""
        require_confirmation("people_delete_contact", confirm, destructive=True)
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            request = client.people().deleteContact(resourceName=resource_name)
            self._execute(request)
            return {
                "resource_name": resource_name,
                "message": "Contact deleted successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def batch_create_contacts(self, contacts: list[Dict[str, Any]], confirm: bool = False) -> Dict[str, Any]:
        """Batch create multiple contacts. Requires confirm=True."""
        require_confirmation("people_batch_create_contacts", confirm)
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            contacts_data = []
            for contact_info in contacts:
                contact = {}
                
                # Add name
                if "given_name" in contact_info:
                    names = [{"givenName": contact_info["given_name"]}]
                    if "family_name" in contact_info:
                        names[0]["familyName"] = contact_info["family_name"]
                    contact["names"] = names
                
                # Add emails
                if "emails" in contact_info:
                    contact["emailAddresses"] = [{"value": email} for email in contact_info["emails"]]
                
                # Add phones
                if "phones" in contact_info:
                    contact["phoneNumbers"] = [{"value": phone} for phone in contact_info["phones"]]
                
                contacts_data.append({"contactPerson": contact})
            
            request = client.people().batchCreateContacts(body={"contacts": contacts_data})
            result = self._execute(request)
            created = result.get("createdPeople", [])
            return {
                "created_count": len(created),
                "resource_names": [p.get("person", {}).get("resourceName") for p in created],
                "message": f"Created {len(created)} contacts successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def create_contact_group(self, name: str, confirm: bool = False) -> Dict[str, Any]:
        """Create a new contact group. Requires confirm=True."""
        require_confirmation("people_create_contact_group", confirm)
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            body = {
                "contactGroup": {
                    "name": name
                }
            }
            request = client.contactGroups().create(body=body)
            result = self._execute(request)
            return {
                "resource_name": result.get("resourceName"),
                "name": result.get("name"),
                "message": "Contact group created successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)

    def add_contact_to_group(self, group_resource_name: str, contact_resource_name: str, confirm: bool = False) -> Dict[str, Any]:
        """Add a contact to a group. Requires confirm=True."""
        require_confirmation("people_add_contact_to_group", confirm)
        scopes = self._resolve_scopes(WRITE_SCOPES)
        client = self._client(scopes)
        try:
            body = {
                "resourceNamesToAdd": [contact_resource_name]
            }
            request = client.contactGroups().members().modify(
                resourceName=group_resource_name,
                body=body
            )
            self._execute(request)
            return {
                "group": group_resource_name,
                "contact": contact_resource_name,
                "message": "Contact added to group successfully"
            }
        except Exception as exc:
            raise normalize_google_error(exc)
