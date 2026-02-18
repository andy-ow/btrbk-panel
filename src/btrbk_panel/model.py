from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class CommandResult:
    argv: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def combined_output(self) -> str:
        return (self.stdout or "") + (self.stderr or "")

@dataclass(frozen=True)
class MountEntry:
    name: str          # np. "T7_backup"
    path: str          # np. "/mnt/T7_backup"
    mounted: bool      # True/False
    