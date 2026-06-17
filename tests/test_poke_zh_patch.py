import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.poke_gm80 import load_game
from tools.poke_zh_patch import (
    DIALOGO_MULTIPLE_SOURCE,
    DIALOGO_SIMPLE_MULTIPLE_SOURCE,
    DRAW_GRAFITI_EXT_SOURCE,
    DRAW_TEXT_SHADOW_SOURCE,
    TEXT_PAR2_SOURCE,
    TEXT_PAR3_SOURCE,
    patch_uifix_incremental_runtime,
)

ROOT = Path(__file__).resolve().parents[1]


class ZhPatchSourceTests(unittest.TestCase):
    def test_draw_text_shadow_routes_mapped_zh_strings_to_bitmap_renderer(self) -> None:
        self.assertIn(
            'if(global.language="zh" && global.zh_text_key_map!=(-1) && ds_map_exists(global.zh_text_key_map,argument2)){',
            DRAW_TEXT_SHADOW_SOURCE,
        )
        self.assertIn(
            'ex(7028,argument2,argument0,argument1,argument3,fa_left,1);',
            DRAW_TEXT_SHADOW_SOURCE,
        )
        self.assertNotIn("draw_get_halign()", DRAW_TEXT_SHADOW_SOURCE)

    def test_draw_modal_base_keeps_centered_confirm_text_centered(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "tools" / "poke_zh_patch.py").read_text(encoding="utf-8")
        self.assertIn(
            'ex(7028,global.drawModalText,view_xview+122+offX,view_yview+global.drawModalOffset+offY,ex(5971,global.cuadrodialogo),fa_center,1);',
            source,
        )
        self.assertIn(
            'ex(7028,global.optionSelection[1],view_xview+120+offX,view_yview+107+offY,Col,fa_center,1);',
            source,
        )
        self.assertIn(
            'ex(7028,global.optionSelection[1],view_xview+69+offX,view_yview+107+offY,Col,fa_center,1);',
            source,
        )
        self.assertIn(
            'ex(7028,global.optionSelection[2],view_xview+170+offX,view_yview+107+offY,Col,fa_center,1);',
            source,
        )
        self.assertIn(
            'ex(7028,global.drawModalText,view_xview+122+offX,view_yview+descPosY+offY,ex(5973,global.cuadrodialogo),fa_center,1);',
            source,
        )
        self.assertIn(
            'ex(7028,global.drawModalMenuText,view_xview+120+offX,view_yview+107+offY,(16744448),fa_center,1);',
            source,
        )

    def test_draw_prior_modal_base_keeps_important_confirm_text_centered(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "tools" / "poke_zh_patch.py").read_text(encoding="utf-8")
        self.assertIn(
            'ex(7028,global.drawModalQuestionText,view_xview+122+offX,view_yview+global.drawModalQuestionOffset+offY,ex(5971,global.cuadrodialogo),fa_center,1);',
            source,
        )
        self.assertIn(
            'ex(7028,global.optionSelection[49],view_xview+69+offX,view_yview+107+offY,Col,fa_center,1);',
            source,
        )
        self.assertIn(
            'ex(7028,global.optionSelection[50],view_xview+170+offX,view_yview+107+offY,Col,fa_center,1);',
            source,
        )
        self.assertIn(
            'ex(7028,global.optionSelection[50],view_xview+120+offX,view_yview+107+offY,Col,fa_center,1);',
            source,
        )

    def test_text_par2_preserves_page_specific_suffixes_for_multi_page_dialogs(self) -> None:
        self.assertIn('if(!variable_global_exists("zh_text_page3_suffix"))global.zh_text_page3_suffix="";', TEXT_PAR2_SOURCE)
        self.assertIn('if(!variable_global_exists("zh_text_page4_suffix"))global.zh_text_page4_suffix="";', TEXT_PAR2_SOURCE)
        self.assertIn('global.zh_text_page3_suffix=""; global.zh_text_page4_suffix="";', TEXT_PAR2_SOURCE)
        self.assertIn('if(parametro1key!="")global.zh_text_page3_suffix="__par1__"+parametro1key;', TEXT_PAR2_SOURCE)
        self.assertIn('else global.zh_text_page3_suffix="__par1raw__"+parametro1;', TEXT_PAR2_SOURCE)
        self.assertIn('if(parametro2key!="")global.zh_text_page4_suffix="__par2__"+parametro2key;', TEXT_PAR2_SOURCE)
        self.assertIn('else global.zh_text_page4_suffix="__par2raw__"+parametro2;', TEXT_PAR2_SOURCE)

    def test_multi_page_dialogs_append_page_specific_suffixes(self) -> None:
        expected_key_lookup = 'base_key=ds_map_find_value(global.zh_text_key_map,argument0);'
        self.assertIn(expected_key_lookup, DIALOGO_MULTIPLE_SOURCE)
        self.assertIn(expected_key_lookup, DIALOGO_SIMPLE_MULTIPLE_SOURCE)
        self.assertNotIn('base_key=global.zh_text_last_key;', DIALOGO_MULTIPLE_SOURCE)
        self.assertNotIn('base_key=global.zh_text_last_key;', DIALOGO_SIMPLE_MULTIPLE_SOURCE)
        expected_page3 = 'if(page=3 && variable_global_exists("zh_text_page3_suffix") && global.zh_text_page3_suffix!="")key+=global.zh_text_page3_suffix;'
        expected_page4 = 'else if(page=4 && variable_global_exists("zh_text_page4_suffix") && global.zh_text_page4_suffix!="")key+=global.zh_text_page4_suffix;'
        self.assertIn(expected_page3, DIALOGO_MULTIPLE_SOURCE)
        self.assertIn(expected_page4, DIALOGO_MULTIPLE_SOURCE)
        self.assertIn(expected_page3, DIALOGO_SIMPLE_MULTIPLE_SOURCE)
        self.assertIn(expected_page4, DIALOGO_SIMPLE_MULTIPLE_SOURCE)

    def test_text_par3_records_all_parameter_suffixes_for_bitmap_lookup(self) -> None:
        self.assertIn('var texto, parametro1, parametro2, parametro3, textofinal, parametro1key, parametro2key, parametro3key, key, basekey;', TEXT_PAR3_SOURCE)
        self.assertIn('if(ds_map_exists(global.zh_text_key_map,texto))basekey=ds_map_find_value(global.zh_text_key_map,texto);', TEXT_PAR3_SOURCE)
        self.assertIn('if(ds_map_exists(global.zh_text_key_map,parametro1))parametro1key=ds_map_find_value(global.zh_text_key_map,parametro1);', TEXT_PAR3_SOURCE)
        self.assertIn('if(ds_map_exists(global.zh_text_key_map,parametro2))parametro2key=ds_map_find_value(global.zh_text_key_map,parametro2);', TEXT_PAR3_SOURCE)
        self.assertIn('if(ds_map_exists(global.zh_text_key_map,parametro3))parametro3key=ds_map_find_value(global.zh_text_key_map,parametro3);', TEXT_PAR3_SOURCE)
        self.assertIn('if(parametro1key!="")key+="__par1__"+parametro1key; else key+="__par1raw__"+parametro1;', TEXT_PAR3_SOURCE)
        self.assertIn('if(parametro2key!="")key+="__par2__"+parametro2key; else key+="__par2raw__"+parametro2;', TEXT_PAR3_SOURCE)
        self.assertIn('if(parametro3key!="")key+="__par3__"+parametro3key; else key+="__par3raw__"+parametro3;', TEXT_PAR3_SOURCE)

    def test_draw_grafiti_ext_can_compose_layout_backed_bitmap_sprites(self) -> None:
        self.assertIn('__layout.txt', DRAW_GRAFITI_EXT_SOURCE)
        self.assertIn('surface_create(totalw,totalh)', DRAW_GRAFITI_EXT_SOURCE)
        self.assertIn('sprite_create_from_surface(surf,0,0,totalw,totalh,0,0,0,0)', DRAW_GRAFITI_EXT_SOURCE)
        self.assertIn('draw_text(xpos,ypos,component_text);', DRAW_GRAFITI_EXT_SOURCE)

    def test_pokedex_moves_page_draws_level_and_move_name_in_separate_columns(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "tools" / "poke_zh_patch.py").read_text(encoding="utf-8")
        self.assertNotIn('ex(7028,ex(9928,1887),15,45+16*i,c_white,fa_left,1);', source)
        self.assertIn(
            'ex(6901,32,45+16*i,string(listaAtdxNv[posAtaque+i]),c_white,c_black,1);',
            source,
        )
        self.assertIn(
            'ex(7028,ex(8471,listaAtdx[posAtaque+i]),45,45+16*i,c_white,fa_left,1);',
            source,
        )
        self.assertIn(
            'ex(7028,ex(9935,txt_pb,ex(7818,PB!="0",PB,"--")),264,45+16*i,c_white,fa_right,1);',
            source,
        )
        self.assertIn(
            'ex(7028,ex(9935,txt_pp,PP),313,45+16*i,c_white,fa_right,1);',
            source,
        )

    def test_pokedex_stats_page_draws_single_row_labels_and_values(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "tools" / "poke_zh_patch.py").read_text(encoding="utf-8")
        self.assertIn(
            'ex(7028,ex(9928,803),49,40,c_white,fa_left,1);',
            source,
        )
        self.assertIn(
            'ex(6901,140,40,string(stat[0]),c_white,c_black,1);',
            source,
        )
        self.assertIn(
            'ex(7028,ex(9942,"txt_battle",353),49,145,c_white,fa_left,1);',
            source,
        )
        self.assertIn(
            'ex(7028,ex(9928,803),49,52,c_white,fa_left,1);',
            source,
        )
        self.assertIn(
            'ex(6901,140,142,string(stat_sinPP[6]),c_white,c_black,1);',
            source,
        )

    def test_bag_scripts_route_titles_items_and_descriptions_to_bitmap_renderer(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "tools" / "poke_zh_patch.py").read_text(encoding="utf-8")
        self.assertIn(
            'ex(7028,txt_obj,52,8,c_white,fa_center,1);',
            source,
        )
        self.assertIn(
            'ex(7028,txt_clave,52,8,c_white,fa_center,1);',
            source,
        )
        self.assertIn(
            'ex(7028,ex(8488,global.ObItem[i]),134,10+16*j,COLOR,fa_left,1);',
            source,
        )
        self.assertIn(
            'ex(7028,ex(8488,global.ObClave[i]),134,10+16*j,COLOR,fa_left,1);',
            source,
        )
        self.assertIn(
            'ex(7028,ex(5229,DESC,302,(3)),9,141,c_white,fa_left,1);',
            source,
        )

    def test_ball_bag_instance_branch_wraps_multi_statement_bitmap_draws(self) -> None:
        source = (ROOT / "tools" / "poke_zh_patch.py").read_text(encoding="utf-8")
        self.assertIn(
            "'{ex(7028,ex(5229,DESC,302,(3)),9,141,c_white,fa_left,1); "
            "ex(7028,ex(9935,txt_usa,txt_ball_safari),9,157,c_white,fa_left,1);}'",
            source,
        )
        self.assertIn(
            "'{ex(7028,ex(5229,DESC,222,(3)),9,141,c_white,fa_left,1); "
            "ex(7028,ex(9935,txt_usa,txt_ball_battle),9,157,c_white,fa_left,1);}'",
            source,
        )

    def test_evolution_arrow_text_uses_centered_bitmap_draw(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "tools" / "poke_zh_patch.py").read_text(encoding="utf-8")
        self.assertIn(
            'ex(7028,str,x,y-18,c_white,fa_center,1);',
            source,
        )

    def test_dex_info_pages_are_mapped_to_page_specific_bitmap_keys(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "tools" / "poke_zh_patch.py").read_text(encoding="utf-8")
        self.assertIn(
            'global.zh_text_last_key+"__page__1"',
            source,
        )
        self.assertIn(
            'global.zh_text_last_key+"__page__2"',
            source,
        )

    def test_home_menu_patch_keeps_cheat_aware_zh_title_assets(self) -> None:
        source = (ROOT / "tools" / "poke_zh_patch.py").read_text(encoding="utf-8")
        self.assertIn('var max_sel; if(global.cheat_enabled=1)max_sel=5; else max_sel=4;', source)
        self.assertIn('draw_sprite_ext(global.zh_menu_0,0,160,74,1,1,0,col1,1);', source)
        self.assertIn('if(max_sel=5){ draw_text_color(160,164,text_op6,col6,col6,col6,col6,1);', source)

    def test_battle_buffer_patch_composes_dash_joined_bitmap_keys(self) -> None:
        source = (ROOT / "tools" / "poke_zh_patch.py").read_text(encoding="utf-8")
        self.assertIn("patch_script_source(patched, 5211, ADD_TEXT_TO_BUFFER_SOURCE)", source)
        self.assertIn('dash_pos=string_pos(" - ",argument0);', source)
        self.assertIn('pair_key="zh__custom__pair_dash";', source)

    def test_battle_info_panel_draws_buffer_lines_with_bitmap_renderer(self) -> None:
        source = (ROOT / "tools" / "poke_zh_patch.py").read_text(encoding="utf-8")
        self.assertIn("patch_script_source(patched, 7089, DRAW_PANEL_INFORMATIVO_SOURCE)", source)
        self.assertIn('ex(7028,buffer[0],80,268+movimiento,(13160656),fa_left,ALPHA*movimiento/16);', source)
        self.assertIn('ex(7028,spr1,80,282,(13160656),fa_left,ALPHA);', source)

    def test_battle_shift_lists_draw_each_line_through_pair_dash_bitmap_layout(self) -> None:
        source = (ROOT / "tools" / "poke_zh_patch.py").read_text(encoding="utf-8")
        self.assertIn('ex(7028,line_text,view_xview+112,line_y,c_white,fa_left,0.9);', source)
        self.assertIn('ex(7028,line_text,view_xview+464,line_y,c_white,fa_right,0.9);', source)
        self.assertIn('pair_key="zh__custom__pair_dash";', source)

    def test_moves_menu_uses_small_consistent_pp_labels(self) -> None:
        source = (ROOT / "tools" / "poke_zh_patch.py").read_text(encoding="utf-8")
        self.assertIn('draw_set_font((3)); for(i=0;i<=3;i+=1){ ex(6901,281,30+i*16,"PP",0,(13160656),1);}', source)

    def test_patch_uifix_incremental_runtime_includes_version_bypass_and_save_isolation(self) -> None:
        source = (ROOT / "tools" / "poke_zh_patch.py").read_text(encoding="utf-8")
        self.assertIn('STARTUP_VALIDATION_BYPASS_SOURCE = "return 1; "', source)
        self.assertIn(r'SAVE_ISOLATION_NEW_PREFIX = r"data\partidas\reloaded_zhcn_"', source)
        self.assertIn("patched = _apply_startup_and_save_isolation_patches(patched)", source)

    def test_committed_zh_uifix_exe_includes_incremental_runtime_patches(self) -> None:
        source_exe = ROOT / "Proyecto Reloaded The Last Beta 1.9.1 Full.zh-cn.uifix.exe"
        game = load_game(source_exe)

        self.assertEqual(game.get_script(10054).source, "return 1; ")
        self.assertIn("global.zh_menu_0", game.get_script(7038).source)
        self.assertIn('pair_key="zh__custom__pair_dash";', game.get_script(5211).source)
        self.assertIn('ex(7028,buffer[0],80,268+movimiento,(13160656),fa_left,ALPHA*movimiento/16);', game.get_script(7089).source)
        self.assertIn('ex(7028,line_text,view_xview+112,line_y,c_white,fa_left,0.9);', game.get_script(7013).source)
        self.assertIn('ex(7028,line_text,view_xview+464,line_y,c_white,fa_right,0.9);', game.get_script(7014).source)
        self.assertIn('draw_set_font((3)); for(i=0;i<=3;i+=1){ ex(6901,281,30+i*16,"PP",0,(13160656),1);}', game.get_script(7077).source)
        for script_index in (7477, 7657, 7680, 7759, 7981, 7993, 8008, 8243, 8613, 9200, 9201, 9440, 9624, 9777, 9779):
            self.assertIn('data\\partidas\\reloaded_zhcn_', game.get_script(script_index).source)
        self.assertIn('if(fileVersion>global.currentVersion){ex(8521,1);exit;}', game.get_script(8244).source)
        self.assertIn('if(global.currentVersion>ex(7584,(0))){ ex(9744,ex(9928,2101));game_restart();exit;}', game.get_script(7759).source)


if __name__ == "__main__":
    unittest.main()
