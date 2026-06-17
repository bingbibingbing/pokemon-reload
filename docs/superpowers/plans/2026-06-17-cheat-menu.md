# Cheat Menu Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an externally gated cheat menu and wire five battle/capture cheats into the GameMaker executable scripts.

**Architecture:** Add a small cheat-config layer inside the patched GameMaker scripts, surface a conditional `Cheat` menu entry on the main menu, then route battle and capture logic through shared cheat checks. Persist all menu edits back to a simple config file so the feature can be enabled externally and adjusted in-game once visible.

**Tech Stack:** Python patch tooling (`tools/poke_gm80.py`), GameMaker 8 script patching, Python unittest/manual verification, Windows PowerShell.

---

## File map

- Modify: `D:\Documents\pokezhongzhuang\Proyecto Reloaded The Last Beta 1.9.1 Full\tools\poke_zh_patch.py`
  - Add the new executable patch pipeline for cheat scripts once target script slots are identified.
- Modify: `D:\Documents\pokezhongzhuang\Proyecto Reloaded The Last Beta 1.9.1 Full\tools\poke_gm80.py`
  - Only if helper support is needed for easier script extraction or replacement.
- Modify: `D:\Documents\pokezhongzhuang\Proyecto Reloaded The Last Beta 1.9.1 Full\Proyecto Reloaded The Last Beta 1.9.1 Full.zh-cn.uifix.exe`
  - Patched output artifact after script replacement.
- Create: `D:\Documents\pokezhongzhuang\Proyecto Reloaded The Last Beta 1.9.1 Full\docs\analysis\2026-06-17-cheat-script-map.md`
  - Record the final script ids used for menu/config/runtime hooks.
- Test: Manual runtime checks on the patched executable.

### Task 1: Map menu and config hook points

**Files:**
- Create: `D:\Documents\pokezhongzhuang\Proyecto Reloaded The Last Beta 1.9.1 Full\docs\analysis\2026-06-17-cheat-script-map.md`
- Modify: `D:\Documents\pokezhongzhuang\Proyecto Reloaded The Last Beta 1.9.1 Full\tools\poke_zh_patch.py`

- [ ] **Step 1: Extract likely menu scripts and identify the main-menu option list**

Run:

```powershell
@'
from tools.poke_gm80 import load_game
from pathlib import Path
game = load_game(Path("Proyecto Reloaded The Last Beta 1.9.1 Full.exe"))
for idx in [6348, 9441, 9442]:
    s = game.get_script(idx)
    print(f"=== {s.index} {s.name} ===")
    print(s.source[:4000])
'@ | python -
```

Expected: readable script excerpts for startup/options code that expose where menu entries are built.

- [ ] **Step 2: Extract scripts around config file IO patterns**

Run:

```powershell
@'
from tools.poke_gm80 import load_game
from pathlib import Path
game = load_game(Path("Proyecto Reloaded The Last Beta 1.9.1 Full.exe"))
for script in game.scripts.values():
    src = script.source
    if "file_text_open_read" in src or "file_text_open_write" in src or "ini_open" in src:
        print(f"{script.index}`t{script.name}")
'@ | python -
```

Expected: a short list of candidate scripts that already read/write config-like files.

- [ ] **Step 3: Write the script map note**

Record the actual script ids and why they matter in:

```markdown
# Cheat Script Map

- Main menu entry script: `<id> <name>` because it builds the visible option list.
- Cheat page script: `<id> <name>` because it handles option-style toggles.
- Config read/write script: `<id> <name>` because it already uses file/ini APIs.
- Battle hooks:
  - `5348 Ataque1GolpeaPokemon2`
  - `5359 Ataque2GolpeaPokemon1`
  - `5782 CombatePorTurnos`
  - `7847 IniciaSalvaje`
  - `7849 IniciaValuesPokemon2`
  - `8726 PokeBallCapturando`
```

- [ ] **Step 4: Verify the note exists and is populated**

Run:

```powershell
Get-Content 'docs\analysis\2026-06-17-cheat-script-map.md'
```

Expected: the file lists concrete script ids with no placeholders.

### Task 2: Add a cheat config layer

**Files:**
- Modify: `D:\Documents\pokezhongzhuang\Proyecto Reloaded The Last Beta 1.9.1 Full\tools\poke_zh_patch.py`
- Modify: `D:\Documents\pokezhongzhuang\Proyecto Reloaded The Last Beta 1.9.1 Full\Proyecto Reloaded The Last Beta 1.9.1 Full.zh-cn.uifix.exe`

- [ ] **Step 1: Write a failing config probe command**

Run:

```powershell
Test-Path 'data\cheat.ini'
```

Expected: `False` before the file is created.

- [ ] **Step 2: Add cheat helper script sources to the patcher**

Implement helper scripts with responsibilities:

```python
CHEAT_DEFAULTS_SOURCE = r'''
global.cheat_enabled = 0;
global.cheat_one_key = 0;
global.cheat_no_player_damage = 0;
global.cheat_one_hit_kill = 0;
global.cheat_enemy_cannot_act = 0;
global.cheat_enemy_start_with_1hp = 0;
global.cheat_always_catch = 0;
'''
```

and read/write helpers that:

```python
CHEAT_CONFIG_PATH = "data\\cheat.ini"
```

Expected: patcher contains dedicated source constants for defaulting, loading, saving, and effective-state checks.

- [ ] **Step 3: Patch startup flow to load cheat config**

Use `patch_script_source` or targeted replacement so the game loads cheat config during startup after other globals are initialized.

Expected code shape inside the patched script:

```text
ex(<cheat_defaults_script>);
ex(<cheat_load_script>);
```

- [ ] **Step 4: Emit a default cheat config file if missing**

Create:

```ini
[cheat]
enabled=0
one_key_cheat=0
no_player_damage=0
one_hit_kill=0
enemy_cannot_act=0
enemy_start_with_1hp=0
always_catch=0
```

Expected: the file exists after patch generation or first boot.

### Task 3: Add the conditional main-menu Cheat entry

**Files:**
- Modify: `D:\Documents\pokezhongzhuang\Proyecto Reloaded The Last Beta 1.9.1 Full\tools\poke_zh_patch.py`
- Modify: `D:\Documents\pokezhongzhuang\Proyecto Reloaded The Last Beta 1.9.1 Full\Proyecto Reloaded The Last Beta 1.9.1 Full.zh-cn.uifix.exe`

- [ ] **Step 1: Identify where the main-menu entries are assembled**

Run:

```powershell
@'
from tools.poke_gm80 import load_game
from pathlib import Path
game = load_game(Path("Proyecto Reloaded The Last Beta 1.9.1 Full.exe"))
for idx in [6348]:
    s = game.get_script(idx)
    print(s.source)
'@ | python -
```

Expected: a menu construction block where one additional option can be inserted.

- [ ] **Step 2: Insert conditional menu entry logic**

Patch the menu builder so it only appends a `Cheat` item when:

```text
global.cheat_enabled = 1
```

Expected: no `Cheat` option is rendered when the config gate is off.

- [ ] **Step 3: Route the new entry to a cheat page object/script**

Add navigation logic similar to existing menu pages:

```text
if(selection = <cheat_option_index>) {
    ex(<open_cheat_menu_script>);
    exit;
}
```

Expected: selecting `Cheat` opens a dedicated toggle page.

### Task 4: Build the Cheat page and persistence

**Files:**
- Modify: `D:\Documents\pokezhongzhuang\Proyecto Reloaded The Last Beta 1.9.1 Full\tools\poke_zh_patch.py`
- Modify: `D:\Documents\pokezhongzhuang\Proyecto Reloaded The Last Beta 1.9.1 Full\Proyecto Reloaded The Last Beta 1.9.1 Full.zh-cn.uifix.exe`

- [ ] **Step 1: Reuse an existing option-page pattern**

Extract a nearby options script that already supports toggle rows and cursor movement.

Run:

```powershell
python tools\poke_gm80.py 'Proyecto Reloaded The Last Beta 1.9.1 Full.exe' --script-index 9441
```

Expected: a pattern that can be cloned/adapted for a cheat page.

- [ ] **Step 2: Implement the six cheat rows**

Required rows:

```text
One-Key Cheat
No Player Damage
One Hit Kill
Enemy Cannot Act
Enemy Start With 1 HP
Always Catch
```

Expected behavior:

```text
if global.cheat_one_key = 1:
    child rows draw disabled/read-only
else:
    child rows can toggle 0/1
```

- [ ] **Step 3: Save changes immediately on toggle**

Expected code path:

```text
toggle value
ex(<cheat_save_script>)
```

Expected: menu changes persist across restart.

### Task 5: Patch battle and capture runtime hooks

**Files:**
- Modify: `D:\Documents\pokezhongzhuang\Proyecto Reloaded The Last Beta 1.9.1 Full\tools\poke_zh_patch.py`
- Modify: `D:\Documents\pokezhongzhuang\Proyecto Reloaded The Last Beta 1.9.1 Full\Proyecto Reloaded The Last Beta 1.9.1 Full.zh-cn.uifix.exe`

- [ ] **Step 1: Prevent player HP loss when configured**

Patch `5359 Ataque2GolpeaPokemon1` so the enemy damage write is skipped when:

```text
ex(<cheat_effective_script>, "no_player_damage")
```

Expected runtime effect: enemy attacks no longer reduce `global.PS_1[...]`.

- [ ] **Step 2: Force one-hit kill on player damage**

Patch `5348 Ataque1GolpeaPokemon2` so on a successful hit:

```text
pokemon2.DANO = global.PS_2[RECEPTOR];
global.PS_2[RECEPTOR] = 0;
```

when the effective cheat state for `one_hit_kill` is on.

- [ ] **Step 3: Prevent enemy action execution**

Patch `5782 CombatePorTurnos` before enemy execution:

```text
if ex(<cheat_effective_script>, "enemy_cannot_act") {
    ACTION2 = 0;
}
```

Expected runtime effect: the enemy turn resolves as no action.

- [ ] **Step 4: Set enemy start HP to 1**

Patch wild initialization/start paths so when the effective cheat state is on:

```text
global.PS_2[POS] = 1;
```

Expected runtime effect: wild enemies start the battle at exactly `1` HP.

- [ ] **Step 5: Force capture success**

Patch `8726 PokeBallCapturando` so when the effective cheat state is on:

```text
capt = true;
timer = -1;
```

Expected runtime effect: wild capture checks always succeed.

### Task 6: Rebuild patched executable and verify manually

**Files:**
- Modify: `D:\Documents\pokezhongzhuang\Proyecto Reloaded The Last Beta 1.9.1 Full\Proyecto Reloaded The Last Beta 1.9.1 Full.zh-cn.uifix.exe`

- [ ] **Step 1: Run the patch pipeline**

Run:

```powershell
python tools\repatch_uifix.py
```

Expected: patched executable is regenerated without traceback.

- [ ] **Step 2: Smoke-check the executable script count**

Run:

```powershell
python tools\poke_gm80.py 'Proyecto Reloaded The Last Beta 1.9.1 Full.zh-cn.uifix.exe'
```

Expected: the patched executable still parses and prints runner/script metadata.

- [ ] **Step 3: Manual game test matrix**

Check these cases:

```text
1. Set enabled=0 -> boot game -> Cheat menu is hidden.
2. Set enabled=1 -> boot game -> Cheat menu appears on main screen.
3. In Cheat menu set one_key_cheat=1 -> child rows are visible but disabled.
4. Start a wild battle with one_key_cheat=1 -> enemy starts with 1 HP, cannot act, player takes no damage, capture always succeeds.
5. Turn one_key_cheat=0 and only always_catch=1 -> battle plays normally except capture is guaranteed.
6. Turn one_key_cheat=0 and only one_hit_kill=1 -> first successful player hit KOs the enemy.
```

- [ ] **Step 4: Record final test notes**

Append actual observed results to:

```markdown
## Verification

- Config gate hidden/menu visible behavior: PASS/FAIL
- One-key read-only child behavior: PASS/FAIL
- No Player Damage: PASS/FAIL
- One Hit Kill: PASS/FAIL
- Enemy Cannot Act: PASS/FAIL
- Enemy Start With 1 HP: PASS/FAIL
- Always Catch: PASS/FAIL
```

