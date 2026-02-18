from __future__ import annotations

import os
import shutil
import subprocess
from typing import Mapping

from .model import CommandResult, MountEntry


class MissingDependencyError(RuntimeError):
    pass


def ensure_on_path(cmd: str) -> None:
    if shutil.which(cmd) is None:
        raise MissingDependencyError(f"Brak {cmd} w PATH")


def build_gui_env(base: Mapping[str, str] | None = None) -> dict[str, str]:
    """
    pkexec czasem potrzebuje sensownego XAUTHORITY w sesjach graficznych.
    """
    env = dict(base or os.environ)

    if "XAUTHORITY" not in env and env.get("HOME"):
        env["XAUTHORITY"] = os.path.join(env["HOME"], ".Xauthority")

    return env


def run_command(argv: list[str], *, env: dict[str, str] | None = None) -> CommandResult:
    ensure_on_path(argv[0])
    cp = subprocess.run(
        argv,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    return CommandResult(
        argv=list(argv),
        returncode=cp.returncode,
        stdout=cp.stdout or "",
        stderr=cp.stderr or "",
    )

def list_backup_mounts(mnt_root: str = "/mnt") -> list[MountEntry]:
    out: list[MountEntry] = []
    try:
        with os.scandir(mnt_root) as it:
            for e in it:
                if not e.is_dir(follow_symlinks=False):
                    continue
                if "_backup" not in e.name:
                    continue
                path = os.path.join(mnt_root, e.name)
                out.append(MountEntry(name=e.name, path=path, mounted=is_mounted(path)))
    except FileNotFoundError:
        # /mnt nie istnieje? raczej nie, ale niech będzie
        return []
    return sorted(out, key=lambda x: x.name.lower())


def is_mounted(target_path: str) -> bool:
    """
    findmnt zwraca kod 0 jeśli target jest zamontowany.
    """
    cp = run_command(["findmnt", "-rn", "--mountpoint", target_path])
    return cp.returncode == 0
