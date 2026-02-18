from __future__ import annotations

import os
import shutil
import subprocess
import FreeSimpleGUI as sg


def run_btrbk(group: str) -> subprocess.CompletedProcess[str]:
    if not shutil.which("pkexec"):
        return subprocess.CompletedProcess(
                args=[],
                returncode=127,
                stdout="",
                stderr="Brak pkexec (zainstaluj polkit)."
        )

    env = os.environ.copy()
    if "XAUTHORITY" not in env and "HOME" in env:
        env["XAUTHORITY"] = os.path.join(env["HOME"], ".Xauthority")

    return subprocess.run(
        ["pkexec", "btrbk", "dryrun", group],
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


def main() -> int:
    sg.theme("SystemDefault")

    layout = [
        [sg.Text("btrbk group:"), sg.Input(key="-GROUP-", size=(30, 1))],
        [sg.Button("Dryrun", bind_return_key=True), sg.Button("Exit")],
        [sg.Multiline(key="-OUT-", size=(100, 25), autoscroll=True, disabled=True)],
    ]

    window = sg.Window("btrbk-panel", layout, finalize=True)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break
        if event == "Dryrun":
            group = (values.get("-GROUP-") or "").strip()
            if not group:
                sg.popup_error("Podaj nazwę group")
                continue

            window["-OUT-"].update("Running...\n", disabled=False)
            cp = run_btrbk(group)

            out = (cp.stdout or "") + (cp.stderr or "")
            window["-OUT-"].update(out, disabled=False)

            if cp.returncode != 0:
                sg.popup_error(f"btrbk returncode={cp.returncode}")

    window.close()
    return 0

