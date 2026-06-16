# Full Chinese Feasibility

## Scope

This note records the current answer to one question:

Can `Proyecto Reloaded The Last Beta 1.9.1 Full` be localized into fully readable Chinese, not just loaded as a new language pack?

## Verified Facts

### Text packs

- `data/text/*` files are normal line-based text resources, not PE DLL files.
- The current text pack tooling can roundtrip these files byte-for-byte.
- The game loads a new language folder successfully when `data/text/lan.txt` and `data/text/config.ini` point to it.

### Runner and script pipeline

- The game executable is a `GameMaker 8.0` runner build.
- `TextReader` (`script 9942`) reads `data\\text\\<language>\\<file>.dll` with `file_text_open_read`.
- Each loaded byte is transformed with `ValuesAdjustment6` (`script 10060`) and then post-processed by `SpecialChars` (`script 9802`).
- `ValuesAdjustment6` only remaps printable ASCII-like bytes `32..126`; bytes outside that range fall through unchanged.
- `TextDialog` and `TextMenu` are thin wrappers over `TextReader`.

### Rendering path

- The game uses built-in `draw_text` / `draw_text_color` style rendering broadly across the UI.
- Script counts from the extracted project:
  - `draw_set_font`: 96
  - `draw_text_color`: 76
  - direct `draw_text(` calls: 30
  - `font_add`: 0
  - `font_add_sprite`: 0
  - `surface`: 0
- There is no evidence of an existing runtime sprite-font renderer.

### Font resources

- The runner contains `27` font slots, `21` of which are populated.
- Every discovered font uses `range_begin=0` and `range_end=255`.
- Representative fonts:
  - `FuenteDialogo` -> `ProggyClean`, size `10`
  - `FuenteDex` -> `Franklin Gothic Medium Cond`, size `8`
  - `FuenteMenu` -> `Times New Roman`, size `7`

This is the critical limitation. The current project fonts are single-byte character sets with only `256` code points available per font resource.

### Tooling state

- Local parser/tooling is stable:
  - `tools/poke_gm80.py`
  - `tests/test_poke_gm80.py`
  - `tests/test_poke_text_pack.py`
- Current test status:
  - `python -m unittest tests.test_poke_gm80 -v` -> pass
  - `python -m unittest tests.test_poke_text_pack -v` -> pass
- `GM8Decompiler 2.2.0` was installed locally and can parse this executable successfully.
- A decompiled project file was generated:
  - `artifacts/decompile/Proyecto Reloaded The Last Beta 1.9.1 Full.gmk`

## Conclusion

### What is definitely possible

- Editing and repacking the external text packs.
- Adding a new language folder that the game recognizes.
- Reaching a decompiled `GMK` project file from the shipped executable.

### What is not enough for full Chinese

Text-pack editing alone is not enough.

The current runtime is built around single-byte font resources and direct GameMaker text drawing. Even if Chinese bytes are made to survive the text loader, the shipped font resources only expose `0..255` glyph slots and the game does not already contain a custom renderer that could map larger character sets.

## Practical Meaning

### Short answer

`Can it be fully Chinese?`

Yes in theory, but not through the current text-pack-only route.

### Real blocker

A full Chinese patch needs both:

1. A writable project/rebuild workflow from the decompiled `GMK`.
2. A new runtime text rendering strategy, likely a custom sprite-font or glyph-atlas system, followed by patching the scripts that measure and draw text.

## Recommended Next Step

If the goal remains strict full Chinese, the project should move to an engine-level phase:

1. Establish a reliable `GMK -> editable project -> rebuilt executable` workflow.
2. Design a custom Chinese renderer that is not limited to the shipped `0..255` font ranges.
3. Replace or intercept the central text measurement and drawing paths before translating the full resource set.

If that workflow cannot be established, the honest conclusion is:

- text localization is tractable,
- full Chinese is not currently deliverable on this runner with external text edits alone.
