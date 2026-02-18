from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import FreeSimpleGUI as sg

from btrbk_panel.model import MountEntry

from .presenter import Presenter
from .state import AppState

KEY_OUT = "-OUT-"
KEY_STATUS = "-STATUS-"

def get_selected_mounts(values: dict, mounts: list[MountEntry]) -> list[MountEntry]:
    return [m for m in mounts if values.get(m)]

def make_rows(mounts: list[MountEntry], selected: list[MountEntry]) -> list[list[sg.Element]]:
    rows: list[list[sg.Element]] = []
    for m in mounts:
        is_sel = (m.name in selected) #(selected == m)
        status_color = "green" if m.mounted else "gray"
        status_text = "mounted" if m.mounted else "not mounted"
        rows.append(
            [
                sg.Checkbox(
                    m.name,
                    key=m, #f"-MOUNT-{m.name}-",
                    default=is_sel,
                    enable_events=True,
                    disabled=not m.mounted,
                    metadata=m,
                ),
                sg.Text(status_text, text_color=status_color, pad=(6, 0)),
                sg.Text(m.path, text_color="black" if m.mounted else "gray", pad=(6, 0)),
            ]
        )
    if not rows:
        rows = [[sg.Text("Brak katalogów *_backup w /mnt", text_color="gray")]]
    return rows

def create_window(mounts: list[MountEntry], selected: list[MountEntry]) -> sg.Window:

    layout = [
        [sg.Text("Backup mounts in /mnt (name contains _backup):")],
        [sg.Column(make_rows(mounts, selected), key='column', scrollable=True, vertical_scroll_only=True, size=(760, 220))],
        [
            sg.Button("Refresh"),
            sg.Button("Dryrun", key="Dryrun", disabled=True),
            sg.Button("Run", key="Run", disabled=True),
            sg.Button("Exit"),
            sg.Text("", key=KEY_STATUS, expand_x=True),
        ],
        [sg.Multiline(key=KEY_OUT, size=(110, 28), autoscroll=True, disabled=True)],
    ]

    window = sg.Window("btrbk-panel", layout, finalize=True)
    return window


def render(window: sg.Window, state: AppState) -> None:
    mounts = state.mounts
    if not all([m in window.AllKeysDict for m in mounts]):
        #window = create_window(state.mounts, state.selected_mount_entries)
        window['column'].update(make_rows(mounts, state.selected_mount_entries))
    for m in mounts:
        window[m].update(value=(m in state.selected_mount_entries), visible=True, disabled=not m.mounted)
    # przyciski
    can_run = (len(state.selected_mount_entries) != 0) and (not state.busy)
    window["Dryrun"].update(disabled=not can_run)
    window["Run"].update(disabled=not can_run)

    # output
    if state.last_result is not None:
        window[KEY_OUT].update(state.last_result.combined_output(), disabled=False)

    # status / error
    if state.busy:
        window[KEY_STATUS].update("Working...", text_color="gray")
    elif state.error:
        window[KEY_STATUS].update(state.error, text_color="red")
    else:
        window[KEY_STATUS].update("", text_color="gray")
    
    return


def handle_event(event: str, values: dict, presenter: Presenter, state: AppState) -> None:
    if event == "Refresh":
        presenter.refresh()
        return

    if event == "Dryrun":
        presenter.dryrun()
        return

    if event == "Run":
        presenter.run()
        return

    if isinstance(event, MountEntry):
        selected = get_selected_mounts(values, state.mounts)
        presenter.select(selected)
        return


def run_gui() -> int:
    sg.theme("SystemDefault")
    presenter = Presenter("/mnt")

    state = AppState()
    state_has_changed = False
    # observer: tylko aktualizuje state (bez dotykania UI)
    def on_state_change(st: AppState) -> None:
        nonlocal state
        nonlocal state_has_changed
        state = st
        state_has_changed = True

    presenter.subscribe(on_state_change)
    presenter.refresh()
    window = create_window(state.mounts, state.selected_mount_entries)

    try:
        while True:
            event, values = window.read(timeout=200)  # timeout opcjonalnie, przydaje się do auto-refresh
            if event in (sg.WINDOW_CLOSED, "Exit"):
                break

            if event is not None and event != sg.TIMEOUT_EVENT:
                handle_event(event, values, presenter, state)

            # --- NA KOŃCU ITERACJI: zawsze render z aktualnego state ---
            if state_has_changed: render(window, state)

    finally:
        window.close()

    return 0
