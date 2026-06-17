# Project Rules

## Highest-Priority Constraint

This repository is being worked on by multiple threads at the same time.

Any cheat-related work must be implemented as an additive patch on top of the current Chinese-localized build.

Do not modify, replace, regress, or rebuild other contributors' localization work.

## Non-Negotiable Rules For Cheat Work

1. Do not modify any Chinese localization text.
2. Do not modify any Chinese localization images or rendered text assets.
3. Do not modify any language-loading or localization pipeline logic.
4. Do not modify the title-screen menu or any pre-game localization behavior.
5. Do not overwrite or regenerate another thread's localization output unless the user explicitly asks for that exact operation.
6. Apply cheat functionality only as a minimal incremental change inside the localized version.
7. Prefer battle logic, capture logic, and in-game options logic for cheat integration.
8. If a cheat implementation would require changing localization behavior, stop and ask the user instead of proceeding.

## Safe Operating Boundary

For this project, the safe default is:

- touch cheat logic only
- avoid localization logic entirely
- preserve all existing localized behavior

If there is any doubt about whether a change affects localization, treat it as forbidden until the user approves it explicitly.
