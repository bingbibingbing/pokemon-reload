from pathlib import Path
import unittest

from tools.poke_zh_static import (
    SOURCE_OVERRIDES,
    build_dynamic_layout_assets,
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

    def test_source_overrides_use_short_labels_for_dense_ui(self) -> None:
        expected = {
            "INFO.": "信息",
            "AREA": "地区",
            "EVOL.": "进化",
            "MOV.": "招式",
            "STATS": "能力",
            "ADD.": "附加",
            "Pokémon Info.": "宝可梦资料",
            "Pokémon Abil.": "宝可梦特性",
            "Battle Moves": "战斗招式",
            "Type A": "属性1",
            "Type B": "属性2",
            "Stats": "能力",
            "Experience": "经验",
            "Exp. Points": "经验值",
            "Next Lv": "下一级",
            "Exp.": "经验",
            "ATTACK": "攻击",
            "DEFENSE": "防御",
            "SP. AT.": "特攻",
            "SP. DEF.": "特防",
            "SPEED": "速度",
            "Stats detail": "能力详情",
            "Instruction Values": "努力值",
            "Natural Talents Values": "个体值",
            "HP:#PP:#Attack:#Defense:#Special At.:#Special Def.:#Speed:#Total:": "HP:#PP:#攻击:#防御:#特攻:#特防:#速度:#总量:",
            "HP:#Attack:#Defense:#Special At.:#Special Def.:#Speed:#Total:": "HP:#攻击:#防御:#特攻:#特防:#速度:#总量:",
            "Health points (HP):#Attack:#Defense:#Spec. Atk.:#Spec. Def.:#Speed:": "HP值:#攻击:#防御:#特攻:#特防:#速度:",
        }

        for source, translated in expected.items():
            self.assertEqual(SOURCE_OVERRIDES[source], translated)

    def test_source_overrides_cover_bag_and_species_quality_fixes(self) -> None:
        expected = {
            "Mouse": "鼠",
            "Key Items": "重要道具",
            "Level": "等级",
            "A map. Press $par1$ to use it.": "地图。#按$par1$使用。",
        }

        for source, translated in expected.items():
            self.assertEqual(SOURCE_OVERRIDES[source], translated)

    def test_build_dynamic_manifest_entries_covers_pokedex_templates(self) -> None:
        translated_pack_lines = {
            "txt_menu": [""] * 2200,
            "txt_dialog": [""] * 6841,
            "txt_pkmn": ["妙蛙种子", "皮卡丘"],
            "txt_attack": ["电击", "叫声"],
            "txt_obj": ["精灵球", "地图"],
            "dex_espec": ["种子", "鼠"],
            "dex_info": [""] * 25,
        }
        translated_pack_lines["txt_menu"][223] = "（雄性）"
        translated_pack_lines["txt_menu"][225] = "（雌性）"
        translated_pack_lines["txt_menu"][1551] = "F1"
        translated_pack_lines["dex_info"][24] = "第一页甲#第一页乙#第一页丙#第二页甲#第二页乙"

        entries = build_dynamic_manifest_entries(translated_pack_lines)
        by_key = {str(entry["key"]): str(entry["text"]) for entry in entries}
        entries_by_key = {str(entry["key"]): entry for entry in entries}

        self.assertEqual(by_key["zh__txt_dialog__5__slot__1"], "已分配槽位 1#按 Z 继续。")
        self.assertEqual(by_key["zh__txt_menu__699__par1raw__1"], "第1页")
        self.assertEqual(by_key["zh__txt_menu__683__par1raw__Z"], "Z翻页")
        self.assertEqual(by_key["zh__txt_menu__686__par1__zh__txt_menu__1552"], "F1帮助")
        self.assertEqual(by_key["zh__txt_menu__698__par1__zh__dex_espec__2"], "鼠宝可梦")
        self.assertEqual(by_key["zh__txt_menu__215__par1__zh__txt_pkmn__2"], "皮卡丘的数据已更新。")
        self.assertEqual(by_key["zh__txt_menu__705__par1__zh__txt_pkmn__2"], "皮卡丘的基础数据")
        self.assertEqual(by_key["zh__txt_menu__707__par1__zh__txt_pkmn__2"], "皮卡丘的升级招式")
        self.assertEqual(by_key["zh__txt_menu__1542__par1__zh__txt_attack__2"], "进化：叫声")
        self.assertEqual(by_key["zh__txt_menu__549__par1raw__40"], "威:40")
        self.assertEqual(by_key["zh__txt_menu__550__par1raw__20"], "PP:20")
        self.assertEqual(by_key["zh__txt_menu__550__par1raw__80"], "PP:80")
        self.assertEqual(by_key["zh__txt_menu__550__par1raw__100"], "PP:100")
        self.assertEqual(by_key["zh__txt_menu__550__par1raw__--"], "PP:--")
        self.assertEqual(entries_by_key["zh__txt_menu__549__par1raw__40"]["font_size"], 12)
        self.assertEqual(entries_by_key["zh__txt_menu__550__par1raw__80"]["font_size"], 12)
        self.assertEqual(by_key["zh__txt_menu__832__par1raw__M"], "按M分配这个树果。")
        self.assertEqual(by_key["zh__txt_menu__833__par1raw__M"], "按M使用。")
        self.assertEqual(by_key["zh__txt_obj_desc__170__par1raw__M"], "地图。#按M使用。")
        self.assertEqual(by_key["zh__dex_info__25__page__1"], "第一页甲#第一页乙#第一页丙")
        self.assertEqual(by_key["zh__dex_info__25__page__2"], "第二页甲#第二页乙")
        self.assertEqual(by_key["zh__txt_menu__795__par1__zh__txt_pkmn__2"], "离开 - 皮卡丘")
        self.assertEqual(by_key["zh__txt_menu__821__par1__zh__txt_pkmn__2"], "资料 - 皮卡丘")
        self.assertEqual(by_key["zh__txt_dialog__2639__par1__zh__txt_pkmn__2"], "你获得了皮卡丘。")
        self.assertEqual(by_key["zh__txt_dialog__2639__par1__zh__txt_obj__2"], "你获得了地图。")
        self.assertEqual(by_key["zh__txt_dialog__4501__par1__zh__txt_obj__2"], "你找到了地图。")
        self.assertEqual(by_key["zh__txt_dialog__6834__par1__zh__txt_pkmn__2"], "这只宝可梦是皮卡丘。")
        self.assertEqual(by_key["zh__txt_dialog__6837__par1__zh__txt_pkmn__2"], "你获得了皮卡丘。")
        self.assertEqual(by_key["zh__txt_dialog__6837__par1__zh__txt_obj__2"], "你获得了地图。")
        self.assertEqual(
            by_key["zh__txt_dialog__1499__par1raw__Z__par2raw__X"],
            "你好，训练家。#按Z可以查看宝可梦资料。#按X可以把它从精灵球里放出来。",
        )
        self.assertEqual(
            by_key["zh__txt_dialog__1513__par1__zh__txt_menu__1552__par2raw__X"],
            "对战开始时，首位宝可梦会上场。#按F1选择首位宝可梦，选中后按X确认。",
        )
        self.assertEqual(
            by_key["zh__txt_menu__220__par1__zh__txt_pkmn__2__par2__zh__txt_menu__224"],
            "要给皮卡丘（雄性）取昵称吗？",
        )
        self.assertEqual(
            by_key["zh__txt_menu__220__par1__zh__txt_pkmn__2__par2__zh__txt_menu__226"],
            "要给皮卡丘（雌性）取昵称吗？",
        )
        self.assertEqual(
            by_key["zh__txt_dialog__2561__par1__zh__txt_menu__1552__page__1"],
            "你好，训练家！我们一直在等你。",
        )
        self.assertEqual(
            by_key["zh__txt_dialog__2561__par1__zh__txt_menu__1552__page__2"],
            "昨天我给了你训练家手册，希望你已经认真看过了。",
        )
        self.assertEqual(
            by_key["zh__txt_dialog__2561__par1__zh__txt_menu__1552__page__3"],
            "按F1就能查看它。",
        )
        self.assertEqual(
            by_key["zh__txt_dialog__6841__par1raw__Z__par2__zh__txt_menu__1552__page__1"],
            "随身带上一些总是很重要。",
        )
        self.assertEqual(
            by_key["zh__txt_dialog__6841__par1raw__Z__par2__zh__txt_menu__1552__page__2"],
            "有了它们，你就能捕捉野生宝可梦。",
        )
        self.assertEqual(
            by_key["zh__txt_dialog__6841__par1raw__Z__par2__zh__txt_menu__1552__page__3"],
            "对战中，按Z就能把它们投出去。",
        )
        self.assertEqual(
            by_key["zh__txt_dialog__6841__par1raw__Z__par2__zh__txt_menu__1552__page__4"],
            "抓到宝可梦后，按F1就能在图鉴里查看信息。",
        )
        self.assertEqual(
            by_key["zh__txt_dialog__6838__par1__zh__txt_pkmn__2__page__1"],
            "皮卡丘……",
        )
        self.assertEqual(
            by_key["zh__txt_dialog__6838__par1__zh__txt_pkmn__2__page__2"],
            "不错的选择！",
        )
        self.assertEqual(by_key["zh__txt_dialog__6841__page__3__par1raw__Z"], "对战时，按Z投出它们。")
        self.assertEqual(
            by_key["zh__txt_dialog__6841__page__4__par2__zh__txt_menu__1552"],
            "如果你捕捉到宝可梦，按F1打开图鉴查看信息。",
        )

    def test_build_dynamic_layout_assets_cover_generic_placeholder_templates(self) -> None:
        source_pack_lines = {
            "txt_character": [""] * 978,
            "txt_obj_desc": [""] * 170,
            "txt_dialog": [""] * 2504,
            "txt_battle": [""] * 195,
        }
        source_pack_lines["txt_character"][977] = "$par1$'s mom"
        source_pack_lines["txt_obj_desc"][159] = "A cellphone. Press $par1$ to use it."
        source_pack_lines["txt_dialog"][2503] = "Remember, you can use the Phone by pressing $par1$!"
        source_pack_lines["txt_battle"][194] = "$par1$ used $par2$."

        translations = {
            ("txt_character", "$par1$'s mom"): "$par1$的妈妈",
            ("txt_obj_desc", "A cellphone. Press $par1$ to use it."): "手机。#按$par1$使用。",
            ("txt_dialog", "Remember, you can use the Phone by pressing $par1$!"): "记住，按$par1$就能使用手机！",
            ("txt_battle", "$par1$ used $par2$."): "$par1$使用了$par2$。",
        }

        def translate_template(filename: str, text: str) -> str | None:
            return translations.get((filename, text))

        entries, layouts = build_dynamic_layout_assets("zh", source_pack_lines, translate_template)
        by_key = {str(entry["key"]): str(entry["text"]) for entry in entries}

        self.assertEqual(by_key["zh__txt_character__978__seg__1"], "的妈妈")
        self.assertEqual(layouts["zh__txt_character__978"], "w290|par1|seg1")
        self.assertEqual(by_key["zh__txt_obj_desc__160__seg__1"], "手机。")
        self.assertEqual(by_key["zh__txt_obj_desc__160__seg__2"], "按")
        self.assertEqual(by_key["zh__txt_obj_desc__160__seg__3"], "使用。")
        self.assertEqual(layouts["zh__txt_obj_desc__160"], "w290|seg1|br|seg2|par1|seg3")
        self.assertEqual(by_key["zh__txt_dialog__2504__seg__1"], "记住，按")
        self.assertEqual(by_key["zh__txt_dialog__2504__seg__2"], "就能使用手机！")
        self.assertEqual(layouts["zh__txt_dialog__2504"], "w290|seg1|par1|seg2")
        self.assertEqual(by_key["zh__txt_battle__195__seg__1"], "使用了")
        self.assertEqual(by_key["zh__txt_battle__195__seg__2"], "。")
        self.assertEqual(layouts["zh__txt_battle__195"], "w290|par1|seg1|par2|seg2")
        self.assertEqual(by_key["zh__custom__pair_dash__seg__1"], " - ")
        self.assertEqual(layouts["zh__custom__pair_dash"], "w0|par1|seg1|par2")


if __name__ == "__main__":
    unittest.main()
