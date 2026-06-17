from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.repatch_uifix import (
    build_uifix_bytes,
    rebuild_uifix_in_place,
    verify_move_column_layout,
    write_with_retry,
)


ROOT = Path(__file__).resolve().parents[1]
GAME_EXE = ROOT / "Proyecto Reloaded The Last Beta 1.9.1 Full.exe"


class RepatchUifixTests(unittest.TestCase):
    def test_write_with_retry_retries_permission_error_then_succeeds(self) -> None:
        calls: list[int] = []
        sleeps: list[float] = []
        written: dict[str, bytes] = {}

        def fake_writer(path: Path, data: bytes) -> None:
            calls.append(1)
            if len(calls) < 3:
                raise PermissionError("locked")
            written[str(path)] = data

        attempt = write_with_retry(
            Path("dummy.exe"),
            b"patched",
            attempts=5,
            sleep_seconds=0.25,
            writer=fake_writer,
            sleeper=sleeps.append,
        )

        self.assertEqual(attempt, 3)
        self.assertEqual(sleeps, [0.25, 0.25])
        self.assertEqual(written["dummy.exe"], b"patched")

    def test_verify_move_column_layout_rejects_unpatched_base_exe(self) -> None:
        with self.assertRaises(ValueError):
            verify_move_column_layout(GAME_EXE)

    def test_build_uifix_bytes_delegates_to_patch_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_exe = Path(temp_dir) / "source.exe"
            source_exe.write_bytes(b"runner-bytes")
            with patch("tools.repatch_uifix.patch_dialog_bitmap_runtime", return_value=b"patched-runner") as runtime_patch:
                patched_bytes = build_uifix_bytes(source_exe)

        self.assertEqual(patched_bytes, b"patched-runner")
        runtime_patch.assert_called_once_with(b"runner-bytes")

    def test_rebuild_uifix_in_place_orchestrates_build_write_and_verify(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_exe = Path(temp_dir) / "source.exe"
            output_exe = Path(temp_dir) / "output.exe"

            with patch("tools.repatch_uifix.build_uifix_bytes", return_value=b"patched-bytes") as build_patch:
                with patch("tools.repatch_uifix.write_with_retry", return_value=4) as write_patch:
                    with patch("tools.repatch_uifix.verify_move_column_layout") as verify_patch:
                        attempt = rebuild_uifix_in_place(source_exe, output_exe, attempts=99, sleep_seconds=0.5)

        self.assertEqual(attempt, 4)
        build_patch.assert_called_once_with(source_exe)
        write_patch.assert_called_once_with(
            output_exe,
            b"patched-bytes",
            attempts=99,
            sleep_seconds=0.5,
        )
        verify_patch.assert_called_once_with(output_exe)


if __name__ == "__main__":
    unittest.main()
