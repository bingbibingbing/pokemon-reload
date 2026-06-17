from pathlib import Path
import json
import unittest

from tools.poke_text_pack import (
    build_token_alphabet,
    compare_line_lengths,
    decode_display_text,
    decode_line_with_composites,
    decode_line_with_mapping,
    decode_lines,
    encode_display_text,
    encode_lines,
    infer_char_mapping,
    replace_line_text,
    roundtrip_bytes,
    tokenize_line,
)


ROOT = Path(__file__).resolve().parents[1]
ES_CREDITOS = ROOT / "data" / "text" / "es" / "txt_creditos.dll"
EN_CREDITOS = ROOT / "data" / "text" / "en" / "txt_creditos.dll"
EN_KEYBOARD = ROOT / "data" / "text" / "en" / "txt_keyboard.dll"
EN_PKMN = ROOT / "data" / "text" / "en" / "txt_pkmn.dll"
ZH_MENU = ROOT / "data" / "text" / "zh" / "txt_menu.dll"
ZH_DIALOG = ROOT / "data" / "text" / "zh" / "txt_dialog.dll"
ZH_RENDER = ROOT / "data" / "text" / "zh" / "render"
ZH_RENDER_MANIFEST = ROOT / "data" / "text" / "zh" / "render_manifest.json"
REFERENCE_POKEMON_151 = ROOT / "artifacts" / "reference" / "en_pokemon_151.txt"


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

    def test_controlled_edit_changes_only_target_line(self) -> None:
        original = ES_CREDITOS.read_bytes()
        edited = replace_line_text(original, 0, b"TEST")
        self.assertNotEqual(edited, original)
        self.assertEqual(len(decode_lines(edited)), len(decode_lines(original)))

    def test_compare_line_lengths_reports_shared_structure(self) -> None:
        rows = compare_line_lengths(ES_CREDITOS.read_bytes(), EN_CREDITOS.read_bytes())
        self.assertEqual(len(rows), len(decode_lines(EN_CREDITOS.read_bytes())))
        self.assertEqual(rows[0][0], 0)

    def test_tokenize_line_splits_bulbasaur_with_keyboard_alphabet(self) -> None:
        alphabet = build_token_alphabet(EN_KEYBOARD.read_text().splitlines())
        encoded = EN_PKMN.read_text().splitlines()[0]
        self.assertEqual(
            tokenize_line(encoded, alphabet),
            ["v", "\\", "=", '"', "}", "G", "}", "\\", "M"],
        )

    def test_infer_char_mapping_decodes_credit_headings(self) -> None:
        alphabet = build_token_alphabet(EN_KEYBOARD.read_text().splitlines())
        encoded_names = EN_PKMN.read_text().splitlines()
        plain_names = REFERENCE_POKEMON_151.read_text(encoding="utf-8").splitlines()
        mapping = infer_char_mapping(
            encoded_names[:151],
            plain_names,
            alphabet,
        )
        credit_lines = EN_CREDITOS.read_text().splitlines()
        self.assertEqual(
            decode_line_with_mapping(credit_lines[1], mapping, alphabet),
            "Credits",
        )
        self.assertEqual(
            decode_line_with_mapping(credit_lines[2], mapping, alphabet),
            "Created by",
        )
        self.assertEqual(
            decode_line_with_mapping(credit_lines[3], mapping, alphabet),
            "Based on the games",
        )

    def test_credit_seed_lines_fill_remaining_project_tokens(self) -> None:
        alphabet = build_token_alphabet(EN_KEYBOARD.read_text().splitlines())
        encoded_names = EN_PKMN.read_text().splitlines()
        plain_names = REFERENCE_POKEMON_151.read_text(encoding="utf-8").splitlines()
        credit_lines = EN_CREDITOS.read_text().splitlines()
        mapping = infer_char_mapping(
            encoded_names[:151] + [credit_lines[10], credit_lines[39]],
            plain_names + ["NDS Project", "Thanks for playing!"],
            alphabet,
        )
        self.assertEqual(
            decode_line_with_mapping(credit_lines[10], mapping, alphabet),
            "NDS Project",
        )
        self.assertEqual(
            decode_line_with_mapping(credit_lines[39], mapping, alphabet),
            "Thanks for playing!",
        )

    def test_composite_accent_decodes_pokemon_word_in_credits(self) -> None:
        alphabet = build_token_alphabet(EN_KEYBOARD.read_text().splitlines())
        encoded_names = EN_PKMN.read_text().splitlines()
        plain_names = REFERENCE_POKEMON_151.read_text(encoding="utf-8").splitlines()
        credit_lines = EN_CREDITOS.read_text().splitlines()
        mapping = infer_char_mapping(
            encoded_names[:151] + [credit_lines[10], credit_lines[39]],
            plain_names + ["NDS Project", "Thanks for playing!"],
            alphabet,
        )
        self.assertEqual(
            decode_line_with_composites(credit_lines[0], mapping, alphabet),
            "Pokémon Reloaded Version",
        )

    def test_tokenize_line_can_preserve_menu_control_tokens(self) -> None:
        alphabet = build_token_alphabet(EN_KEYBOARD.read_text().splitlines())
        encoded = (ROOT / "data" / "text" / "en" / "txt_menu.dll").read_text().splitlines()[6]
        tokens = tokenize_line(encoded, alphabet, allow_fallback_single_chars=True)
        self.assertEqual("".join(tokens), encoded)
        self.assertIn("~", tokens)
        self.assertIn("#", tokens)

    def test_decode_display_text_decodes_known_zh_menu_lines(self) -> None:
        lines = decode_lines(ZH_MENU.read_bytes())
        self.assertEqual(decode_display_text(lines[0]), "New game")
        self.assertEqual(decode_display_text(lines[1]), "ZH LOAD")
        self.assertEqual(decode_display_text(lines[2]), "Exit game")
        self.assertEqual(decode_display_text(lines[3]), "Yes (&Z)")
        self.assertEqual(decode_display_text(lines[4]), "No (&X)")
        self.assertEqual(decode_display_text(lines[5]), "OK (&Z)")

    def test_encode_display_text_roundtrips_known_menu_line(self) -> None:
        lines = decode_lines(ZH_MENU.read_bytes())
        decoded = decode_display_text(lines[6])
        encoded = encode_display_text(decoded)
        self.assertEqual(encoded, lines[6].rstrip(b"\r\n"))

    def test_startup_slot_prompt_bitmap_variants_exist(self) -> None:
        self.assertTrue((ZH_RENDER / "zh__txt_dialog__5__slot__1.png").exists())
        self.assertTrue((ZH_RENDER / "zh__txt_dialog__5__slot__99.png").exists())

    def test_startup_intro_placeholder_dialogs_have_rendered_bitmaps(self) -> None:
        manifest_entries = json.loads(ZH_RENDER_MANIFEST.read_text(encoding="utf-8"))
        manifest_keys = {
            (entry["filename"], int(entry["line"])): entry["text"]
            for entry in manifest_entries
        }

        self.assertIn(("txt_dialog", 20), manifest_keys)
        self.assertIn(("txt_dialog", 24), manifest_keys)
        self.assertTrue((ZH_RENDER / "zh__txt_dialog__20.png").exists())
        self.assertTrue((ZH_RENDER / "zh__txt_dialog__24.png").exists())

    def test_multi_page_story_dialogs_have_page_bitmaps(self) -> None:
        manifest_entries = json.loads(ZH_RENDER_MANIFEST.read_text(encoding="utf-8"))
        manifest_entry_keys = {entry.get("key") for entry in manifest_entries if entry.get("key")}

        for key in (
            "zh__txt_dialog__7887__page__1",
            "zh__txt_dialog__7887__page__2",
            "zh__txt_dialog__10693__page__1",
            "zh__txt_dialog__10693__page__2",
            "zh__txt_dialog__10694__page__1",
            "zh__txt_dialog__10694__page__2",
        ):
            self.assertIn(key, manifest_entry_keys)
            self.assertTrue((ZH_RENDER / f"{key}.png").exists())

    def test_pokedex_and_dynamic_ui_bitmaps_exist(self) -> None:
        manifest_entries = json.loads(ZH_RENDER_MANIFEST.read_text(encoding="utf-8"))
        manifest_keys = {entry.get("key") for entry in manifest_entries if entry.get("key")}
        manifest_lines = {
            (entry["filename"], int(entry["line"])): entry["text"]
            for entry in manifest_entries
        }

        self.assertIn(("dex_espec", 25), manifest_lines)
        self.assertIn(("dex_info", 25), manifest_lines)
        self.assertTrue((ZH_RENDER / "zh__dex_espec__25.png").exists())
        self.assertTrue((ZH_RENDER / "zh__dex_info__25.png").exists())

        for key in (
            "zh__txt_menu__683__par1raw__Z",
            "zh__txt_menu__684__par1raw__A",
            "zh__txt_menu__685__par1raw__X",
            "zh__txt_menu__686__par1__zh__txt_menu__1552",
            "zh__txt_menu__698__par1__zh__dex_espec__25",
            "zh__txt_menu__699__par1raw__1",
            "zh__txt_menu__549__par1raw__40",
            "zh__txt_menu__550__par1raw__20",
            "zh__txt_menu__550__par1raw__80",
            "zh__txt_menu__550__par1raw__100",
            "zh__txt_dialog__6838__par1__zh__txt_pkmn__25__page__1",
            "zh__txt_dialog__6838__par1__zh__txt_pkmn__25__page__2",
            "zh__txt_dialog__2561__par1__zh__txt_menu__1552__page__1",
            "zh__txt_dialog__2561__par1__zh__txt_menu__1552__page__2",
            "zh__txt_dialog__2561__par1__zh__txt_menu__1552__page__3",
            "zh__txt_dialog__6841__par1raw__Z__par2__zh__txt_menu__1552__page__1",
            "zh__txt_dialog__6841__par1raw__Z__par2__zh__txt_menu__1552__page__2",
            "zh__txt_dialog__6841__par1raw__Z__par2__zh__txt_menu__1552__page__3",
            "zh__txt_dialog__6841__par1raw__Z__par2__zh__txt_menu__1552__page__4",
            "zh__txt_menu__705__par1__zh__txt_pkmn__25",
            "zh__txt_menu__707__par1__zh__txt_pkmn__25",
            "zh__txt_menu__833__par1raw__M",
            "zh__txt_obj_desc__170__par1raw__M",
            "zh__txt_menu__1542__par1__zh__txt_attack__6",
            "zh__txt_dialog__2639__par1__zh__txt_pkmn__25",
            "zh__txt_dialog__2639__par1__zh__txt_obj__1",
            "zh__dex_info__25__page__1",
        ):
            self.assertIn(key, manifest_keys)
            self.assertTrue((ZH_RENDER / f"{key}.png").exists())

        for filename in (
            "zh__txt_menu__39.png",
            "zh__txt_menu__693.png",
            "zh__txt_menu__694.png",
            "zh__txt_menu__695.png",
            "zh__txt_menu__696.png",
            "zh__txt_menu__697.png",
            "zh__txt_menu__700.png",
            "zh__txt_menu__738.png",
            "zh__txt_menu__740.png",
            "zh__txt_menu__741.png",
            "zh__txt_menu__742.png",
            "zh__txt_menu__2119.png",
        ):
            self.assertTrue((ZH_RENDER / filename).exists())


if __name__ == "__main__":
    unittest.main()
