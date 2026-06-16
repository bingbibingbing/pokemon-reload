# Text Pack Roundtrip PoC Design

## Goal

Prove whether a text pack used by Pokemon Reloaded can be unpacked and packed back without loss.

## Scope

This PoC only targets the text pack format itself.

In scope:
- Inspect one or two small localized files under `data/text/{lang}`.
- Infer the encoding structure by comparing matching `es` and `en` files.
- Build a local script that supports `decode` and `encode`.
- Verify roundtrip fidelity with a byte-for-byte comparison.
- Apply one small controlled text change after roundtrip succeeds.

Out of scope:
- Chinese rendering support.
- Font replacement or glyph injection.
- Full-game translation.
- Reverse engineering the whole executable unless the file-only approach fails.

## Target Samples

Primary sample:
- `data/text/es/txt_creditos.dll`

Secondary sample if needed:
- `data/text/es/txt_menu.dll`
- Matching `en` version for comparison.

The first sample should be as small as possible to reduce noise while still exercising the real format.

## Working Assumptions

Observed facts from the extracted game files:
- Language resources are split by locale under `data/text/en` and `data/text/es`.
- Many `.dll` files are not PE DLLs. They are custom text resources with a line-based structure.
- Matching `es` and `en` files often have the same number of lines, which suggests indexed text entries.
- `txt_keyboard.dll` looks like a symbol table or character mapping table and may influence text encoding.

Initial hypothesis:
- A text pack is encoded line by line using a fixed token or substitution table.
- Newlines are significant and must be preserved exactly.

## Approach Options

### Option 1: Differential format inference from localized pairs

Compare the same file across `es` and `en`, infer repeated token patterns, then implement a decoder/encoder.

Pros:
- Fastest path to a usable PoC.
- Stays focused on the actual packed files.

Cons:
- May stall if the format uses additional hidden state or checksums.

### Option 2: Reverse engineer decode logic from the executable

Find the runtime load/decode path in the game binary and reproduce it.

Pros:
- Highest confidence in format behavior.

Cons:
- Much slower.
- Overkill for a first PoC.

### Option 3: Hybrid fallback

Start with Option 1 and only inspect the executable if file-pair inference stops making progress.

Pros:
- Preserves fast path while keeping a fallback.

Cons:
- Slightly more coordination overhead.

## Recommended Design

Use Option 3 with Option 1 as the default path.

Implementation flow:
1. Select the smallest viable sample, starting with `txt_creditos.dll`.
2. Inspect raw bytes, line boundaries, and differences between `es` and `en`.
3. Test whether encoding is line-local, token-based, or position-based.
4. Implement a script that:
   - reads a packed file,
   - decodes it into an intermediate representation,
   - re-encodes the representation,
   - compares output bytes with the source file.
5. If roundtrip fails, use the mismatch positions to refine the inferred rules.
6. After exact roundtrip succeeds, change one low-risk entry and confirm the encoder produces a structurally valid modified file.

## Intermediate Representation

The first version of the script should prefer a minimal representation:
- ordered list of lines,
- per-line raw token sequence,
- decoded form if confidently inferred.

This avoids overcommitting to a textual model before the encoding is understood.

## Success Criteria

The PoC is successful only if all of the following are true:
- The decoder can consume the chosen sample file without manual patching.
- The encoder can rebuild the same file from the decoded representation.
- The rebuilt output matches the original file byte for byte.
- A small controlled edit can be encoded without breaking file structure.

## Failure Criteria

The PoC is blocked if any of the following turn out to be true:
- The file format depends on executable-only logic that cannot be inferred from file comparison.
- The encoding uses per-file secrets, checksums, or runtime-generated state.
- The chosen sample is too small or atypical to generalize, and a second sample shows contradictory behavior.

If blocked, the next move is to inspect the executable's text loading path.

## Test Strategy

Before implementation code:
- Add a failing test for byte-exact roundtrip on the chosen sample file.
- Add a second failing test for a controlled edit path if the first test passes.

Verification commands should prove:
- the test fails before implementation,
- the test passes after implementation,
- the output file matches the original source file exactly.

## Deliverables

- One spec document.
- One local analysis script or small tool.
- Automated roundtrip test for the selected sample.
- Short findings summary on whether the format is tractable.

## Risks

- `txt_keyboard.dll` may encode a custom alphabet that has to be modeled first.
- The file extension `.dll` is misleading and may hide multiple internal formats.
- Small files may omit edge cases present in `txt_menu.dll` or `txt_dialog.dll`.

## Decision Log

- Use a file-pair inference approach first because it gives the fastest proof.
- Use `txt_creditos.dll` before `txt_menu.dll` unless the former is too trivial to expose the format.
