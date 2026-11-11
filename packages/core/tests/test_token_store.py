import json
import os
import stat
import sys

import pytest
from google.oauth2.credentials import Credentials

from google_mcp_core.auth.token_store import FileTokenStore

posix_only = pytest.mark.skipif(sys.platform == "win32", reason="POSIX permission bits")


def _creds(token="access-1"):
    return Credentials(
        token=token,
        refresh_token="refresh-1",
        client_id="client-id",
        client_secret="client-secret",
        token_uri="https://oauth2.googleapis.com/token",
    )


def _mode(path):
    return stat.S_IMODE(os.stat(path).st_mode)


@posix_only
def test_token_file_is_owner_only(tmp_path):
    path = tmp_path / "tokens.json"
    FileTokenStore(str(path)).write(_creds())
    assert _mode(path) == 0o600


@posix_only
def test_permissive_umask_cannot_widen_the_file(tmp_path):
    old = os.umask(0)
    try:
        path = tmp_path / "tokens.json"
        FileTokenStore(str(path)).write(_creds())
    finally:
        os.umask(old)
    assert _mode(path) == 0o600


@posix_only
def test_existing_world_readable_token_is_tightened(tmp_path):
    path = tmp_path / "tokens.json"
    path.write_text("{}")
    os.chmod(path, 0o644)  # what an older version would have left behind
    FileTokenStore(str(path)).write(_creds())
    assert _mode(path) == 0o600


@posix_only
def test_stale_loose_temp_file_does_not_leak_permissions(tmp_path):
    path = tmp_path / "tokens.json"
    stale = tmp_path / f".tokens.json.{os.getpid()}.tmp"
    stale.write_text("old")
    os.chmod(stale, 0o666)
    FileTokenStore(str(path)).write(_creds())
    assert _mode(path) == 0o600
    assert not stale.exists()


def test_round_trip_and_no_temp_files_left(tmp_path):
    path = tmp_path / "nested" / "dir" / "tokens.json"
    store = FileTokenStore(str(path))
    store.write(_creds("access-1"))
    store.write(_creds("access-2"))  # overwrite
    loaded = store.read()
    assert loaded.token == "access-2" and loaded.refresh_token == "refresh-1"
    assert json.loads(path.read_text())["client_id"] == "client-id"
    assert [p.name for p in path.parent.iterdir()] == ["tokens.json"]


def test_read_missing_file_returns_none(tmp_path):
    assert FileTokenStore(str(tmp_path / "nope.json")).read() is None


def test_failed_write_leaves_previous_token_and_no_temp_file(tmp_path):
    path = tmp_path / "tokens.json"
    store = FileTokenStore(str(path))
    store.write(_creds("good"))

    class Broken:
        def to_json(self):
            raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        store.write(Broken())
    assert store.read().token == "good"
    assert [p.name for p in tmp_path.iterdir()] == ["tokens.json"]
