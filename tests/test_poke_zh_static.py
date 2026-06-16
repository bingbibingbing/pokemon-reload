from pathlib import Path
import unittest

from tools.poke_zh_static import (
    build_dynamic_manifest_entries,
    build_static_manifest_entries,
    build_term_regex,
    is_static_renderable,
    mask_known_terms,
    translate_place_name,
    translate_item_name,
    translate_pokemon_name,
    unmask_known_terms,
    wrap_text_to_width,
)


class ZhStaticBuildTests(unittest.TestCase):
    def test_is_static_renderable_rejects_placeholder_lines(self) -> None:
        self.assertTrue(is_static_renderable("New game"))
        self.assertTrue(is_static_renderable("Exit game?#All unsaved data will be lost."))
        self.assertFalse(is_static_renderable("$par1$ learned $par2$."))
        self.assertFalse(is_static_renderable("   "))

    def test_mask_and_unmask_terms_prefer_longest_match(self) -> None:
        glossary = [
            ("Fire Blast", "大字爆炎"),
            ("Fire", "火"),
            ("Pokémon", "宝可梦"),
        ]
        term_regex = build_term_regex(glossary)

        masked, replacements = mask_known_terms(
            "Teach Fire Blast to your Pokémon.",
            glossary,
            term_regex,
        )
        self.assertNotIn("Fire Blast", masked)
        self.assertNotIn("Pokémon", masked)
        self.assertIn("ZZHTERM", masked)

        restored = unmask_known_terms("教会ZZHTERM0000ZZ给你的ZZHTERM0001ZZ。", replacements)
        self.assertEqual(restored, "教会大字爆炎给你的宝可梦。")

    def test_mask_known_terms_does_not_match_inside_larger_words(self) -> None:
        glossary = [
            ("Absorb", "吸取"),
            ("Art", "艺术"),
        ]
        term_regex = build_term_regex(glossary)
        masked, replacements = mask_known_terms("Absorbs sunlight before Restart.", glossary, term_regex)
        self.assertEqual(masked, "Absorbs sunlight before Restart.")
        self.assertEqual(replacements, {})

    def test_wrap_text_to_width_adds_breaks_for_long_lines(self) -> None:
        wrapped = wrap_text_to_width("这是一个很长的中文句子用于测试自动换行是否会在较窄宽度下插入断行。", 96)
        self.assertIn("#", wrapped)

    def test_translate_pokemon_name_handles_special_forms(self) -> None:
        species_map = {
            "Bulbasaur": "妙蛙种子",
            "Charizard": "喷火龙",
            "Mr. Mime": "魔墙人偶",
        }
        self.assertEqual(translate_pokemon_name("Bulbasaur", species_map), "妙蛙种子")
        self.assertEqual(translate_pokemon_name("Mega Charizard X", species_map), "超级喷火龙X")
        self.assertEqual(translate_pokemon_name("Charizard Gigamax", species_map), "喷火龙 超极巨化")
        self.assertEqual(translate_pokemon_name("Mr. Mime", species_map), "魔墙人偶")

    def test_translate_item_name_uses_exact_match_then_species_fallback(self) -> None:
        item_map = {
            "Master Ball": "大师球",
        }
        species_map = {
            "Venusaur": "妙蛙花",
            "Lucario": "路卡利欧",
            "Tatsugiri": "米立龙",
        }
        self.assertEqual(translate_item_name("Master Ball", item_map, species_map), "大师球")
        self.assertEqual(translate_item_name("Venusaurite", item_map, species_map), "妙蛙花进化石")
        self.assertEqual(translate_item_name("Lucarionite Z", item_map, species_map), "路卡利欧进化石Z")
        self.assertEqual(translate_item_name("Tatsugirite", item_map, species_map), "米立龙进化石")

    def test_translate_place_name_handles_routes_and_floors(self) -> None:
        self.assertEqual(translate_place_name("Route 1"), "1号道路")
        self.assertEqual(translate_place_name("(Upper Floor)"), "（上层）")
        self.assertEqual(translate_place_name("(Middle Floor)"), "（中层）")
        self.assertEqual(translate_place_name("(Lower Floor)"), "（下层）")

    def test_build_static_manifest_entries_skips_dynamic_lines(self) -> None:
        def fake_translate(text: str) -> str:
            return {
                "New game": "新游戏",
                "This is a long line for wrapping.": "这是一条用于测试自动换行的较长中文句子。",
            }[text]

        entries = build_static_manifest_entries(
            "zh",
            "txt_menu",
            [
                "New game",
                "$par1$ learned $par2$.",
                "This is a long line for wrapping.",
                "   ",
            ],
            fake_translate,
            max_width=96,
        )

        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["line"], 1)
        self.assertEqual(entries[0]["text"], "新游戏")
        self.assertEqual(entries[1]["line"], 3)
        self.assertIn("#", entries[1]["text"])

    def test_build_dynamic_manifest_entries_covers_pokedex_templates(self) -> None:
        translated_pack_lines = {
            "txt_menu": [""] * 1608,
            "txt_dialog": [""] * 2639,
            "txt_pkmn": ["妙蛙种子", "皮卡丘"],
            "txt_obj": ["精灵球", "地图"],
            "dex_espec": ["种子", "鼠"],
        }
        translated_pack_lines["txt_menu"][1551] = "F1"

        entries = build_dynamic_manifest_entries(translated_pack_lines)
        by_key = {str(entry["key"]): str(entry["text"]) for entry in entries}

        self.assertEqual(by_key["zh__txt_dialog__5__slot__1"], "已分配槽位 1#按 Z 继续。")
        self.assertEqual(by_key["zh__txt_menu__699__par1raw__1"], "第1页")
        self.assertEqual(by_key["zh__txt_menu__683__par1raw__Z"], "Z - 页面")
        self.assertEqual(by_key["zh__txt_menu__686__par1__zh__txt_menu__1552"], "F1 - 帮助")
        self.assertEqual(by_key["zh__txt_menu__698__par1__zh__dex_espec__2"], "鼠宝可梦")
        self.assertEqual(by_key["zh__txt_menu__705__par1__zh__txt_pkmn__2"], "皮卡丘的一般能力值。")
        self.assertEqual(by_key["zh__txt_menu__707__par1__zh__txt_pkmn__2"], "皮卡丘升级可学会的招式。")
        self.assertEqual(by_key["zh__txt_dialog__2639__par1__zh__txt_pkmn__2"], "你获得了皮卡丘。")
        self.assertEqual(by_key["zh__txt_dialog__2639__par1__zh__txt_obj__2"], "你获得了地图。")


if __name__ == "__main__":
    unittest.main()
