from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from .model import MountEntry, CommandResult

@dataclass
class AppState:
    mounts: List[MountEntry] = field(default_factory=list)
    selected_mount_entries: list[MountEntry] = field(default_factory=list)
    last_result: Optional[CommandResult] = None
    last_action: Optional[str] = None   # "dryrun" / "run"
    busy: bool = False
    error: Optional[str] = None
