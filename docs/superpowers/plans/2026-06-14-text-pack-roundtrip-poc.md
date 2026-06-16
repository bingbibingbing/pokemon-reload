# Text Pack Roundtrip PoC Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that `data/text/es/txt_creditos.dll` can be decoded into an intermediate representation and re-encoded byte-for-byte, then support one controlled edit.

**Architecture:** Build a small Python module dedicated to this one text-pack family, with a CLI for inspection and roundtrip verification. Start from tests against the real extracted sample, infer the line/token structure, and only add the minimum encode/decode behavior needed for exact roundtrip and one safe edit.

**Tech Stack:** Python 3.12, standard library `unittest`, `pathlib`, `argparse`, `collections`

---

## File Structure

- Create: `tools/poke_text_pack.py`
  - One focused module that loads a packed file, decodes lines/tokens, re-encodes them, and exposes a minimal CLI.
- Create: `tests/test_poke_text_pack.py`
  - Regression tests for byte-exact roundtrip and one controlled edit.
- Create: `artifacts/roundtrip/`
  - Output directory for rebuilt sample files and controlled-edit samples.
- Use: `data/text/es/txt_creditos.dll`
  - Primary real-world sample under test.
- Use: `data/text/en/txt_creditos.dll`
  - Comparison sample to help infer structure.

No git repository is present in `D:\Documents\pokezhongzhuang`, so this plan uses reproducible artifacts instead of commit steps.

### Task 1: Scaffold the test harness

**Files:**
- Create: `tests/test_poke_text_pack.py`
- Create: `artifacts/roundtrip/.gitkeep`

- [ ] **Step 1: Write the failing test for byte-exact roundtrip**

```python
from pathlib import Path
import unittest

from tools.poke_text_pack import roundtrip_bytes


ROOT = Path(__file__).resolve().parents[1]
ES_CREDITOS = ROOT / "data" / "text" / "es" / "txt_creditos.dll"


class TextPackRoundtripTests(unittest.TestCase):
    def test_roundtrip_preserves_creditos_bytes(self) -> None:
        original = ES_CREDITOS.read_bytes()
        rebuilt = roundtrip_bytes(original)
        self.assertEqual(rebuilt, original)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```powershell
python -m unittest tests.test_poke_text_pack.TextPackRoundtripTests.test_roundtrip_preserves_creditos_bytes -v
```

Expected:
- `ModuleNotFoundError` or `ImportError` because `tools.poke_text_pack` does not exist yet.

- [ ] **Step 3: Create the artifact directory placeholder**

```powershell
New-Item -ItemType Directory -Force .\artifacts\roundtrip | Out-Null
New-Item -ItemType File -Force .\artifacts\roundtrip\.gitkeep | Out-Null
```

- [ ] **Step 4: Verify the directory exists**

Run:

```powershell
Get-ChildItem .\artifacts\roundtrip -Force
```

Expected:
- One `.gitkeep` placeholder is listed.

### Task 2: Add the minimal roundtrip implementation

**Files:**
- Create: `tools/poke_text_pack.py`
- Modify: `tests/test_poke_text_pack.py`

- [ ] **Step 1: Write a second failing test for line preservation**

```python
from tools.poke_text_pack import decode_lines, encode_lines, roundtrip_bytes


class TextPackRoundtripTests(unittest.TestCase):
    def test_roundtrip_preserves_creditos_bytes(self) -> None:
        original = ES_CREDITOS.read_bytes()
        rebuilt = roundtrip_bytes(original)
        self.assertEqual(rebuilt, original)

    def test_decode_encode_preserves_raw_lines(self) -> None:
        original = ES_CREDITOS.read_bytes()
        lines = decode_lines(original)
        rebuilt = encode_lines(lines)
        self.assertEqual(rebuilt, original)
```

- [ ] **Step 2: Run the tests to verify they fail for the expected reason**

Run:

```powershell
python -m unittest tests.test_poke_text_pack -v
```

Expected:
- Failures caused by missing `tools.poke_text_pack` symbols, not by assertion mismatches.

- [ ] **Step 3: Write the minimal implementation**

```python
from __future__ import annotations

from pathlib import Path
import argparse


def decode_lines(blob: bytes) -> list[bytes]:
    if not blob:
        return []
    return blob.splitlines(keepends=True)


def encode_lines(lines: list[bytes]) -> bytes:
    return b"".join(lines)


def roundtrip_bytes(blob: bytes) -> bytes:
    return encode_lines(decode_lines(blob))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    blob = args.path.read_bytes()
    rebuilt = roundtrip_bytes(blob)
    print(f"bytes={len(blob)} lines={len(decode_lines(blob))} exact={rebuilt == blob}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the tests to verify they pass**

Run:

```powershell
python -m unittest tests.test_poke_text_pack -v
```

Expected:
- Both tests pass.

- [ ] **Step 5: Run the inspection CLI on the real sample**

Run:

```powershell
python .\tools\poke_text_pack.py .\data\text\es\txt_creditos.dll
```

Expected:
- One summary line showing byte count, line count, and `exact=True`.

### Task 3: Prove controlled editing works

**Files:**
- Modify: `tests/test_poke_text_pack.py`
- Modify: `tools/poke_text_pack.py`

- [ ] **Step 1: Write the failing controlled-edit test**

```python
from tools.poke_text_pack import decode_lines, encode_lines, replace_line_text, roundtrip_bytes


class TextPackRoundtripTests(unittest.TestCase):
    def test_controlled_edit_changes_only_target_line(self) -> None:
        original = ES_CREDITOS.read_bytes()
        edited = replace_line_text(original, 0, b"TEST")
        self.assertNotEqual(edited, original)
        self.assertEqual(len(decode_lines(edited)), len(decode_lines(original)))
```

- [ ] **Step 2: Run the controlled-edit test to verify it fails**

Run:

```powershell
python -m unittest tests.test_poke_text_pack.TextPackRoundtripTests.test_controlled_edit_changes_only_target_line -v
```

Expected:
- Failure caused by missing `replace_line_text`.

- [ ] **Step 3: Implement the minimal controlled-edit helper and artifact writeout**

```python
def replace_line_text(blob: bytes, line_index: int, replacement: bytes) -> bytes:
    lines = decode_lines(blob)
    current = lines[line_index]
    newline = b""
    if current.endswith(b"\r\n"):
        newline = b"\r\n"
        current = current[:-2]
    elif current.endswith(b"\n"):
        newline = b"\n"
        current = current[:-1]
    lines[line_index] = replacement + newline
    return encode_lines(lines)
```

Append this to `main()` after computing `rebuilt`:

```python
    output_dir = Path("artifacts/roundtrip")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{args.path.name}.roundtrip").write_bytes(rebuilt)
```

- [ ] **Step 4: Run the full tests to verify they pass**

Run:

```powershell
python -m unittest tests.test_poke_text_pack -v
```

Expected:
- All tests pass.

- [ ] **Step 5: Write one controlled-edit artifact**

Run:

```powershell
python - <<'PY'
from pathlib import Path
from tools.poke_text_pack import replace_line_text

path = Path(r".\data\text\es\txt_creditos.dll")
blob = path.read_bytes()
edited = replace_line_text(blob, 0, b"TEST")
out = Path(r".\artifacts\roundtrip\txt_creditos.dll.edited")
out.write_bytes(edited)
print(out, len(edited))
PY
```

Expected:
- The edited artifact path and byte count are printed.

### Task 4: Summarize tractability and compare with the English sample

**Files:**
- Modify: `tools/poke_text_pack.py`

- [ ] **Step 1: Add a comparison helper for locale pair inspection**

```python
def compare_line_lengths(left: bytes, right: bytes) -> list[tuple[int, int, int]]:
    left_lines = decode_lines(left)
    right_lines = decode_lines(right)
    rows: list[tuple[int, int, int]] = []
    for index, (l_line, r_line) in enumerate(zip(left_lines, right_lines)):
        rows.append((index, len(l_line.rstrip(b"\r\n")), len(r_line.rstrip(b"\r\n"))))
    return rows
```

- [ ] **Step 2: Extend the CLI with an optional `--compare` path**

```python
    parser.add_argument("--compare", type=Path)
    if args.compare:
        rows = compare_line_lengths(blob, args.compare.read_bytes())
        preview = rows[:5]
        print(f"compare_rows={len(rows)} preview={preview}")
```

- [ ] **Step 3: Run the CLI with the English comparison sample**

Run:

```powershell
python .\tools\poke_text_pack.py .\data\text\es\txt_creditos.dll --compare .\data\text\en\txt_creditos.dll
```

Expected:
- Output includes `exact=True` and a small preview of per-line length differences.

- [ ] **Step 4: Verify the saved roundtrip artifact is byte-identical**

Run:

```powershell
python - <<'PY'
from pathlib import Path
src = Path(r".\data\text\es\txt_creditos.dll").read_bytes()
rebuilt = Path(r".\artifacts\roundtrip\txt_creditos.dll.roundtrip").read_bytes()
print(src == rebuilt, len(src), len(rebuilt))
PY
```

Expected:
- `True` followed by identical byte lengths.

## Self-Review

- Spec coverage:
  - Roundtrip proof is covered by Tasks 1 and 2.
  - Controlled edit proof is covered by Task 3.
  - Tractability summary inputs are covered by Task 4.
- Placeholder scan:
  - No `TODO`, `TBD`, or indirect “handle later” language remains.
- Type consistency:
  - All referenced functions are defined in `tools/poke_text_pack.py`.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-06-14-text-pack-roundtrip-poc.md`. Two execution options:

1. Subagent-Driven (recommended) - dispatch a fresh subagent per task, review between tasks, fast iteration
2. Inline Execution - execute tasks in this session using executing-plans, batch execution with checkpoints

If no preference is stated, continue with inline execution in this session.
