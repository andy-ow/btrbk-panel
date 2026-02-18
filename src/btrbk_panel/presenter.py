from __future__ import annotations
from typing import Callable, Optional, List

from .state import AppState
from .linux import list_backup_mounts, MissingDependencyError
from .btrbk import run_btrbk

Listener = Callable[[AppState], None]

class Presenter:
    def __init__(self, mnt_root: str = "/mnt") -> None:
        self._mnt_root = mnt_root
        self.state = AppState()
        self._listeners: List[Listener] = []

    def subscribe(self, fn: Listener) -> None:
        self._listeners.append(fn)
        fn(self.state)  # push initial state

    def _emit(self) -> None:
        print(f"_emit: {self.state}")
        for fn in self._listeners:
            print(f'Emiting to: ${fn}')
            fn(self.state)

    def refresh(self) -> None:
        mounts = list_backup_mounts(self._mnt_root)
        mounted = [m for m in mounts if m.mounted]
        self.state.mounts = mounts
        self.state.selected_name = mounted[0].name if mounted else None
        self.state.error = None
        self._emit()

    def select(self, mount_name: Optional[str]) -> None:
        if mount_name and any(m.name == mount_name and m.mounted for m in self.state.mounts):
            self.state.selected_name = mount_name
        else:
            self.state.selected_name = None
        self._emit()

    def _group_from_mount(self, mount_name: str) -> str:
        return mount_name.split("_backup")[0]

    def dryrun(self) -> None:
        self._run_action("dryrun")

    def run(self) -> None:
        self._run_action("run")

    def _run_action(self, action: str) -> None:
        if not self.state.selected_name:
            self.state.error = "No mount selected"
            self._emit()
            return

        group = self._group_from_mount(self.state.selected_name)

        self.state.busy = True
        self.state.error = None
        self.state.last_action = action
        self._emit()

        try:
            res = run_btrbk(action, group)
            self.state.last_result = res
            if not res.ok:
                self.state.error = f"btrbk returncode={res.returncode}"
        except MissingDependencyError as e:
            self.state.error = str(e)
        finally:
            self.state.busy = False
            self._emit()
