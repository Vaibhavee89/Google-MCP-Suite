from __future__ import annotations

import json
import os
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
        """Write the token file readable by the owner only (0600).

        The data goes to a temp file created with mode 0600 and is then renamed over the
        target, so it is never on disk with wider permissions, and a pre-existing file with
        looser permissions is replaced rather than reused.
        """
        path = self._resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(credentials.to_json())
                fh.flush()
                os.fsync(fh.fileno())
            os.chmod(tmp, 0o600)  # in case a stale temp file already existed with other bits
            os.replace(tmp, path)
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise
