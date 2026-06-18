from __future__ import annotations

from pathlib import Path
import argparse

try:
    from tools.poke_gm80 import patch_script_batch
except ModuleNotFoundError:
    from poke_gm80 import patch_script_batch


CHEAT_CONFIG_FIELDS = (
    ("enabled", "cheat_enabled", 0),
    ("one_key_cheat", "cheat_one_key", 0),
    ("no_player_damage", "cheat_no_player_damage", 0),
    ("one_hit_kill", "cheat_one_hit_kill", 0),
    ("enemy_cannot_act", "cheat_enemy_cannot_act", 0),
    ("enemy_start_with_1hp", "cheat_enemy_start_with_1hp", 0),
    ("always_catch", "cheat_always_catch", 0),
    ("always_shiny_wild", "cheat_always_shiny_wild", 0),
    ("no_random_encounter", "cheat_no_random_encounter", 0),
    ("instant_encounter_x", "cheat_instant_encounter_x", 0),
    ("hold_z_noclip", "cheat_hold_z_noclip", 0),
    ("pokeball_not_consumed", "cheat_pokeball_not_consumed", 0),
    ("catch_enemy_trainer_pokemon", "cheat_catch_enemy_trainer_pokemon", 0),
    ("exp_multiplier", "cheat_exp_multiplier", 1),
)


def _build_defaults_source() -> str:
    return " ".join(f"global.{global_name}={default};" for _, global_name, default in CHEAT_CONFIG_FIELDS) + " "


def _build_guard_source() -> str:
    parts = [
        f'if(!variable_global_exists("{global_name}"))global.{global_name}={default};'
        for _, global_name, default in CHEAT_CONFIG_FIELDS
    ]
    parts.append('if(!variable_global_exists("cheat_force_encounter_now"))global.cheat_force_encounter_now=0;')
    return " ".join(parts) + " "


def _build_create_file_source() -> str:
    parts = [
        'f=file_text_open_write("data\\cheat.ini");',
        'file_text_write_string(f,"[cheat]");',
        "file_text_writeln(f);",
    ]
    for key_name, _, default in CHEAT_CONFIG_FIELDS:
        parts.append(f'file_text_write_string(f,"{key_name}={default}");')
        parts.append("file_text_writeln(f);")
    parts.append("file_text_close(f);")
    return " ".join(parts) + " "


def _build_write_config_source() -> str:
    parts = [
        'f=file_text_open_write("data\\cheat.ini");',
        'file_text_write_string(f,"[cheat]");',
        "file_text_writeln(f);",
    ]
    for key_name, global_name, _ in CHEAT_CONFIG_FIELDS:
        parts.append(f'file_text_write_string(f,"{key_name}="+string(global.{global_name}));')
        parts.append("file_text_writeln(f);")
    parts.append("file_text_close(f);")
    return " ".join(parts) + " "


CHEAT_GLOBAL_DEFAULTS_SOURCE = _build_defaults_source()
CHEAT_GLOBAL_GUARD_SOURCE = _build_guard_source()
CHEAT_CREATE_FILE_SOURCE = _build_create_file_source()
CHEAT_WRITE_CONFIG_SOURCE = _build_write_config_source()
CHEAT_SANITIZE_SOURCE = "if(global.cheat_exp_multiplier!=10 && global.cheat_exp_multiplier!=100)global.cheat_exp_multiplier=1; "

_load_clauses = []
for key_name, global_name, _ in CHEAT_CONFIG_FIELDS:
    prefix = f"{key_name}="
    delete_count = len(prefix)
    clause = f'if(string_pos("{prefix}",cheat_line)=1)global.{global_name}=real(string_delete(cheat_line,1,{delete_count}));'
    _load_clauses.append(clause)

CHEAT_LOAD_CONFIG_SOURCE = (
    CHEAT_GLOBAL_DEFAULTS_SOURCE
    + r'''if(!file_exists("data\cheat.ini")){'''
    + CHEAT_CREATE_FILE_SOURCE
    + r'''} f=file_text_open_read("data\cheat.ini"); while(!file_text_eof(f)){ cheat_line=file_text_read_string(f); '''
    + " else ".join(_load_clauses)
    + r''' file_text_readln(f);} file_text_close(f); '''
    + CHEAT_SANITIZE_SOURCE
)


OPTIONS_DEFINE_SOURCE = (
    r'''ABAJO=false;VIEW=0; canshoot=true; SEL=0;AVANCE=0;  col0=c_black;col1=c_black;col2=c_black; col3=c_black;col4=c_black;col5=c_black;  str0="";str1="";str2="";str3="";str4="";str5="";  val0="";val1="";val2="";val3="";val4="";val5="";  STR0="";STR1="";STR2="";STR3="";STR4="";STR5=""; STR6="";STR7="";STR8="";STR9="";STR10="";STR11=""; STR12="";STR13="";STR14="";STR15="";STR16="";STR17=""; STR18="";  VAL0="";VAL1="";VAL2="";VAL3="";VAL4="";VAL5=""; VAL6="";VAL7="";VAL8="";VAL9="";VAL10="";VAL11=""; VAL12="";VAL13="";VAL14="";VAL15="";VAL16="";VAL17=""; VAL18="";  f=file_text_open_read("data\text\lan.txt"); IDIOMA_ACTUAL=0;NUM_LAN=0; while(!file_text_eof(f)){NUM_LAN+=1;file_text_readln(f);} file_text_close(f);  f=file_text_open_read("data\text\lan.txt"); for(i=0;i<NUM_LAN;i+=1){ linea=file_text_read_string(f); LAN_FOL[i]=string_copy(linea,0,2); LAN_TXT[i]=string_copy(linea,4,ex(9827,linea)-1); if(global.language=LAN_FOL[i])IDIOMA_ACTUAL=i; file_text_readln(f);} file_text_close(f);  f=file_text_open_read("data\audio\musica\audio.txt"); FOLDERMUSIC_ACTUAL=0;NUM_FOLDER=0; while(!file_text_eof(f)){NUM_FOLDER+=1;file_text_readln(f);} file_text_close(f);  f=file_text_open_read("data\audio\musica\audio.txt"); for(i=0;i<NUM_FOLDER;i+=1){ linea=file_text_read_string(f); MUS_FOL[i]=string_copy(linea,0,2); MUS_TXT[i]=string_copy(linea,4,ex(9827,linea)-1); if(global.foldermusic=MUS_FOL[i])FOLDERMUSIC_ACTUAL=i; file_text_readln(f);} file_text_close(f);  ex(7829,ex(7836));  ex(9438);  PORCENTAJE=string(ex(8886))+"%"; '''
    + CHEAT_LOAD_CONFIG_SOURCE
)

OPTIONS_TEXTS_APPEND_OLD = 'txt_otr18=ex(9928,1499); txt_otr19=ex(9928,1500); txt_otr20=ex(9928,1501); txt_otr21=ex(9928,2454);  acc=195;'
OPTIONS_TEXTS_APPEND_NEW = (
    'txt_otr18=ex(9928,1499); txt_otr19=ex(9928,1500); txt_otr20=ex(9928,1501); txt_otr21=ex(9928,2454); '
    'txt_menu6="Cheat"; txt_cht1="One-Key Cheat"; txt_cht2="No Player Damage"; txt_cht3="One Hit Kill"; '
    'txt_cht4="Enemy Cannot Act"; txt_cht5="Enemy Start With 1 HP"; txt_cht6="Always Catch"; '
    'txt_cht7="Always Shiny Wild"; txt_cht8="No Random Encounter"; txt_cht9="Instant Encounter X"; '
    'txt_cht10="Hold Z Noclip"; txt_cht11="PokeBall Not Consumed"; txt_cht12="Catch Trainer Pokemon"; '
    'txt_cht13="EXP Multiplier";  acc=195;'
)

OPTIONS_VALUES_INSERT_OLD = ' if(VIEW=4){ if(global.primerosiempreactual=false){STR0=txt_otr1;VAL0=txt_otr2;} else {STR0=txt_otr1;VAL0=txt_otr3;} if(global.show_ponermote=true){STR1=txt_otr7;VAL1=txt_on;} else {STR1=txt_otr7;VAL1=txt_off;} if(global.show_avisos_mision=true){STR2=txt_avmis;VAL2=txt_on;} else {STR2=txt_avmis;VAL2=txt_off;} if(global.show_avisos_objetivo=true){STR3=txt_avobj;VAL3=txt_on;} else {STR3=txt_avobj;VAL3=txt_off;} STR4=txt_otr18; if(global.sistema_medida=0)VAL4=txt_otr19; else VAL4=txt_otr20; if(global.dificultad=1)DIF=txt_otr11;if(global.dificultad=2)DIF=txt_otr12;if(global.dificultad=3)DIF=txt_otr13; if(global.dificultad=4)DIF=txt_otr21;if(global.dificultad=5)DIF=txt_otr15;if(global.dificultad=6)DIF=txt_otr14; STR5=txt_otr16;VAL5=DIF; STR6=txt_otr17;VAL6=PORCENTAJE; if(SEL>=4){AVANCE=1;} }  if(AVANCE=0){'
OPTIONS_VALUES_INSERT_NEW = (
    ' if(VIEW=4){ if(global.primerosiempreactual=false){STR0=txt_otr1;VAL0=txt_otr2;} else {STR0=txt_otr1;VAL0=txt_otr3;} if(global.show_ponermote=true){STR1=txt_otr7;VAL1=txt_on;} else {STR1=txt_otr7;VAL1=txt_off;} if(global.show_avisos_mision=true){STR2=txt_avmis;VAL2=txt_on;} else {STR2=txt_avmis;VAL2=txt_off;} if(global.show_avisos_objetivo=true){STR3=txt_avobj;VAL3=txt_on;} else {STR3=txt_avobj;VAL3=txt_off;} STR4=txt_otr18; if(global.sistema_medida=0)VAL4=txt_otr19; else VAL4=txt_otr20; if(global.dificultad=1)DIF=txt_otr11;if(global.dificultad=2)DIF=txt_otr12;if(global.dificultad=3)DIF=txt_otr13; if(global.dificultad=4)DIF=txt_otr21;if(global.dificultad=5)DIF=txt_otr15;if(global.dificultad=6)DIF=txt_otr14; STR5=txt_otr16;VAL5=DIF; STR6=txt_otr17;VAL6=PORCENTAJE; if(SEL>=4){AVANCE=1;} }  '
    'if(VIEW=5){ STR0=txt_cht1; if(global.cheat_one_key=1)VAL0=txt_on; else VAL0=txt_off; '
    'STR1=txt_cht2; STR2=txt_cht3; STR3=txt_cht4; STR4=txt_cht5; STR5=txt_cht6; '
    'if(global.cheat_one_key=1){VAL1=txt_on;VAL2=txt_on;VAL3=txt_on;VAL4=txt_on;VAL5=txt_on;} else { '
    'if(global.cheat_no_player_damage=1)VAL1=txt_on; else VAL1=txt_off; '
    'if(global.cheat_one_hit_kill=1)VAL2=txt_on; else VAL2=txt_off; '
    'if(global.cheat_enemy_cannot_act=1)VAL3=txt_on; else VAL3=txt_off; '
    'if(global.cheat_enemy_start_with_1hp=1)VAL4=txt_on; else VAL4=txt_off; '
    'if(global.cheat_always_catch=1)VAL5=txt_on; else VAL5=txt_off; } '
    'STR6=txt_cht7; if(global.cheat_always_shiny_wild=1)VAL6=txt_on; else VAL6=txt_off; '
    'STR7=txt_cht8; if(global.cheat_no_random_encounter=1)VAL7=txt_on; else VAL7=txt_off; '
    'STR8=txt_cht9; if(global.cheat_instant_encounter_x=1)VAL8=txt_on; else VAL8=txt_off; '
    'STR9=txt_cht10; if(global.cheat_hold_z_noclip=1)VAL9=txt_on; else VAL9=txt_off; '
    'STR10=txt_cht11; if(global.cheat_pokeball_not_consumed=1)VAL10=txt_on; else VAL10=txt_off; '
    'STR11=txt_cht12; if(global.cheat_catch_enemy_trainer_pokemon=1)VAL11=txt_on; else VAL11=txt_off; '
    'STR12=txt_cht13; if(global.cheat_exp_multiplier=100)VAL12="100x"; else if(global.cheat_exp_multiplier=10)VAL12="10x"; else VAL12="1x"; '
    'if(SEL>=4){AVANCE=SEL-3;} if(SEL>=10){AVANCE=7;} }  if(AVANCE=0){'
)

OPTIONS_ACTION_INSERT_OLD = ' if(VIEW=4){ if(SEL=0){if(global.primerosiempreactual=true){global.primerosiempreactual=false;} else {global.primerosiempreactual=true;}} if(SEL=1){if(global.show_ponermote=true)global.show_ponermote=false; else global.show_ponermote=true;} if(SEL=2){if(global.show_avisos_mision=true){global.show_avisos_mision=false;} else {global.show_avisos_mision=true;}} if(SEL=3){if(global.show_avisos_objetivo=true){global.show_avisos_objetivo=false;} else {global.show_avisos_objetivo=true;}} if(SEL=4){ if(global.sistema_medida=0)global.sistema_medida=1; else global.sistema_medida=0;} if(SEL=5){ if(global.dificultad=6)global.dificultad=1;else global.dificultad+=1; if((20).MEDALLA_STAR[1]!=false && global.dificultad=1)global.dificultad=2; if(global.dificultad=1){global.PowDif1=2;global.PowDif2=4;exit;}if(global.dificultad=2){global.PowDif1=4;global.PowDif2=4;exit;}if(global.dificultad=3){global.PowDif1=4;global.PowDif2=2;exit;}if(global.dificultad=4){global.PowDif1=2;global.PowDif2=2;exit;}if(global.dificultad=5){global.PowDif1=1;global.PowDif2=1;exit;}if(global.dificultad=6){global.PowDif1=4;global.PowDif2=1;exit;}}} exit;}'
OPTIONS_ACTION_INSERT_NEW = (
    ' if(VIEW=4){ if(SEL=0){if(global.primerosiempreactual=true){global.primerosiempreactual=false;} else {global.primerosiempreactual=true;}} if(SEL=1){if(global.show_ponermote=true)global.show_ponermote=false; else global.show_ponermote=true;} if(SEL=2){if(global.show_avisos_mision=true){global.show_avisos_mision=false;} else {global.show_avisos_mision=true;}} if(SEL=3){if(global.show_avisos_objetivo=true){global.show_avisos_objetivo=false;} else {global.show_avisos_objetivo=true;}} if(SEL=4){ if(global.sistema_medida=0)global.sistema_medida=1; else global.sistema_medida=0;} if(SEL=5){ if(global.dificultad=6)global.dificultad=1;else global.dificultad+=1; if((20).MEDALLA_STAR[1]!=false && global.dificultad=1)global.dificultad=2; if(global.dificultad=1){global.PowDif1=2;global.PowDif2=4;exit;}if(global.dificultad=2){global.PowDif1=4;global.PowDif2=4;exit;}if(global.dificultad=3){global.PowDif1=4;global.PowDif2=2;exit;}if(global.dificultad=4){global.PowDif1=2;global.PowDif2=2;exit;}if(global.dificultad=5){global.PowDif1=1;global.PowDif2=1;exit;}if(global.dificultad=6){global.PowDif1=4;global.PowDif2=1;exit;}}}'
    + ' if(VIEW=5){ if(SEL=0){ if(global.cheat_one_key=1)global.cheat_one_key=0; else global.cheat_one_key=1; } '
    + 'else if(global.cheat_one_key=0){ if(SEL=1){ if(global.cheat_no_player_damage=1)global.cheat_no_player_damage=0; else global.cheat_no_player_damage=1; } '
    + 'if(SEL=2){ if(global.cheat_one_hit_kill=1)global.cheat_one_hit_kill=0; else global.cheat_one_hit_kill=1; } '
    + 'if(SEL=3){ if(global.cheat_enemy_cannot_act=1)global.cheat_enemy_cannot_act=0; else global.cheat_enemy_cannot_act=1; } '
    + 'if(SEL=4){ if(global.cheat_enemy_start_with_1hp=1)global.cheat_enemy_start_with_1hp=0; else global.cheat_enemy_start_with_1hp=1; } '
    + 'if(SEL=5){ if(global.cheat_always_catch=1)global.cheat_always_catch=0; else global.cheat_always_catch=1; } } '
    + 'if(SEL=6){ if(global.cheat_always_shiny_wild=1)global.cheat_always_shiny_wild=0; else global.cheat_always_shiny_wild=1; } '
    + 'if(SEL=7){ if(global.cheat_no_random_encounter=1)global.cheat_no_random_encounter=0; else global.cheat_no_random_encounter=1; } '
    + 'if(SEL=8){ if(global.cheat_instant_encounter_x=1)global.cheat_instant_encounter_x=0; else global.cheat_instant_encounter_x=1; } '
    + 'if(SEL=9){ if(global.cheat_hold_z_noclip=1)global.cheat_hold_z_noclip=0; else global.cheat_hold_z_noclip=1; } '
    + 'if(SEL=10){ if(global.cheat_pokeball_not_consumed=1)global.cheat_pokeball_not_consumed=0; else global.cheat_pokeball_not_consumed=1; } '
    + 'if(SEL=11){ if(global.cheat_catch_enemy_trainer_pokemon=1)global.cheat_catch_enemy_trainer_pokemon=0; else global.cheat_catch_enemy_trainer_pokemon=1; } '
    + 'if(SEL=12){ if(global.cheat_exp_multiplier=1)global.cheat_exp_multiplier=10; else if(global.cheat_exp_multiplier=10)global.cheat_exp_multiplier=100; else global.cheat_exp_multiplier=1; } '
    + CHEAT_SANITIZE_SOURCE
    + CHEAT_WRITE_CONFIG_SOURCE
    + ' } exit;}'
)

OPTIONS_MAXNUM_OLD = ' if(VIEW=0)max_num=11; if(VIEW=1)max_num=18; if(VIEW=2)max_num=6; if(VIEW=3)max_num=12; if(VIEW=4)max_num=6;'
OPTIONS_MAXNUM_NEW = ' if(VIEW=0)max_num=11; if(VIEW=1)max_num=18; if(VIEW=2)max_num=6; if(VIEW=3)max_num=12; if(VIEW=4)max_num=6; if(VIEW=5)max_num=12;'

OPTIONS_UP_WRAP_OLD = 'if(ABAJO=false){ ABAJO=true; if(VIEW=0)SEL=11; if(VIEW=1)SEL=18; if(VIEW=2)SEL=6; if(VIEW=3)SEL=12; if(VIEW=4)SEL=6; exit;}'
OPTIONS_UP_WRAP_NEW = 'if(ABAJO=false){ ABAJO=true; if(VIEW=0)SEL=11; if(VIEW=1)SEL=18; if(VIEW=2)SEL=6; if(VIEW=3)SEL=12; if(VIEW=4)SEL=6; if(VIEW=5)SEL=12; exit;}'

OPTIONS_VIEW_LEFT_OLD = ' if(ABAJO=false){ if(VIEW=0)VIEW=4; else VIEW-=1; exit;}'
OPTIONS_VIEW_LEFT_NEW = ' if(ABAJO=false){ if(global.cheat_enabled=1){ if(VIEW=0)VIEW=5; else VIEW-=1; } else { if(VIEW=0)VIEW=4; else VIEW-=1; } exit;}'

OPTIONS_VIEW_RIGHT_OLD = ' if(ABAJO=false){ if(VIEW=4)VIEW=0; else VIEW+=1; exit;}'
OPTIONS_VIEW_RIGHT_NEW = ' if(ABAJO=false){ if(global.cheat_enabled=1){ if(VIEW=5)VIEW=0; else VIEW+=1; } else { if(VIEW=4)VIEW=0; else VIEW+=1; } exit;}'

CHEAT_ZH_KEYMAP_SOURCE = (
    'if(global.language="zh" && global.cheat_enabled=1 && global.zh_text_key_map!=(-1)){'
    'if(ds_map_exists(global.zh_text_key_map,txt_menu6))ds_map_replace(global.zh_text_key_map,txt_menu6,"zh__custom__cheat_tab"); else ds_map_add(global.zh_text_key_map,txt_menu6,"zh__custom__cheat_tab"); '
    'if(ds_map_exists(global.zh_text_key_map,txt_cht1))ds_map_replace(global.zh_text_key_map,txt_cht1,"zh__custom__cheat_one_key"); else ds_map_add(global.zh_text_key_map,txt_cht1,"zh__custom__cheat_one_key"); '
    'if(ds_map_exists(global.zh_text_key_map,txt_cht2))ds_map_replace(global.zh_text_key_map,txt_cht2,"zh__custom__cheat_no_player_damage"); else ds_map_add(global.zh_text_key_map,txt_cht2,"zh__custom__cheat_no_player_damage"); '
    'if(ds_map_exists(global.zh_text_key_map,txt_cht3))ds_map_replace(global.zh_text_key_map,txt_cht3,"zh__custom__cheat_one_hit_kill"); else ds_map_add(global.zh_text_key_map,txt_cht3,"zh__custom__cheat_one_hit_kill"); '
    'if(ds_map_exists(global.zh_text_key_map,txt_cht4))ds_map_replace(global.zh_text_key_map,txt_cht4,"zh__custom__cheat_enemy_cannot_act"); else ds_map_add(global.zh_text_key_map,txt_cht4,"zh__custom__cheat_enemy_cannot_act"); '
    'if(ds_map_exists(global.zh_text_key_map,txt_cht5))ds_map_replace(global.zh_text_key_map,txt_cht5,"zh__custom__cheat_enemy_start_with_1hp"); else ds_map_add(global.zh_text_key_map,txt_cht5,"zh__custom__cheat_enemy_start_with_1hp"); '
    'if(ds_map_exists(global.zh_text_key_map,txt_cht6))ds_map_replace(global.zh_text_key_map,txt_cht6,"zh__custom__cheat_always_catch"); else ds_map_add(global.zh_text_key_map,txt_cht6,"zh__custom__cheat_always_catch"); '
    'if(ds_map_exists(global.zh_text_key_map,txt_cht7))ds_map_replace(global.zh_text_key_map,txt_cht7,"zh__custom__cheat_always_shiny_wild"); else ds_map_add(global.zh_text_key_map,txt_cht7,"zh__custom__cheat_always_shiny_wild"); '
    'if(ds_map_exists(global.zh_text_key_map,txt_cht8))ds_map_replace(global.zh_text_key_map,txt_cht8,"zh__custom__cheat_no_random_encounter"); else ds_map_add(global.zh_text_key_map,txt_cht8,"zh__custom__cheat_no_random_encounter"); '
    'if(ds_map_exists(global.zh_text_key_map,txt_cht9))ds_map_replace(global.zh_text_key_map,txt_cht9,"zh__custom__cheat_instant_encounter_x"); else ds_map_add(global.zh_text_key_map,txt_cht9,"zh__custom__cheat_instant_encounter_x"); '
    'if(ds_map_exists(global.zh_text_key_map,txt_cht10))ds_map_replace(global.zh_text_key_map,txt_cht10,"zh__custom__cheat_hold_z_noclip"); else ds_map_add(global.zh_text_key_map,txt_cht10,"zh__custom__cheat_hold_z_noclip"); '
    'if(ds_map_exists(global.zh_text_key_map,txt_cht11))ds_map_replace(global.zh_text_key_map,txt_cht11,"zh__custom__cheat_pokeball_not_consumed"); else ds_map_add(global.zh_text_key_map,txt_cht11,"zh__custom__cheat_pokeball_not_consumed"); '
    'if(ds_map_exists(global.zh_text_key_map,txt_cht12))ds_map_replace(global.zh_text_key_map,txt_cht12,"zh__custom__cheat_catch_enemy_trainer_pokemon"); else ds_map_add(global.zh_text_key_map,txt_cht12,"zh__custom__cheat_catch_enemy_trainer_pokemon"); '
    'if(ds_map_exists(global.zh_text_key_map,txt_cht13))ds_map_replace(global.zh_text_key_map,txt_cht13,"zh__custom__cheat_exp_multiplier"); else ds_map_add(global.zh_text_key_map,txt_cht13,"zh__custom__cheat_exp_multiplier"); '
    'if(ds_map_exists(global.zh_text_key_map,txt_on))ds_map_replace(global.zh_text_key_map,txt_on,"zh__custom__cheat_on"); else ds_map_add(global.zh_text_key_map,txt_on,"zh__custom__cheat_on"); '
    'if(ds_map_exists(global.zh_text_key_map,txt_off))ds_map_replace(global.zh_text_key_map,txt_off,"zh__custom__cheat_off"); else ds_map_add(global.zh_text_key_map,txt_off,"zh__custom__cheat_off"); '
    'if(ds_map_exists(global.zh_text_key_map,"1x"))ds_map_replace(global.zh_text_key_map,"1x","zh__custom__cheat_exp_multiplier_1"); else ds_map_add(global.zh_text_key_map,"1x","zh__custom__cheat_exp_multiplier_1"); '
    'if(ds_map_exists(global.zh_text_key_map,"10x"))ds_map_replace(global.zh_text_key_map,"10x","zh__custom__cheat_exp_multiplier_10"); else ds_map_add(global.zh_text_key_map,"10x","zh__custom__cheat_exp_multiplier_10"); '
    'if(ds_map_exists(global.zh_text_key_map,"100x"))ds_map_replace(global.zh_text_key_map,"100x","zh__custom__cheat_exp_multiplier_100"); else ds_map_add(global.zh_text_key_map,"100x","zh__custom__cheat_exp_multiplier_100");'
    '} '
)

OPTIONS_DRAW_TAB6_OLD = 'draw_text_color(234,25,txt_menu5,col4,col4,col4,col4,1);  if(ABAJO=false){'
OPTIONS_DRAW_TAB6_NEW = (
    'draw_text_color(234,25,txt_menu5,col4,col4,col4,col4,1); '
    'if(global.cheat_enabled=1){ if(global.language="zh" && global.cheat_enabled=1){ ex(7028,txt_menu6,286,25,col5,fa_center,1); } else { '
    'draw_text_color(286,26,txt_menu6,(13160656),(13160656),(13160656),(13160656),1);'
    'draw_text_color(287,26,txt_menu6,(13160656),(13160656),(13160656),(13160656),1); '
    'draw_text_color(287,25,txt_menu6,(13160656),(13160656),(13160656),(13160656),1);'
    'draw_text_color(286,25,txt_menu6,col5,col5,col5,col5,1); } } if(ABAJO=false){'
)

OPTIONS_DRAW_LIST_OLD = (
    'draw_set_font((0)); draw_set_halign(fa_left); '
    'draw_text_color(24,65,str0,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(25,65,str0,(13160656),(13160656),(13160656),(13160656),1); '
    'draw_text_color(25,64,str0,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(24,64,str0,col0,col0,col0,col0,1); '
    'draw_text_color(24,81,str1,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(25,81,str1,(13160656),(13160656),(13160656),(13160656),1); '
    'draw_text_color(25,80,str1,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(24,80,str1,col1,col1,col1,col1,1); '
    'draw_text_color(24,97,str2,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(25,97,str2,(13160656),(13160656),(13160656),(13160656),1); '
    'draw_text_color(25,96,str2,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(24,96,str2,col2,col2,col2,col2,1); '
    'draw_text_color(24,113,str3,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(25,113,str3,(13160656),(13160656),(13160656),(13160656),1); '
    'draw_text_color(25,112,str3,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(24,112,str3,col3,col3,col3,col3,1); '
    'draw_text_color(24,129,str4,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(25,129,str4,(13160656),(13160656),(13160656),(13160656),1); '
    'draw_text_color(25,128,str4,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(24,128,str4,col4,col4,col4,col4,1); '
    'draw_text_color(24,145,str5,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(25,145,str5,(13160656),(13160656),(13160656),(13160656),1); '
    'draw_text_color(25,144,str5,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(24,144,str5,col5,col5,col5,col5,1);  '
    'draw_set_halign(fa_right); '
    'draw_text_color(room_width-24,65,val0,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(room_width-23,65,val0,(13160656),(13160656),(13160656),(13160656),1); '
    'draw_text_color(room_width-23,64,val0,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(room_width-24,64,val0,col0,col0,col0,col0,1); '
    'draw_text_color(room_width-24,81,val1,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(room_width-23,81,val1,(13160656),(13160656),(13160656),(13160656),1); '
    'draw_text_color(room_width-23,80,val1,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(room_width-24,80,val1,col1,col1,col1,col1,1); '
    'draw_text_color(room_width-24,97,val2,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(room_width-23,97,val2,(13160656),(13160656),(13160656),(13160656),1); '
    'draw_text_color(room_width-23,96,val2,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(room_width-24,96,val2,col2,col2,col2,col2,1); '
    'draw_text_color(room_width-24,113,val3,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(room_width-23,113,val3,(13160656),(13160656),(13160656),(13160656),1); '
    'draw_text_color(room_width-23,112,val3,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(room_width-24,112,val3,col3,col3,col3,col3,1); '
    'draw_text_color(room_width-24,129,val4,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(room_width-23,129,val4,(13160656),(13160656),(13160656),(13160656),1); '
    'draw_text_color(room_width-23,128,val4,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(room_width-24,128,val4,col4,col4,col4,col4,1); '
    'draw_text_color(room_width-24,145,val5,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(room_width-23,145,val5,(13160656),(13160656),(13160656),(13160656),1); '
    'draw_text_color(room_width-23,144,val5,(13160656),(13160656),(13160656),(13160656),1);draw_text_color(room_width-24,144,val5,col5,col5,col5,col5,1);'
)

OPTIONS_DRAW_LIST_NEW = (
    'draw_set_font((0)); draw_set_halign(fa_left); if(global.language="zh" && VIEW=5){ '
    'ex(7028,str0,24,64,col0,fa_left,1); ex(7028,str1,24,80,col1,fa_left,1); ex(7028,str2,24,96,col2,fa_left,1); '
    'ex(7028,str3,24,112,col3,fa_left,1); ex(7028,str4,24,128,col4,fa_left,1); ex(7028,str5,24,144,col5,fa_left,1); '
    'draw_set_halign(fa_right); ex(7028,val0,room_width-24,64,col0,fa_right,1); ex(7028,val1,room_width-24,80,col1,fa_right,1); '
    'ex(7028,val2,room_width-24,96,col2,fa_right,1); ex(7028,val3,room_width-24,112,col3,fa_right,1); '
    'ex(7028,val4,room_width-24,128,col4,fa_right,1); ex(7028,val5,room_width-24,144,col5,fa_right,1); } else { '
    + OPTIONS_DRAW_LIST_OLD
    + ' }'
)


def _replace_once(source: str, old: str, new: str) -> str:
    if old not in source:
        raise ValueError(f"substring not found: {old!r}")
    return source.replace(old, new, 1)


def _patch_options_draw_source(source: str) -> str:
    source = _replace_once(
        source,
        "draw_set_font((1));",
        'if(!variable_global_exists("cheat_enabled"))global.cheat_enabled=0; if(!variable_global_exists("zh_text_key_map"))global.zh_text_key_map=(-1); draw_set_font((1));',
    )
    source = _replace_once(
        source,
        "if(VIEW=0){col0=col_sel;col1=(6316128); col2=(6316128); col3=(6316128); col4=(6316128); } if(VIEW=1){col0=(6316128); col1=col_sel;col2=(6316128); col3=(6316128); col4=(6316128); } if(VIEW=2){col0=(6316128); col1=(6316128); col2=col_sel;col3=(6316128); col4=(6316128); } if(VIEW=3){col0=(6316128); col1=(6316128); col2=(6316128); col3=col_sel;col4=(6316128); } if(VIEW=4){col0=(6316128); col1=(6316128); col2=(6316128); col3=(6316128); col4=col_sel;}",
        "if(VIEW=0){col0=col_sel;col1=(6316128);col2=(6316128);col3=(6316128);col4=(6316128);col5=(6316128);} if(VIEW=1){col0=(6316128);col1=col_sel;col2=(6316128);col3=(6316128);col4=(6316128);col5=(6316128);} if(VIEW=2){col0=(6316128);col1=(6316128);col2=col_sel;col3=(6316128);col4=(6316128);col5=(6316128);} if(VIEW=3){col0=(6316128);col1=(6316128);col2=(6316128);col3=col_sel;col4=(6316128);col5=(6316128);} if(VIEW=4){col0=(6316128);col1=(6316128);col2=(6316128);col3=(6316128);col4=col_sel;col5=(6316128);} if(VIEW=5){col0=(6316128);col1=(6316128);col2=(6316128);col3=(6316128);col4=(6316128);col5=col_sel;}",
    )
    source = _replace_once(
        source,
        "  draw_text_color(38,26,txt_menu1",
        f"  {CHEAT_ZH_KEYMAP_SOURCE} draw_text_color(38,26,txt_menu1",
    )

    tab_replacements = (
        ("draw_text_color(38,26,txt_menu1", "draw_text_color(26,26,txt_menu1"),
        ("draw_text_color(39,26,txt_menu1", "draw_text_color(27,26,txt_menu1"),
        ("draw_text_color(39,25,txt_menu1", "draw_text_color(27,25,txt_menu1"),
        ("draw_text_color(38,25,txt_menu1", "draw_text_color(26,25,txt_menu1"),
        ("draw_text_color(100,26,txt_menu2", "draw_text_color(78,26,txt_menu2"),
        ("draw_text_color(101,26,txt_menu2", "draw_text_color(79,26,txt_menu2"),
        ("draw_text_color(101,25,txt_menu2", "draw_text_color(79,25,txt_menu2"),
        ("draw_text_color(100,25,txt_menu2", "draw_text_color(78,25,txt_menu2"),
        ("draw_text_color(162,26,txt_menu3", "draw_text_color(130,26,txt_menu3"),
        ("draw_text_color(163,26,txt_menu3", "draw_text_color(131,26,txt_menu3"),
        ("draw_text_color(163,25,txt_menu3", "draw_text_color(131,25,txt_menu3"),
        ("draw_text_color(162,25,txt_menu3", "draw_text_color(130,25,txt_menu3"),
        ("draw_text_color(225,26,txt_menu4", "draw_text_color(182,26,txt_menu4"),
        ("draw_text_color(226,26,txt_menu4", "draw_text_color(183,26,txt_menu4"),
        ("draw_text_color(226,25,txt_menu4", "draw_text_color(183,25,txt_menu4"),
        ("draw_text_color(225,25,txt_menu4", "draw_text_color(182,25,txt_menu4"),
        ("draw_text_color(288,26,txt_menu5", "draw_text_color(234,26,txt_menu5"),
        ("draw_text_color(289,26,txt_menu5", "draw_text_color(235,26,txt_menu5"),
        ("draw_text_color(289,25,txt_menu5", "draw_text_color(235,25,txt_menu5"),
        ("draw_text_color(288,25,txt_menu5", "draw_text_color(234,25,txt_menu5"),
    )
    for old, new in tab_replacements:
        source = _replace_once(source, old, new)

    source = _replace_once(source, OPTIONS_DRAW_TAB6_OLD, OPTIONS_DRAW_TAB6_NEW)
    source = _replace_once(source, OPTIONS_DRAW_LIST_OLD, OPTIONS_DRAW_LIST_NEW)
    return source


def _patch_wild_encounter_frequency_source(source: str) -> str:
    source = _replace_once(
        source,
        "var i, NV, Pokemon, PK, Valor, MAX_FREQUENCY, FREC_HORDAS, req_poke;",
        CHEAT_GLOBAL_GUARD_SOURCE + "var i, NV, Pokemon, PK, Valor, MAX_FREQUENCY, FREC_HORDAS, req_poke;",
    )
    if "if(ex(7531," not in source:
        raise ValueError("wild encounter frequency pattern not found")
    source = source.replace("if(ex(7531,", "if(global.cheat_force_encounter_now=1 || ex(7531,")
    return source.replace(
        "instance_create(0,0,(447));",
        "global.cheat_force_encounter_now=0;instance_create(0,0,(447));",
    )


def patch_cheat_features(raw: bytes) -> bytes:
    return patch_script_batch(
        raw,
        source_updates={
            9436: OPTIONS_DEFINE_SOURCE,
        },
        transform_updates={
            9437: _patch_options_draw_source,
            7788: _patch_wild_encounter_frequency_source,
        },
        replace_updates={
            9438: [(OPTIONS_TEXTS_APPEND_OLD, OPTIONS_TEXTS_APPEND_NEW)],
            9442: [(OPTIONS_VALUES_INSERT_OLD, OPTIONS_VALUES_INSERT_NEW)],
            9441: [
                (OPTIONS_ACTION_INSERT_OLD, OPTIONS_ACTION_INSERT_NEW),
                (OPTIONS_MAXNUM_OLD, OPTIONS_MAXNUM_NEW),
                (OPTIONS_UP_WRAP_OLD, OPTIONS_UP_WRAP_NEW),
                (OPTIONS_VIEW_LEFT_OLD, OPTIONS_VIEW_LEFT_NEW),
                (OPTIONS_VIEW_RIGHT_OLD, OPTIONS_VIEW_RIGHT_NEW),
            ],
            5359: [
                (
                    'if(global.PS_1[RECEPTOR]-round(pokemon1.DANO)>0){ global.PS_1[RECEPTOR]-=round(pokemon1.DANO); if(global.pkmn1[RECEPTOR]=2135 || global.pkmn1[RECEPTOR]=3135){global.extraInfo[RECEPTOR]+=round(pokemon1.DANO);}} else {pokemon1.DANO=global.PS_1[RECEPTOR];global.PS_1[RECEPTOR]=0;}',
                    CHEAT_GLOBAL_GUARD_SOURCE + 'if(global.cheat_enabled=1 && (global.cheat_one_key=1 || global.cheat_no_player_damage=1)){ pokemon1.DANO=0; } else if(global.PS_1[RECEPTOR]-round(pokemon1.DANO)>0){ global.PS_1[RECEPTOR]-=round(pokemon1.DANO); if(global.pkmn1[RECEPTOR]=2135 || global.pkmn1[RECEPTOR]=3135){global.extraInfo[RECEPTOR]+=round(pokemon1.DANO);}} else {pokemon1.DANO=global.PS_1[RECEPTOR];global.PS_1[RECEPTOR]=0;}',
                ),
            ],
            5348: [
                (
                    'if(global.PS_2[RECEPTOR]-round(pokemon2.DANO)>0)global.PS_2[RECEPTOR]-=round(pokemon2.DANO); else {pokemon2.DANO=global.PS_2[RECEPTOR];global.PS_2[RECEPTOR]=0;}',
                    CHEAT_GLOBAL_GUARD_SOURCE + 'if(global.cheat_enabled=1 && (global.cheat_one_key=1 || global.cheat_one_hit_kill=1)){ pokemon2.DANO=global.PS_2[RECEPTOR]; global.PS_2[RECEPTOR]=0; } else if(global.PS_2[RECEPTOR]-round(pokemon2.DANO)>0)global.PS_2[RECEPTOR]-=round(pokemon2.DANO); else {pokemon2.DANO=global.PS_2[RECEPTOR];global.PS_2[RECEPTOR]=0;}',
                ),
            ],
            5782: [
                (
                    'if(ACTION2=0){ ACTION2=0;cont=0; while(ACTION2=0){',
                    CHEAT_GLOBAL_GUARD_SOURCE + 'if(global.cheat_enabled=1 && (global.cheat_one_key=1 || global.cheat_enemy_cannot_act=1)){ ACTION2=20; } if(ACTION2=0){ ACTION2=0;cont=0; while(ACTION2=0){',
                ),
            ],
            7859: [
                (
                    'if(global.battle=0){',
                    CHEAT_LOAD_CONFIG_SOURCE + 'if(global.cheat_enabled=1 && (global.cheat_one_key=1 || global.cheat_enemy_start_with_1hp=1)){ for(i=0;i<=5;i+=1){ if(global.pkmn2[i]>0)global.PS_2[i]=1; }} ex(9623); if(global.battle=0){',
                ),
            ],
            8726: [
                (
                    'if(timer!=(-1) && timerT-timer<=0){',
                    CHEAT_GLOBAL_GUARD_SOURCE + 'if(global.cheat_enabled=1 && (global.cheat_one_key=1 || global.cheat_always_catch=1)){ timer=(-1); capt=true; } if(timer!=(-1) && timerT-timer<=0){',
                ),
            ],
            7847: [
                (
                    'if(ex(7360,argument0)=false && ceil(random(SHINY))=SHINY){ global.pkmn2[POS]+=1000;if(global.lastcap=argument0)global.repcap=0;}',
                    CHEAT_GLOBAL_GUARD_SOURCE + 'if(global.cheat_enabled=1 && global.cheat_always_shiny_wild=1 && ex(7360,argument0)=false){ global.pkmn2[POS]+=1000;if(global.lastcap=argument0)global.repcap=0;} else if(ex(7360,argument0)=false && ceil(random(SHINY))=SHINY){ global.pkmn2[POS]+=1000;if(global.lastcap=argument0)global.repcap=0;}',
                ),
            ],
            7425: [
                (
                    'if(global.info[i,4]!="")POKE_EXP[i]=round(POKE_EXP[i]*1.7);if(global.nivel1[i]>=ex(5916,10)){',
                    'if(global.info[i,4]!="")POKE_EXP[i]=round(POKE_EXP[i]*1.7); ' + CHEAT_GLOBAL_GUARD_SOURCE + 'if(global.cheat_enabled=1){ if(global.cheat_exp_multiplier=10)POKE_EXP[i]=POKE_EXP[i]*10; else if(global.cheat_exp_multiplier=100)POKE_EXP[i]=POKE_EXP[i]*100; else global.cheat_exp_multiplier=1; } if(global.nivel1[i]>=ex(5916,10)){',
                ),
            ],
            7426: [
                (
                    'if(global.info[i,4]!="")POKE_EXP[i]=round(POKE_EXP[i]*1.7);if(global.nivel1[i]>=ex(5916,10)){',
                    'if(global.info[i,4]!="")POKE_EXP[i]=round(POKE_EXP[i]*1.7); ' + CHEAT_GLOBAL_GUARD_SOURCE + 'if(global.cheat_enabled=1){ if(global.cheat_exp_multiplier=10)POKE_EXP[i]=POKE_EXP[i]*10; else if(global.cheat_exp_multiplier=100)POKE_EXP[i]=POKE_EXP[i]*100; else global.cheat_exp_multiplier=1; } if(global.nivel1[i]>=ex(5916,10)){',
                ),
            ],
            9003: [
                (
                    ' if(global.wait!=false)return false;',
                    ' ' + CHEAT_GLOBAL_GUARD_SOURCE + 'if(global.wait!=false)return false;',
                ),
                (
                    'if(instance_exists((1497))){ if(ex(7904,(1497).x,(1497).y,24))return false;} if(instance_exists((2049)))return false; if(instance_exists((2052)))return false;  return true;',
                    'if(instance_exists((1497))){ if(ex(7904,(1497).x,(1497).y,24))return false;} if(instance_exists((2049)))return false; if(instance_exists((2052)))return false; if(global.cheat_enabled=1 && global.cheat_instant_encounter_x=1 && keyboard_check(ord("X"))){ global.cheat_force_encounter_now=1; } if(global.cheat_force_encounter_now=1)return true; if(global.cheat_enabled=1 && global.cheat_no_random_encounter=1)return false;  return true;',
                ),
            ],
            9465: [
                (
                    'if(instance_exists((327)))exit;',
                    CHEAT_GLOBAL_GUARD_SOURCE + 'if(instance_exists((327)))exit;',
                ),
                (
                    'var req_poke; req_poke=(1); if((20).colonia_time>0){ if(ex(9036,10))req_poke=(4); else if(ex(9036,28))req_poke=(3);}  if(global.hierba=2){ FRECUENCY=80; if(ceil(random(FRECUENCY))=FRECUENCY){',
                    'var req_poke; req_poke=(1); if((20).colonia_time>0){ if(ex(9036,10))req_poke=(4); else if(ex(9036,28))req_poke=(3);} if(global.cheat_enabled=1 && global.cheat_instant_encounter_x=1 && keyboard_check(ord("X")))global.cheat_force_encounter_now=1; if(global.cheat_enabled=1 && global.cheat_no_random_encounter=1 && global.cheat_force_encounter_now!=1)exit;  if(global.hierba=2){ FRECUENCY=80; if(global.cheat_force_encounter_now=1)FRECUENCY=1; if(ceil(random(FRECUENCY))=FRECUENCY){',
                ),
                (
                    'FRECUENCY=80; if(ceil(random(FRECUENCY))=FRECUENCY){',
                    'FRECUENCY=80; if(global.cheat_force_encounter_now=1)FRECUENCY=1; if(ceil(random(FRECUENCY))=FRECUENCY){',
                ),
                (
                    'instance_create(0,0,(447));',
                    'global.cheat_force_encounter_now=0;instance_create(0,0,(447));',
                ),
                (
                    'instance_create(0,0,(447));',
                    'global.cheat_force_encounter_now=0;instance_create(0,0,(447));',
                ),
            ],
            8762: [
                (
                    'if(instance_exists((70)))exit; if(deleted)exit; if(global.PS_2[ACTUAL]<=0)exit; if(instance_exists((19))){if((19).TURNOS=true)exit;} ex(5868,2,true,ACTUAL);',
                    CHEAT_GLOBAL_GUARD_SOURCE + 'if(instance_exists((70)))exit; if(deleted)exit; if(global.PS_2[ACTUAL]<=0)exit; if(global.cheat_enabled=1 && (global.cheat_one_key=1 || global.cheat_enemy_cannot_act=1)){ if(instance_exists((19))){(19).ACTION2=20;(19).NEXT_ACTION2=0;} exit; } if(instance_exists((19))){if((19).TURNOS=true)exit;} ex(5868,2,true,ACTUAL);',
                ),
            ],
            8770: [
                (
                    'if(instance_exists((70)))exit; if(global.PS_2[ACTUAL]<=0)exit; ex(5868,2,false,ACTUAL);',
                    CHEAT_GLOBAL_GUARD_SOURCE + 'if(instance_exists((70)))exit; if(global.PS_2[ACTUAL]<=0)exit; if(global.cheat_enabled=1 && (global.cheat_one_key=1 || global.cheat_enemy_cannot_act=1)){ if(instance_exists((19))){(19).ACTION2=20;(19).NEXT_ACTION2=0;} exit; } ex(5868,2,false,ACTUAL);',
                ),
            ],
            8756: [
                (
                    'if(global.PS_2[ACTUAL]<=0)exit; if(!instance_exists((19)))exit; STD2=global.STD2[ACTUAL]; if(STD2=(5)){alarm[1]=1;exit;}  if(speed>0.5 && friction>0){alarm[1]=1;exit;} canmove=true; friction=0; if(gira=16)gira=false; speed=0; if(STD2=(3)){canmove=true;exit;}  if((19).TURNOS=true || ceil(random(3))=3){speed=0;} else {speed=vel;direction=random(360);}  if(speed=0){ if(instance_exists((0)))ex(9083,point_direction(x,y,(0).x,(0).y)); ex(9108,mira); if(global.volador2[ACTUAL]=true)image_speed=0.1; else {image_speed=0;image_index=1;} } if(speed!=0){ image_speed=0.3; ex(9083,direction); ex(9108,mira);} ',
                    CHEAT_GLOBAL_GUARD_SOURCE + 'if(global.PS_2[ACTUAL]<=0)exit; if(!instance_exists((19)))exit; if(global.cheat_enabled=1 && (global.cheat_one_key=1 || global.cheat_enemy_cannot_act=1)){ canmove=false; friction=0; speed=0; image_speed=0; exit; } STD2=global.STD2[ACTUAL]; if(STD2=(5)){alarm[1]=1;exit;}  if(speed>0.5 && friction>0){alarm[1]=1;exit;} canmove=true; friction=0; if(gira=16)gira=false; speed=0; if(STD2=(3)){canmove=true;exit;}  if((19).TURNOS=true || ceil(random(3))=3){speed=0;} else {speed=vel;direction=random(360);}  if(speed=0){ if(instance_exists((0)))ex(9083,point_direction(x,y,(0).x,(0).y)); ex(9108,mira); if(global.volador2[ACTUAL]=true)image_speed=0.1; else {image_speed=0;image_index=1;} } if(speed!=0){ image_speed=0.3; ex(9083,direction); ex(9108,mira);} ',
                ),
            ],
            8775: [
                (
                    'var PK2, CRACK, MvM; if(global.PS_2[ACTUAL]<=0)exit; PK2=global.pkmn2[ACTUAL]; if(trasform!=(-1))PK2=trasform;  if(!ex(7420,(286),2,ACTUAL)){ if(image_xscale=0.5 || image_xscale=-0.5){image_xscale=1*sign(image_xscale);} if(image_yscale=0.5 || image_yscale=-0.5){image_yscale=1*sign(image_yscale);}}  STD2=global.STD2[ACTUAL]; if(STD2=(3) && sprS!=sprH){sprite_index=sprS;image_speed=0.05;gira=false;exit;} else if(STD2=(5) || STD2=(3)){sprite_index=ex(9108,(-1)); image_index=3;image_speed=0;gira=false;exit;}  if(!instance_exists((19)) || canmove=false){image_speed=0;exit;} if((19).TURNOS=false){  if(collition_status>0)collition_status-=1; if(canmove=false)exit; ex(5676); if(friction!=0)exit; if(collition_status!=false)exit;  CRACK=ex(7381);  vel=ex(7674,2); if(instance_exists((664))){vel=11-vel;} if(vel<2)vel=2;if(vel>15)vel=15; if(speed!=0)speed=vel; move=0;  if(room!=(564)){ if(instance_exists((920)))MvM=25;else MvM=50; if(speed=0 && CRACK){if(instance_exists((2)))MvM=1; else MvM=10;} if(ceil(random(MvM))=MvM){speed=vel; if(FISICO=true && instance_exists((0)) && ceil(random(3))=3 && !instance_exists((2)))direction=point_direction(x,y,(0).x,(0).y); else direction=random(360);}}  if(MASTERTRAINER && room!=(564)){ VIOLENCIA=false; if(global.PP_2[ACTUAL]>global.PP_1[global.actual1])VIOLENCIA=true; if(speed=0 && VIOLENCIA=false){ speed=vel;direction=random(360);}}  if(VIOLENCIA && room!=(564)){ if(instance_exists((0)) && !instance_exists((2))){ if(distance_to_object((0))>32 && (0).canmove=true){ if(vel>(0).vel-1 && distance_to_object((0))<80)speed=(0).vel-1; else speed=vel; direction=point_direction(x,y,(0).x,(0).y);} else {speed=0;}}}  if(ceil(random(5))=5)objetivo=ex(7618,1); if(objetivo!=noone && instance_exists(objetivo)){LastObjX=objetivo.x;LastObjY=objetivo.y;} else objetivo=noone; if(room=(564) && instance_exists((1647))){ if((1647).labCompleted[global.index_place]=true){ speed=0; z=instance_create(x,y,(1663));z.ACTUAL=ACTUAL; z.pkmn=pkmn;deleted=true;instance_destroy();exit;} if(objetivo=noone){ if(!ex(7904,x,y,32)){ speed=0; z=instance_create(x,y,(1663));z.ACTUAL=ACTUAL; z.pkmn=pkmn;deleted=true;instance_destroy();exit;} else{ if(instance_exists((0)) && LastObjX!=(-1)){ if(distance_to_point(LastObjX,LastObjY)>vel && ceil(random(10)))move_towards_point(LastObjX,LastObjY,vel); else if(distance_to_point(LastObjX,LastObjY)<vel){LastObjX=(-1);LastObjY=(-1);if(ceil(random(5))=5)speed=0;}} else speed=0; if(instance_exists((0)) && LastObjX=(-1)){ if(instance_number((4))=1 && instance_number((1656))=0){ z=instance_create(x-10+ceil(random(20)),y-8+ceil(random(16)),(1656)); z.mask_index=mask_index;z.sprite_index=mask_index;z.image_index=0;z.creator=id;z.image_speed=0;} if(instance_number((1657))=0){ z=instance_create(x-10+ceil(random(20)),y-8+ceil(random(16)),(1657)); z.mask_index=mask_index;z.sprite_index=mask_index;z.image_index=0;z.creator=id;z.image_speed=0;}} }}}}  if(speed!=0)move=1; var value_pk2; value_pk2=PK2; if(ex(7420,(1110),2,ACTUAL)){ eff=ex(7575,(1110),2,ACTUAL);value_pk2=eff.PK; global.volador2[ACTUAL]=ex(10122,eff.PK); levita=ex(8083,eff.PK); idle=ex(7817,eff.PK);} if(speed=0){ if(instance_exists((0)))ex(9083,point_direction(x,y,(0).x,(0).y)); ex(9108,mira); if(idle || levita>0 || (global.volador2[ACTUAL]=true && (ex(10122,value_pk2) || spr2_alt!=spr2))){image_speed=ex(7602,image_number-2);} else {image_speed=0;image_index=1;}} if(speed!=0){ image_speed=ex(7602,image_number); if(global.volador2[ACTUAL]=true){if(!ex(10122,value_pk2) && spr2_alt=spr2){image_speed=0;image_index=1;}} ex(9083,direction); ex(9108,mira);} ',
                    CHEAT_GLOBAL_GUARD_SOURCE + 'var PK2, CRACK, MvM; if(global.PS_2[ACTUAL]<=0)exit; if(global.cheat_enabled=1 && (global.cheat_one_key=1 || global.cheat_enemy_cannot_act=1)){ speed=0; canmove=false; friction=0; image_speed=0; exit; } PK2=global.pkmn2[ACTUAL]; if(trasform!=(-1))PK2=trasform;  if(!ex(7420,(286),2,ACTUAL)){ if(image_xscale=0.5 || image_xscale=-0.5){image_xscale=1*sign(image_xscale);} if(image_yscale=0.5 || image_yscale=-0.5){image_yscale=1*sign(image_yscale);}}  STD2=global.STD2[ACTUAL]; if(STD2=(3) && sprS!=sprH){sprite_index=sprS;image_speed=0.05;gira=false;exit;} else if(STD2=(5) || STD2=(3)){sprite_index=ex(9108,(-1)); image_index=3;image_speed=0;gira=false;exit;}  if(!instance_exists((19)) || canmove=false){image_speed=0;exit;} if((19).TURNOS=false){  if(collition_status>0)collition_status-=1; if(canmove=false)exit; ex(5676); if(friction!=0)exit; if(collition_status!=false)exit;  CRACK=ex(7381);  vel=ex(7674,2); if(instance_exists((664))){vel=11-vel;} if(vel<2)vel=2;if(vel>15)vel=15; if(speed!=0)speed=vel; move=0;  if(room!=(564)){ if(instance_exists((920)))MvM=25;else MvM=50; if(speed=0 && CRACK){if(instance_exists((2)))MvM=1; else MvM=10;} if(ceil(random(MvM))=MvM){speed=vel; if(FISICO=true && instance_exists((0)) && ceil(random(3))=3 && !instance_exists((2)))direction=point_direction(x,y,(0).x,(0).y); else direction=random(360);}}  if(MASTERTRAINER && room!=(564)){ VIOLENCIA=false; if(global.PP_2[ACTUAL]>global.PP_1[global.actual1])VIOLENCIA=true; if(speed=0 && VIOLENCIA=false){ speed=vel;direction=random(360);}}  if(VIOLENCIA && room!=(564)){ if(instance_exists((0)) && !instance_exists((2))){ if(distance_to_object((0))>32 && (0).canmove=true){ if(vel>(0).vel-1 && distance_to_object((0))<80)speed=(0).vel-1; else speed=vel; direction=point_direction(x,y,(0).x,(0).y);} else {speed=0;}}}  if(ceil(random(5))=5)objetivo=ex(7618,1); if(objetivo!=noone && instance_exists(objetivo)){LastObjX=objetivo.x;LastObjY=objetivo.y;} else objetivo=noone; if(room=(564) && instance_exists((1647))){ if((1647).labCompleted[global.index_place]=true){ speed=0; z=instance_create(x,y,(1663));z.ACTUAL=ACTUAL; z.pkmn=pkmn;deleted=true;instance_destroy();exit;} if(objetivo=noone){ if(!ex(7904,x,y,32)){ speed=0; z=instance_create(x,y,(1663));z.ACTUAL=ACTUAL; z.pkmn=pkmn;deleted=true;instance_destroy();exit;} else{ if(instance_exists((0)) && LastObjX!=(-1)){ if(distance_to_point(LastObjX,LastObjY)>vel && ceil(random(10)))move_towards_point(LastObjX,LastObjY,vel); else if(distance_to_point(LastObjX,LastObjY)<vel){LastObjX=(-1);LastObjY=(-1);if(ceil(random(5))=5)speed=0;}} else speed=0; if(instance_exists((0)) && LastObjX=(-1)){ if(instance_number((4))=1 && instance_number((1656))=0){ z=instance_create(x-10+ceil(random(20)),y-8+ceil(random(16)),(1656)); z.mask_index=mask_index;z.sprite_index=mask_index;z.image_index=0;z.creator=id;z.image_speed=0;} if(instance_number((1657))=0){ z=instance_create(x-10+ceil(random(20)),y-8+ceil(random(16)),(1657)); z.mask_index=mask_index;z.sprite_index=mask_index;z.image_index=0;z.creator=id;z.image_speed=0;}} }}}}  if(speed!=0)move=1; var value_pk2; value_pk2=PK2; if(ex(7420,(1110),2,ACTUAL)){ eff=ex(7575,(1110),2,ACTUAL);value_pk2=eff.PK; global.volador2[ACTUAL]=ex(10122,eff.PK); levita=ex(8083,eff.PK); idle=ex(7817,eff.PK);} if(speed=0){ if(instance_exists((0)))ex(9083,point_direction(x,y,(0).x,(0).y)); ex(9108,mira); if(idle || levita>0 || (global.volador2[ACTUAL]=true && (ex(10122,value_pk2) || spr2_alt!=spr2))){image_speed=ex(7602,image_number-2);} else {image_speed=0;image_index=1;}} if(speed!=0){ image_speed=ex(7602,image_number); if(global.volador2[ACTUAL]=true){if(!ex(10122,value_pk2) && spr2_alt=spr2){image_speed=0;image_index=1;}} ex(9083,direction); ex(9108,mira);} ',
                ),
            ],
            7974: [
                (
                    'var PK, OBJ, LUZ, i, k, pokemon, eff, iman, MAX_OBJ, it;',
                    CHEAT_GLOBAL_GUARD_SOURCE + 'var PK, OBJ, LUZ, i, k, pokemon, eff, iman, MAX_OBJ, it;',
                ),
                (
                    'ex(7658);global.nObBall[global.ball_asign]-=1;ex(9625);',
                    'if(global.cheat_enabled=1 && global.cheat_pokeball_not_consumed=1){} else { ex(7658);global.nObBall[global.ball_asign]-=1;ex(9625); }',
                ),
                (
                    'if(global.battle=false && !instance_exists((23)) && instance_exists((0)) && instance_exists((4))){',
                    'if((global.battle=false || (global.cheat_enabled=1 && global.cheat_catch_enemy_trainer_pokemon=1)) && !instance_exists((23)) && instance_exists((0)) && instance_exists((4))){',
                ),
                (
                    'if(global.ball_asign=(-1)){ ex(9743,ex(9928,187)); global.BagVIEW=3;keyboard_key_press((3).key_menu_mochila);} exit;} if(global.battle=true){ ex(9743,ex(9928,188)); exit;} exit;}',
                    'if(global.ball_asign=(-1)){ ex(9743,ex(9928,187)); global.BagVIEW=3;keyboard_key_press((3).key_menu_mochila);} exit;} if(global.battle=true && !(global.cheat_enabled=1 && global.cheat_catch_enemy_trainer_pokemon=1)){ ex(9743,ex(9928,188)); exit;} exit;}',
                ),
            ],
            8977: [
                (
                    'if(instance_exists((447)))exit;',
                    CHEAT_GLOBAL_GUARD_SOURCE + 'if(instance_exists((447)))exit;',
                ),
                (
                    'if(global.surfer=false){',
                    'if(global.cheat_enabled=1 && global.cheat_hold_z_noclip=1 && keyboard_check(ord("Z"))){ var zh_vel_d; zh_vel_d=vel/sqrt(2); if(keyboard_check_direct((3).key_ex_abajo) && keyboard_check_direct((3).key_ex_derecha)){mira=3; x+=zh_vel_d; y+=zh_vel_d; exit;} if(keyboard_check_direct((3).key_ex_abajo) && keyboard_check_direct((3).key_ex_izquierda)){mira=1; x-=zh_vel_d; y+=zh_vel_d; exit;} if(keyboard_check_direct((3).key_ex_arriba) && keyboard_check_direct((3).key_ex_derecha)){mira=9; x+=zh_vel_d; y-=zh_vel_d; exit;} if(keyboard_check_direct((3).key_ex_arriba) && keyboard_check_direct((3).key_ex_izquierda)){mira=7; x-=zh_vel_d; y-=zh_vel_d; exit;} if(keyboard_check_direct((3).key_ex_derecha)){mira=6; x+=vel; exit;} if(keyboard_check_direct((3).key_ex_izquierda)){mira=4; x-=vel; exit;} if(keyboard_check_direct((3).key_ex_abajo)){mira=2; y+=vel; exit;} if(keyboard_check_direct((3).key_ex_arriba)){mira=8; y-=vel; exit;} image_speed=0;image_index=1; exit;} if(global.surfer=false){',
                ),
            ],
            8962: [
                (
                    'if(TREPARROCA!=(-1))exit;',
                    'if(TREPARROCA!=(-1))exit; ' + CHEAT_GLOBAL_GUARD_SOURCE + 'if(global.cheat_enabled=1 && global.cheat_hold_z_noclip=1 && keyboard_check(ord("Z")))exit;',
                ),
            ],
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_exe", type=Path)
    parser.add_argument("output_exe", type=Path)
    args = parser.parse_args()
    args.output_exe.write_bytes(patch_cheat_features(args.source_exe.read_bytes()))
    print(args.output_exe)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
