from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import FreeSimpleGUI as sg

from .presenter import Presenter
from .state import AppState

KEY_OUT = "-OUT-"
KEY_STATUS = "-STATUS-"
MAX_ROWS = 30  # ustaw na sensowną górkę


@dataclass
class ViewCtx:
    # mapowanie wiersz->nazwa mounta (albo None gdy wiersz pusty)
    row_name: list[Optional[str]]


def make_rows() -> list[list[sg.Element]]:
    rows: list[list[sg.Element]] = []
    for i in range(MAX_ROWS):
        rows.append([
            sg.Radio("", group_id="MOUNTS", key=f"-SEL-{i}-", enable_events=True, visible=False),
            sg.Text("", key=f"-NAME-{i}-", size=(18, 1), visible=False),
            sg.Text("", key=f"-STATE-{i}-", size=(12, 1), visible=False),
            sg.Text("", key=f"-PATH-{i}-", size=(50, 1), visible=False),
        ])
    return rows


def render(window: sg.Window, state: AppState, ctx: ViewCtx) -> None:
    mounts = state.mounts

    # wiersze
    for i in range(MAX_ROWS):
        if i < len(mounts):
            m = mounts[i]
            ctx.row_name[i] = m.name

            window[f"-SEL-{i}-"].update(value=(state.selected_name == m.name), visible=True, disabled=not m.mounted)
            window[f"-NAME-{i}-"].update(value=m.name, visible=True, text_color="black" if m.mounted else "gray")

            window[f"-STATE-{i}-"].update(
                value="mounted" if m.mounted else "not mounted",
                visible=True,
                text_color="green" if m.mounted else "gray",
            )

            window[f"-PATH-{i}-"].update(
                value=m.path,
                visible=True,
                text_color="black" if m.mounted else "gray",
            )
        else:
            ctx.row_name[i] = None
            window[f"-SEL-{i}-"].update(visible=False)
            window[f"-NAME-{i}-"].update(visible=False)
            window[f"-STATE-{i}-"].update(visible=False)
            window[f"-PATH-{i}-"].update(visible=False)

    # przyciski
    can_run = (state.selected_name is not None) and (not state.busy)
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


def handle_event(event: str, values: dict, presenter: Presenter, state: AppState, ctx: ViewCtx) -> None:
    if event == "Refresh":
        presenter.refresh()
        return

    if event == "Dryrun":
        presenter.dryrun()
        return

    if event == "Run":
        presenter.run()
        return

    if isinstance(event, str) and event.startswith("-SEL-"):
        # znajdź, który index jest zaznaczony
        picked: Optional[str] = None
        for i in range(MAX_ROWS):
            if values.get(f"-SEL-{i}-"):
                picked = ctx.row_name[i]
                break
        presenter.select(picked)
        return


def run_gui() -> int:
    sg.theme("SystemDefault")
    presenter = Presenter("/mnt")

    state = AppState()
    ctx = ViewCtx(row_name=[None] * MAX_ROWS)

    layout = [
        [sg.Text("Backup mounts in /mnt (name contains _backup):")],
        [sg.Column(make_rows(), scrollable=True, vertical_scroll_only=True, size=(760, 220))],
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

    # observer: tylko aktualizuje state (bez dotykania UI)
    def on_state_change(st: AppState) -> None:
        nonlocal state
        state = st

    presenter.subscribe(on_state_change)
    presenter.refresh()

    try:
        while True:
            event, values = window.read(timeout=200)  # timeout opcjonalnie, przydaje się do auto-refresh
            if event in (sg.WINDOW_CLOSED, "Exit"):
                break

            if event is not None and event != sg.TIMEOUT_EVENT:
                handle_event(event, values, presenter, state, ctx)

            # --- NA KOŃCU ITERACJI: zawsze render z aktualnego state ---
            render(window, state, ctx)

    finally:
        window.close()

    return 0
