from __future__ import annotations

from .linux import ensure_on_path, build_gui_env, run_command, MissingDependencyError
from .model import CommandResult


def run_btrbk(action: str, group: str) -> CommandResult:
    """
    action: 'dryrun' albo 'run'
    """
    ensure_on_path("pkexec")
    ensure_on_path("btrbk")
    env = build_gui_env()
    
    return run_command(["pkexec", "btrbk", action, group], env=env)
    