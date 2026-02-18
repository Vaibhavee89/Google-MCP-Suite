from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from google.oauth2.credentials import Credentials


class TokenStore:
    def read(self) -> Optional[Credentials]:
        raise NotImplementedError

    def write(self, credentials: Credentials) -> None:
        raise NotImplementedError


@dataclass
class FileTokenStore(TokenStore):
    path: str

    def _resolve(self) -> Path:
        return Path(self.path).expanduser()

    def read(self) -> Optional[Credentials]:
        path = self._resolve()
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return Credentials.from_authorized_user_info(data)

    def write(self, credentials: Credentials) -> None:
        path = self._resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(credentials.to_json(), encoding="utf-8")
