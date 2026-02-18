from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import random

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
    #id = f'{random.randint(0, 1000000000)}_{datetime.now()}'
    name: str          # np. "T7_backup"
    path: str          # np. "/mnt/T7_backup"
    mounted: bool      # True/False

    def __eq__(self, other):
        return self.name == other.name and self.path == other.path
