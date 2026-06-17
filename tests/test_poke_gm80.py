from pathlib import Path
import tempfile
import unittest

from tools.poke_gm80 import (
    extract_encrypted_game_blob,
    encrypt_game_blob,
    load_game,
    patch_script_batch,
    patch_script_source,
    patch_script_source_replace,
)
from tools.poke_zh_patch import patch_dialog_bitmap_runtime


ROOT = Path(__file__).resolve().parents[1]
GAME_EXE = ROOT / "Proyecto Reloaded The Last Beta 1.9.1 Full.exe"


class Gm80ResourceTests(unittest.TestCase):
    def test_load_game_detects_gm80_runner(self) -> None:
        game = load_game(GAME_EXE)
        self.assertEqual(game.runner_version, 800)
        self.assertEqual(game.script_count, 10198)

    def test_load_game_extracts_known_font_metadata(self) -> None:
        game = load_game(GAME_EXE)
        self.assertEqual(len(game.fonts), 27)

        first_font = game.fonts[0]
        self.assertIsNotNone(first_font)
        assert first_font is not None
        self.assertEqual(first_font.name, "Fuente1")
        self.assertEqual(first_font.font_name, "Arial")
        self.assertEqual(first_font.size, 10)
        self.assertEqual(first_font.range_begin, 0)
        self.assertEqual(first_font.range_end, 255)

    def test_load_game_extracts_text_reader_script(self) -> None:
        game = load_game(GAME_EXE)
        script = game.get_script(9942)
        self.assertEqual(script.name, "TextReader")
        self.assertIn('file_text_open_read("data\\text\\"+folder+"\\"+filename+".dll")', script.source)
        self.assertIn("txt_final+=chr(ex(10060,ord(string_char_at(txt,i))))", script.source)

    def test_load_game_extracts_dialog_script(self) -> None:
        game = load_game(GAME_EXE)
        script = game.get_script(6834)
        self.assertEqual(script.name, "Dialogo")
        self.assertIn("string_width(argument0)>ANCHO", script.source)
        self.assertIn("global.drawModalSystem=(6834)", script.source)

    def test_load_game_extracts_startup_selection_objects(self) -> None:
        game = load_game(GAME_EXE)
        self.assertGreater(game.object_count, 0)
        object_names = {resource.name for resource in game.objects.values()}
        self.assertIn("obj_black", object_names)
        self.assertIn("obj_ProtaSEL", object_names)
        self.assertIn("obj_RivalSEL", object_names)

    def test_encrypt_game_blob_roundtrips_original_runner_payload(self) -> None:
        raw = GAME_EXE.read_bytes()
        blob = extract_encrypted_game_blob(raw)
        rebuilt = encrypt_game_blob(blob.decrypted_data, blob.forward_table)
        self.assertEqual(rebuilt, blob.encrypted_data)

    def test_patch_script_source_replace_updates_text_menu_lookup(self) -> None:
        raw = GAME_EXE.read_bytes()
        patched = patch_script_source_replace(raw, 9928, "txt_menu", "txt_pkmn")

        with tempfile.TemporaryDirectory() as temp_dir:
            patched_exe = Path(temp_dir) / GAME_EXE.name
            patched_exe.write_bytes(patched)
            game = load_game(patched_exe)

        script = game.get_script(9928)
        self.assertEqual(script.name, "TextMenu")
        self.assertIn('"txt_pkmn"', script.source)
        self.assertNotIn('"txt_menu"', script.source)

    def test_patch_script_source_replaces_entire_text_menu_script(self) -> None:
        raw = GAME_EXE.read_bytes()
        new_source = "return chr(214)+chr(208)+chr(206)+chr(196); "
        patched = patch_script_source(raw, 9928, new_source)

        with tempfile.TemporaryDirectory() as temp_dir:
            patched_exe = Path(temp_dir) / GAME_EXE.name
            patched_exe.write_bytes(patched)
            game = load_game(patched_exe)

        script = game.get_script(9928)
        self.assertEqual(script.name, "TextMenu")
        self.assertEqual(script.source, new_source)

    def test_patch_script_batch_updates_multiple_scripts_in_one_pass(self) -> None:
        raw = GAME_EXE.read_bytes()
        patched = patch_script_batch(
            raw,
            source_updates={9928: "return 7; "},
            replace_updates={9942: [("txt_final", "txt_ready")]},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            patched_exe = Path(temp_dir) / GAME_EXE.name
            patched_exe.write_bytes(patched)
            game = load_game(patched_exe)

        self.assertEqual(game.get_script(9928).source, "return 7; ")
        self.assertIn("var f, i, txt, txt_ready", game.get_script(9942).source)

    def test_patch_dialog_bitmap_runtime_updates_text_reader_cache(self) -> None:
        raw = GAME_EXE.read_bytes()
        patched = patch_dialog_bitmap_runtime(raw)

        with tempfile.TemporaryDirectory() as temp_dir:
            patched_exe = Path(temp_dir) / GAME_EXE.name
            patched_exe.write_bytes(patched)
            game = load_game(patched_exe)

        text_reader = game.get_script(9942)
        self.assertIn('if(!variable_global_exists("zh_text_key_map"))global.zh_text_key_map=(-1);', text_reader.source)
        self.assertIn('if(!variable_global_exists("zh_text_last_key"))global.zh_text_last_key="";', text_reader.source)
        self.assertIn('global.zh_text_last_key=folder+"__"+filename+"__"+string(line);', text_reader.source)
        self.assertIn("global.zh_text_key_map=ds_map_create();", text_reader.source)
        self.assertIn("ds_map_replace(global.zh_text_key_map,txt_final,global.zh_text_last_key);", text_reader.source)

    def test_patch_dialog_bitmap_runtime_updates_dialog_renderers(self) -> None:
        raw = GAME_EXE.read_bytes()
        patched = patch_dialog_bitmap_runtime(raw)

        with tempfile.TemporaryDirectory() as temp_dir:
            patched_exe = Path(temp_dir) / GAME_EXE.name
            patched_exe.write_bytes(patched)
            game = load_game(patched_exe)

        draw_grafiti_ext = game.get_script(7028)
        dialogo = game.get_script(6834)
        modal_base = game.get_script(7076)
        draw_text_shadow = game.get_script(6901)
        dialogo_selection_draw = game.get_script(6983)
        init_inicio = game.get_script(7879)
        draw_inicio = game.get_script(7038)
        text_menu = game.get_script(9928)
        text_par1 = game.get_script(9935)
        dialogo_multiple = game.get_script(6841)
        dialogo_simple_multiple = game.get_script(6848)
        draw_text_shadow = game.get_script(6901)
        selection_big = game.get_script(7578)
        selection_small = game.get_script(7666)
        selection_special = game.get_script(7672)
        prota_selection_draw = game.get_script(7124)
        rival_selection_draw = game.get_script(7135)
        self.assertIn('if(!variable_global_exists("zh_text_key_map"))global.zh_text_key_map=(-1);', text_menu.source)
        self.assertNotIn("draw_get_halign()", draw_text_shadow.source)
        self.assertIn('ex(7028,str,letraX,letraY,c_white,fa_left,1);', dialogo_selection_draw.source)
        self.assertIn('global.zh_menu_0=(-1);global.zh_menu_1=(-1);global.zh_menu_2=(-1);global.zh_menu_3=(-1);global.zh_menu_4=(-1);', init_inicio.source)
        self.assertIn('if(!variable_global_exists("zh_menu_0"))global.zh_menu_0=(-1);', draw_inicio.source)
        self.assertIn('if(global.language="zh" && sprite_exists(global.zh_menu_0)', draw_inicio.source)
        self.assertIn('path=working_directory+"\\\\data\\\\text\\\\zh\\\\render\\\\"+key+".png";', draw_grafiti_ext.source)
        self.assertIn("base_key=global.zh_text_last_key;", dialogo_multiple.source)
        self.assertIn('key=base_key+"__page__"+string(page);', dialogo_multiple.source)
        self.assertIn("ex(6834,text_page,argument1,argument2);", dialogo_multiple.source)
        self.assertIn("base_key=global.zh_text_last_key;", dialogo_simple_multiple.source)
        self.assertIn('key=base_key+"__page__"+string(page);', dialogo_simple_multiple.source)
        self.assertIn("ex(6846,text_page);", dialogo_simple_multiple.source)
        self.assertIn('if(global.zh_text_last_key="zh__txt_dialog__5")key=global.zh_text_last_key+"__slot__"+parametro1;', text_par1.source)
        self.assertIn('if(global.language="zh" && global.zh_text_key_map!=(-1) && ds_map_exists(global.zh_text_key_map,argument[0])){', selection_big.source)
        self.assertIn('if(global.language="zh"){ global.drawModalText=text; ex(9774,1); } else for(i=1;i<=ex(9827,text);i+=1){', selection_big.source)
        self.assertIn('if(global.language="zh" && global.zh_text_key_map!=(-1) && ds_map_exists(global.zh_text_key_map,argument[0])){', selection_small.source)
        self.assertIn('if(global.language="zh"){ global.drawModalText=text; ex(9774,1); } else for(i=1;i<=ex(9827,text);i+=1){', selection_small.source)
        self.assertIn('if(global.language="zh" && global.zh_text_key_map!=(-1) && ds_map_exists(global.zh_text_key_map,argument[0])){', selection_special.source)
        self.assertIn('if(global.language="zh"){ global.drawModalText=text; ex(9774,1); } else for(i=1;i<=ex(9827,argument[0]);i+=1){', selection_special.source)
        self.assertIn('else ex(7028,global.protaname,x,y+42,c_white,fa_center,1);', prota_selection_draw.source)
        self.assertIn('else ex(7028,global.rivalname,x,y+42,c_white,fa_center,1);', rival_selection_draw.source)
        self.assertIn('ex(7028,global.optionSelection[i],view_xview+114+offX,view_yview+global.drawModalOffset+offY,Col,fa_center,1);', modal_base.source)
        self.assertIn('ex(7028,global.drawModalMenuText,view_xview+114+offX,view_yview+global.drawModalOffset+offY,Col,fa_center,1);', modal_base.source)
        self.assertIn("key=ds_map_find_value(global.zh_text_key_map,st);", draw_grafiti_ext.source)
        self.assertIn("if(ds_map_exists(global.zh_sprite_cache,key))spr=ds_map_find_value(global.zh_sprite_cache,key);", draw_grafiti_ext.source)
        self.assertIn("draw_sprite_ext(spr,0,drawX,Y,1,1,0,col,alpha);", draw_grafiti_ext.source)
        self.assertIn('if(global.language="zh"){ global.drawModalText=argument0; ex(9774,global.vel_text); }', dialogo.source)
        self.assertIn("ex(7028,global.drawModalText,view_xview+15,view_yview+142,global.colordialogo,fa_left,1);", modal_base.source)
        self.assertIn(
            "ex(7028,global.drawModalText,view_xview+122+offX,view_yview+global.drawModalOffset+offY,ex(5971,global.cuadrodialogo),fa_center,1);",
            modal_base.source,
        )
        self.assertIn(
            "ex(7028,global.drawModalText,view_xview+122+offX,view_yview+descPosY+offY,ex(5973,global.cuadrodialogo),fa_center,1);",
            modal_base.source,
        )
        self.assertIn('if(global.language="zh" && global.zh_text_key_map!=(-1) && ds_map_exists(global.zh_text_key_map,argument2)){', draw_text_shadow.source)
        self.assertIn('ex(7028,argument2,argument0,argument1,argument3,fa_left,1);', draw_text_shadow.source)

    def test_patch_dialog_bitmap_runtime_covers_dex_and_pokedex_ui(self) -> None:
        raw = GAME_EXE.read_bytes()
        patched = patch_dialog_bitmap_runtime(raw)

        with tempfile.TemporaryDirectory() as temp_dir:
            patched_exe = Path(temp_dir) / GAME_EXE.name
            patched_exe.write_bytes(patched)
            game = load_game(patched_exe)

        cargar_strings = game.get_script(5641)
        ajustar_texto = game.get_script(5229)
        text_cartel = game.get_script(9919)
        dex_especie = game.get_script(6814)
        dex_info = game.get_script(6819)
        draw_buttons = game.get_script(6948)
        draw_cartel = game.get_script(6956)
        draw_detail = game.get_script(6982)

        self.assertIn('if(global.language="zh"){ if(global.zh_text_key_map=(-1))global.zh_text_key_map=ds_map_create();', cargar_strings.source)
        self.assertIn('ds_map_add(global.zh_text_key_map,global.STR_POK[i],"zh__txt_pkmn__"+string(i));', cargar_strings.source)
        self.assertIn('ds_map_add(global.zh_text_key_map,global.STR_ATK[i],"zh__txt_attack__"+string(i));', cargar_strings.source)
        self.assertIn('ds_map_add(global.zh_text_key_map,global.STR_OBJ[i],"zh__txt_obj__"+string(i));', cargar_strings.source)
        self.assertIn('ds_map_add(global.zh_text_key_map,global.STR_HAB[i],"zh__txt_abilities__"+string(i));', cargar_strings.source)
        self.assertIn('ds_map_exists(global.zh_text_key_map,argument0)', ajustar_texto.source)
        self.assertIn('ds_map_add(global.zh_text_key_map,info,key);', ajustar_texto.source)
        self.assertIn('ds_map_exists(global.zh_text_key_map,txt)', text_cartel.source)
        self.assertIn('ex(9942,"dex_espec",PK)', dex_especie.source)
        self.assertIn('ex(9942,"dex_info",PK)', dex_info.source)
        self.assertIn('ex(7028,txt_op1,x+3,y+1,col1,fa_left,1);', draw_buttons.source)
        self.assertIn('ex(7028,spr,view_xview+15,view_yview+142,global.colordialogo,fa_left,1);', draw_cartel.source)
        self.assertIn('ex(7028,txt_help1,3,18,c_white,fa_left,1);', draw_detail.source)
        self.assertIn('ex(7028,txt_desc,160,80,0,fa_center,0.6);', draw_detail.source)


if __name__ == "__main__":
    unittest.main()
