from __future__ import annotations

from pathlib import Path
from typing import Callable
import argparse
import time

try:
    from tools.poke_gm80 import load_game
    from tools.poke_zh_patch import patch_dialog_bitmap_runtime
    from tools.patch_cheat_menu import patch_cheat_features
except ModuleNotFoundError:
    from poke_gm80 import load_game
    from poke_zh_patch import patch_dialog_bitmap_runtime
    from patch_cheat_menu import patch_cheat_features


DEFAULT_SOURCE_EXE = "Proyecto Reloaded The Last Beta 1.9.1 Full.exe"
DEFAULT_OUTPUT_EXE = "Proyecto Reloaded The Last Beta 1.9.1 Full.zh-cn.uifix.exe"
MOVE_LAYOUT_NEEDLES = (
    'ex(7028,ex(9935,txt_pb,ex(7818,PB!="0",PB,"--")),264,45+16*i,c_white,fa_right,1);',
    'ex(7028,ex(9935,txt_pp,PP),313,45+16*i,c_white,fa_right,1);',
)


def build_uifix_bytes(source_exe: Path) -> bytes:
    content = patch_dialog_bitmap_runtime(source_exe.read_bytes())
    return patch_cheat_features(content)


def verify_move_column_layout(exe_path: Path) -> None:
    source = load_game(exe_path).get_script(6982).source
    missing = [needle for needle in MOVE_LAYOUT_NEEDLES if needle not in source]
    if missing:
        raise ValueError(f"patched exe is missing move layout markers: {missing}")


def write_with_retry(
    output_exe: Path,
    content: bytes,
    *,
    attempts: int = 600,
    sleep_seconds: float = 1.0,
    writer: Callable[[Path, bytes], None] | None = None,
    sleeper: Callable[[float], None] | None = None,
) -> int:
    writer = writer or (lambda path, data: path.write_bytes(data))
    sleeper = sleeper or time.sleep

    last_error: PermissionError | None = None
    for attempt in range(1, attempts + 1):
        try:
            writer(output_exe, content)
            return attempt
        except PermissionError as error:
            last_error = error
            if attempt == attempts:
                break
            sleeper(sleep_seconds)

    if last_error is not None:
        raise last_error
    raise RuntimeError("write_with_retry exhausted attempts without writing or raising PermissionError")


def rebuild_uifix_in_place(
    source_exe: Path,
    output_exe: Path,
    *,
    attempts: int = 600,
    sleep_seconds: float = 1.0,
) -> int:
    content = build_uifix_bytes(source_exe)
    used_attempt = write_with_retry(
        output_exe,
        content,
        attempts=attempts,
        sleep_seconds=sleep_seconds,
    )
    verify_move_column_layout(output_exe)
    return used_attempt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--source-exe", type=Path)
    parser.add_argument("--output-exe", type=Path)
    parser.add_argument("--attempts", type=int, default=600)
    parser.add_argument("--sleep-seconds", type=float, default=1.0)
    args = parser.parse_args()

    root = args.root
    source_exe = args.source_exe or (root / DEFAULT_SOURCE_EXE)
    output_exe = args.output_exe or (root / DEFAULT_OUTPUT_EXE)
    used_attempt = rebuild_uifix_in_place(
        source_exe,
        output_exe,
        attempts=args.attempts,
        sleep_seconds=args.sleep_seconds,
    )
    print(f"patched={output_exe} attempts={used_attempt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
