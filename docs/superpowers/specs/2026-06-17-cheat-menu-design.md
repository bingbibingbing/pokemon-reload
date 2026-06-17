# Cheat Menu Design

## Goal

Add a hidden cheat system for battle and capture assistance that is controlled by an external config gate and, when enabled, exposed through a main-menu `Cheat` page.

## Requirements

### External gate

- Add a `[cheat]` section to a plain-text config file.
- `enabled=0` means:
  - the `Cheat` menu is not visible in the main menu
  - all cheat logic is fully disabled at runtime
- `enabled=1` means:
  - the `Cheat` menu is visible in the main menu
  - runtime logic may use cheat settings

### Runtime cheat settings

The config must support these keys:

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

### Cheat menu

- The menu is only shown when `enabled=1`.
- The menu contains:
  - `One-Key Cheat`
  - `No Player Damage`
  - `One Hit Kill`
  - `Enemy Cannot Act`
  - `Enemy Start With 1 HP`
  - `Always Catch`
- The menu must allow toggling values and persist them back to the config file.

### One-key behavior

- `one_key_cheat=1` means the predefined cheat bundle is active.
- The bundle includes all five battle/capture cheats:
  - no player damage
  - one hit kill
  - enemy cannot act
  - enemy start with 1 HP
  - always catch
- While `one_key_cheat=1`, the five individual cheat items remain visible but are read-only/greyed out.
- While `one_key_cheat=0`, the five individual cheat items are editable and control behavior independently.

### Runtime precedence

Runtime evaluation must follow this order:

1. If `enabled=0`, all cheats are off.
2. Else if `one_key_cheat=1`, all five supported cheats are on.
3. Else, each cheat follows its own config key.

## Codebase impact

### Config layer

- Add a shared way to read and write the cheat config values from the executable's script resources.
- Keep parsing simple and resilient to missing keys by falling back to `0`.

### Main menu

- Locate the main menu option list and inject a conditional `Cheat` entry.
- Hook menu navigation so the new page opens only when `enabled=1`.

### Cheat page

- Reuse existing option/menu patterns instead of inventing a new UI system.
- The page only needs toggles and persistence.

### Battle and capture logic

Patch these already verified logic areas:

- Enemy dealing damage to the player party:
  - `5359 Ataque2GolpeaPokemon1`
- Player dealing damage to the enemy:
  - `5348 Ataque1GolpeaPokemon2`
- Turn/action selection for enemy turns:
  - `5782 CombatePorTurnos`
- Wild enemy initialization:
  - `7847 IniciaSalvaje`
  - `7849 IniciaValuesPokemon2`
  - any follow-up start-of-battle HP reset path discovered during implementation
- Capture success:
  - `8726 PokeBallCapturando`

## Error handling

- Missing config file should behave as all cheats off.
- Missing keys should default to `0`.
- Invalid values should be treated as `0`.
- Config writes should only update cheat keys and should not corrupt unrelated config content.

## Testing

Implementation must verify:

- `enabled=0` hides the `Cheat` menu and disables all cheat effects.
- `enabled=1` shows the `Cheat` menu.
- `one_key_cheat=1` activates all five cheats and greys out child toggles.
- `one_key_cheat=0` allows enabling cheats individually.
- `No Player Damage` prevents HP loss from enemy attacks.
- `One Hit Kill` defeats enemies in one successful player hit.
- `Enemy Cannot Act` prevents enemy move execution.
- `Enemy Start With 1 HP` sets target enemy HP to `1` at battle start.
- `Always Catch` guarantees capture in wild encounters.

## Non-goals

- No hotkey-based cheat toggles.
- No hidden in-game method to turn `enabled` on when it is `0`.
- No new cheat effects beyond the five listed above.
