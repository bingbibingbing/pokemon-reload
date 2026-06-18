from pathlib import Path
import unittest

from tools.patch_cheat_menu import patch_cheat_features
from tools.poke_gm80 import load_game


ROOT = Path(__file__).resolve().parents[1]
CLEAN_EXE = ROOT / "Proyecto Reloaded The Last Beta 1.9.1 Full.zh-cn.uifix.clean.exe"
CHEAT_EXE = ROOT / "Proyecto Reloaded The Last Beta 1.9.1 Full.zh-cn.uifix.cheat.exe"
TITLE_SCRIPT_IDS = (6348, 7038, 7991, 8442)
CHEAT_SCRIPT_IDS = (9436, 9437, 9438, 9441, 9442, 5359, 5348, 5782, 7859, 8726)
EXTENDED_CHEAT_SCRIPT_IDS = CHEAT_SCRIPT_IDS + (7425, 7426, 7788, 7847, 7974, 9003, 9465, 8977, 8962, 8756, 8762, 8770, 8775)


class CheatPatchBoundaryTests(unittest.TestCase):
    def test_zh_render_contains_cheat_menu_assets(self) -> None:
        render_dir = ROOT / "data" / "text" / "zh" / "render"
        expected_files = (
            "zh__custom__cheat_tab.png",
            "zh__custom__cheat_one_key.png",
            "zh__custom__cheat_no_player_damage.png",
            "zh__custom__cheat_one_hit_kill.png",
            "zh__custom__cheat_enemy_cannot_act.png",
            "zh__custom__cheat_enemy_start_with_1hp.png",
            "zh__custom__cheat_always_catch.png",
            "zh__custom__cheat_always_shiny_wild.png",
            "zh__custom__cheat_no_random_encounter.png",
            "zh__custom__cheat_instant_encounter_x.png",
            "zh__custom__cheat_hold_z_noclip.png",
            "zh__custom__cheat_pokeball_not_consumed.png",
            "zh__custom__cheat_catch_enemy_trainer_pokemon.png",
            "zh__custom__cheat_exp_multiplier.png",
            "zh__custom__cheat_exp_multiplier_1.png",
            "zh__custom__cheat_exp_multiplier_10.png",
            "zh__custom__cheat_exp_multiplier_100.png",
            "zh__custom__cheat_on.png",
            "zh__custom__cheat_off.png",
        )

        for filename in expected_files:
            self.assertTrue((render_dir / filename).exists(), filename)

    def test_patch_cheat_features_source_only_patches_options_and_battle_scripts(self) -> None:
        source = (ROOT / "tools" / "patch_cheat_menu.py").read_text(encoding="utf-8")

        self.assertIn("patch_script_batch(", source)
        self.assertIn("source_updates={", source)
        self.assertIn("9436: OPTIONS_DEFINE_SOURCE", source)
        self.assertIn("transform_updates={", source)
        self.assertIn("9437: _patch_options_draw_source", source)
        self.assertIn("7788: _patch_wild_encounter_frequency_source", source)
        self.assertIn("replace_updates={", source)
        for script_index in TITLE_SCRIPT_IDS:
            self.assertNotIn(f"{script_index}:", source)
        for script_index in EXTENDED_CHEAT_SCRIPT_IDS[1:]:
            self.assertIn(f"{script_index}:", source)

    def test_patch_cheat_features_source_declares_new_config_keys(self) -> None:
        source = (ROOT / "tools" / "patch_cheat_menu.py").read_text(encoding="utf-8")

        for key in (
            "always_shiny_wild",
            "no_random_encounter",
            "instant_encounter_x",
            "hold_z_noclip",
            "pokeball_not_consumed",
            "catch_enemy_trainer_pokemon",
            "exp_multiplier",
        ):
            self.assertIn(key, source)

    def test_patch_cheat_features_draws_visible_options_cheat_tab(self) -> None:
        output_exe = ROOT / "artifacts" / "test_patch_cheat_menu.gm80"
        output_exe.parent.mkdir(parents=True, exist_ok=True)
        output_exe.write_bytes(patch_cheat_features(CLEAN_EXE.read_bytes()))
        cheat_game = load_game(output_exe)

        draw_options = cheat_game.get_script(9437).source
        option_texts = cheat_game.get_script(9438).source

        self.assertIn("if(VIEW=5){", draw_options)
        self.assertIn(
            "if(VIEW=5){col0=(6316128);col1=(6316128);col2=(6316128);col3=(6316128);col4=(6316128);col5=col_sel;}",
            draw_options,
        )
        self.assertIn(
            'if(global.language="zh" && global.cheat_enabled=1){ ex(7028,txt_menu6,286,25,col5,fa_center,1); } else {',
            draw_options,
        )
        self.assertIn(
            'if(global.language="zh" && VIEW=5){ ex(7028,str0,24,64,col0,fa_left,1);',
            draw_options,
        )
        self.assertIn(
            'ex(7028,val5,room_width-24,144,col5,fa_right,1); } else {',
            draw_options,
        )
        for key in (
            "zh__custom__cheat_tab",
            "zh__custom__cheat_one_key",
            "zh__custom__cheat_no_player_damage",
            "zh__custom__cheat_one_hit_kill",
            "zh__custom__cheat_enemy_cannot_act",
            "zh__custom__cheat_enemy_start_with_1hp",
            "zh__custom__cheat_always_catch",
            "zh__custom__cheat_on",
            "zh__custom__cheat_off",
        ):
            self.assertIn(key, draw_options)
        self.assertIn('txt_menu6="Cheat";', option_texts)
        self.assertIn('txt_cht1="One-Key Cheat";', option_texts)
        self.assertIn('txt_cht2="No Player Damage";', option_texts)
        self.assertIn('txt_cht3="One Hit Kill";', option_texts)
        self.assertIn('txt_cht4="Enemy Cannot Act";', option_texts)
        self.assertIn('txt_cht5="Enemy Start With 1 HP";', option_texts)
        self.assertIn('txt_cht6="Always Catch";', option_texts)
        self.assertIn('txt_cht7="Always Shiny Wild";', option_texts)
        self.assertIn('txt_cht8="No Random Encounter";', option_texts)
        self.assertIn('txt_cht9="Instant Encounter X";', option_texts)
        self.assertIn('txt_cht10="Hold Z Noclip";', option_texts)
        self.assertIn('txt_cht11="PokeBall Not Consumed";', option_texts)
        self.assertIn('txt_cht12="Catch Trainer Pokemon";', option_texts)
        self.assertIn('txt_cht13="EXP Multiplier";', option_texts)
        self.assertNotIn('txt_menu6=ex(9928,2664);', option_texts)

    def test_patch_cheat_features_recomputes_integrity_after_enemy_hp_override(self) -> None:
        output_exe = ROOT / "artifacts" / "test_patch_cheat_integrity.gm80"
        output_exe.parent.mkdir(parents=True, exist_ok=True)
        output_exe.write_bytes(patch_cheat_features(CLEAN_EXE.read_bytes()))
        cheat_game = load_game(output_exe)

        initialize_battle = cheat_game.get_script(7859).source

        self.assertIn(
            'if(global.cheat_enabled=1 && (global.cheat_one_key=1 || global.cheat_enemy_start_with_1hp=1)){ for(i=0;i<=5;i+=1){ if(global.pkmn2[i]>0)global.PS_2[i]=1; }} ex(9623); if(global.battle=0){',
            initialize_battle,
        )

    def test_patch_cheat_features_forces_enemy_turn_to_skip_actions(self) -> None:
        output_exe = ROOT / "artifacts" / "test_patch_cheat_enemy_skip.gm80"
        output_exe.parent.mkdir(parents=True, exist_ok=True)
        output_exe.write_bytes(patch_cheat_features(CLEAN_EXE.read_bytes()))
        cheat_game = load_game(output_exe)

        turn_logic = cheat_game.get_script(5782).source

        self.assertIn(
            'if(global.cheat_enabled=1 && (global.cheat_one_key=1 || global.cheat_enemy_cannot_act=1)){ ACTION2=20; } if(ACTION2=0){ ACTION2=0;cont=0; while(ACTION2=0){',
            turn_logic,
        )
        self.assertNotIn(
            'if(global.cheat_enabled=1 && (global.cheat_one_key=1 || global.cheat_enemy_cannot_act=1)){ ACTION2=0; } if(ACTION2=0){ ACTION2=0;cont=0; while(ACTION2=0){',
            turn_logic,
        )

    def test_patch_cheat_features_blocks_non_turn_enemy_ai_actions(self) -> None:
        output_exe = ROOT / "artifacts" / "test_patch_cheat_enemy_non_turn_skip.gm80"
        output_exe.parent.mkdir(parents=True, exist_ok=True)
        output_exe.write_bytes(patch_cheat_features(CLEAN_EXE.read_bytes()))
        cheat_game = load_game(output_exe)

        enemy_auto_attack = cheat_game.get_script(8762).source
        enemy_manual_attack = cheat_game.get_script(8770).source

        self.assertIn(
            'if(global.cheat_enabled=1 && (global.cheat_one_key=1 || global.cheat_enemy_cannot_act=1)){ if(instance_exists((19))){(19).ACTION2=20;(19).NEXT_ACTION2=0;} exit; }',
            enemy_auto_attack,
        )
        self.assertIn(
            'if(global.cheat_enabled=1 && (global.cheat_one_key=1 || global.cheat_enemy_cannot_act=1)){ if(instance_exists((19))){(19).ACTION2=20;(19).NEXT_ACTION2=0;} exit; }',
            enemy_manual_attack,
        )

    def test_patch_cheat_features_freezes_non_turn_enemy_movement(self) -> None:
        output_exe = ROOT / "artifacts" / "test_patch_cheat_enemy_non_turn_freeze.gm80"
        output_exe.parent.mkdir(parents=True, exist_ok=True)
        output_exe.write_bytes(patch_cheat_features(CLEAN_EXE.read_bytes()))
        cheat_game = load_game(output_exe)

        canmove_logic = cheat_game.get_script(8756).source
        movement_logic = cheat_game.get_script(8775).source

        self.assertIn(
            'if(global.cheat_enabled=1 && (global.cheat_one_key=1 || global.cheat_enemy_cannot_act=1)){ canmove=false; friction=0; speed=0; image_speed=0; exit; }',
            canmove_logic,
        )
        self.assertIn(
            'if(global.cheat_enabled=1 && (global.cheat_one_key=1 || global.cheat_enemy_cannot_act=1)){ speed=0; canmove=false; friction=0; image_speed=0; exit; }',
            movement_logic,
        )

    def test_patch_cheat_features_allows_trainer_battle_pokeball_throw_flow(self) -> None:
        output_exe = ROOT / "artifacts" / "test_patch_cheat_trainer_ball_flow.gm80"
        output_exe.parent.mkdir(parents=True, exist_ok=True)
        output_exe.write_bytes(patch_cheat_features(CLEAN_EXE.read_bytes()))
        cheat_game = load_game(output_exe)

        battle_keys = cheat_game.get_script(7974).source

        self.assertIn(
            'if((global.battle=false || (global.cheat_enabled=1 && global.cheat_catch_enemy_trainer_pokemon=1)) && !instance_exists((23)) && instance_exists((0)) && instance_exists((4))){',
            battle_keys,
        )

    def test_patch_cheat_features_patches_extended_runtime_hooks(self) -> None:
        output_exe = ROOT / "artifacts" / "test_patch_cheat_runtime.gm80"
        output_exe.parent.mkdir(parents=True, exist_ok=True)
        output_exe.write_bytes(patch_cheat_features(CLEAN_EXE.read_bytes()))
        cheat_game = load_game(output_exe)

        self.assertIn("global.cheat_always_shiny_wild", cheat_game.get_script(7847).source)
        trigger_guard = cheat_game.get_script(9003).source
        wild_frequency = cheat_game.get_script(7788).source
        safari_frequency = cheat_game.get_script(9465).source

        self.assertIn('keyboard_check(ord("X"))', trigger_guard)
        self.assertIn("global.cheat_no_random_encounter", trigger_guard)
        self.assertEqual(trigger_guard.count("global.cheat_force_encounter_now=0;"), 1)
        self.assertIn("global.cheat_force_encounter_now", wild_frequency)
        self.assertIn("global.cheat_force_encounter_now=0;instance_create(0,0,(447));", wild_frequency)
        self.assertIn("global.cheat_force_encounter_now", safari_frequency)
        self.assertIn('keyboard_check(ord("X"))', safari_frequency)
        self.assertIn("global.cheat_force_encounter_now=0;instance_create(0,0,(447));", safari_frequency)
        self.assertIn("global.cheat_pokeball_not_consumed", cheat_game.get_script(7974).source)
        self.assertIn("global.cheat_catch_enemy_trainer_pokemon", cheat_game.get_script(7974).source)
        self.assertIn("global.cheat_exp_multiplier", cheat_game.get_script(7425).source)
        self.assertIn("global.cheat_exp_multiplier", cheat_game.get_script(7426).source)
        self.assertIn('keyboard_check(ord("Z"))', cheat_game.get_script(8977).source)
        self.assertIn('keyboard_check(ord("Z"))', cheat_game.get_script(8962).source)

    def test_patch_cheat_features_keeps_title_scripts_equal_to_clean_base(self) -> None:
        clean_game = load_game(CLEAN_EXE)

        output_exe = ROOT / "artifacts" / "test_patch_cheat_menu_boundary.gm80"
        output_exe.parent.mkdir(parents=True, exist_ok=True)
        output_exe.write_bytes(patch_cheat_features(CLEAN_EXE.read_bytes()))
        cheat_game = load_game(output_exe)

        for script_index in TITLE_SCRIPT_IDS:
            self.assertEqual(
                cheat_game.get_script(script_index).source,
                clean_game.get_script(script_index).source,
            )
        for script_index in EXTENDED_CHEAT_SCRIPT_IDS:
            self.assertNotEqual(
                cheat_game.get_script(script_index).source,
                clean_game.get_script(script_index).source,
            )

    def test_committed_cheat_exe_uses_clean_title_scripts_and_only_changes_allowed_scripts(self) -> None:
        clean_game = load_game(CLEAN_EXE)
        cheat_game = load_game(CHEAT_EXE)

        for script_index in TITLE_SCRIPT_IDS:
            self.assertEqual(
                cheat_game.get_script(script_index).source,
                clean_game.get_script(script_index).source,
            )
        for script_index in EXTENDED_CHEAT_SCRIPT_IDS:
            self.assertNotEqual(
                cheat_game.get_script(script_index).source,
                clean_game.get_script(script_index).source,
            )


if __name__ == "__main__":
    unittest.main()
