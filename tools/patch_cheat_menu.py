from __future__ import annotations

from pathlib import Path
import argparse

try:
    from tools.poke_gm80 import patch_script_source, patch_script_source_replace
except ModuleNotFoundError:
    from poke_gm80 import patch_script_source, patch_script_source_replace


CHEAT_LOAD_INITIO_CONTROL_SOURCE = r'''global.raton=true; global.language="es"; global.drawModalSystem=(-1); global.drawModalSel=(-1); global.drawPriorModalSystem=(-1); global.autoBlack=true; window_set_cursor(cr_default); canshoot=true; SEL=0; col1=0; col2=0; MOUSE=(-1); text_op1=""; text_op2=""; text_op3=""; text_op4=""; text_op5="";  key_ini_accion=ord('Z'); key_ini_cancelar=ord('X'); key_ini_entrar=vk_enter; key_ini_salir=vk_escape; key_ini_reinicio=vk_f2; key_ini_cargar=vk_f6; key_ini_info=vk_f12; key_ini_opciones=vk_f11; key_ini_multi=ord('M'); key_ini_nueva=vk_space; key_ini_subir=vk_up; key_ini_bajar=vk_down;  valid=ex(10054); msg_pre=ex(9923,6219); msg_post=ex(9923,6235); msg_limit=ex(9923,6257); global.cheat_enabled=0; global.cheat_one_key=0; global.cheat_no_player_damage=0; global.cheat_one_hit_kill=0; global.cheat_enemy_cannot_act=0; global.cheat_enemy_start_with_1hp=0; global.cheat_always_catch=0; global.cheat_open_menu=false; text_op6="Cheat"; var f, line; if(file_exists("data\cheat.ini")){ f=file_text_open_read("data\cheat.ini"); while(!file_text_eof(f)){ line=file_text_read_string(f); if(string_pos("enabled=",line)=1)global.cheat_enabled=real(string_delete(line,1,8)); else if(string_pos("one_key_cheat=",line)=1)global.cheat_one_key=real(string_delete(line,1,14)); else if(string_pos("no_player_damage=",line)=1)global.cheat_no_player_damage=real(string_delete(line,1,17)); else if(string_pos("one_hit_kill=",line)=1)global.cheat_one_hit_kill=real(string_delete(line,1,13)); else if(string_pos("enemy_cannot_act=",line)=1)global.cheat_enemy_cannot_act=real(string_delete(line,1,18)); else if(string_pos("enemy_start_with_1hp=",line)=1)global.cheat_enemy_start_with_1hp=real(string_delete(line,1,22)); else if(string_pos("always_catch=",line)=1)global.cheat_always_catch=real(string_delete(line,1,13)); file_text_readln(f);} file_text_close(f);}'''

MAIN_MENU_DRAW_SOURCE = r'''draw_set_font((0)); draw_set_halign(fa_center);  var max_sel; if(global.cheat_enabled=1)max_sel=5; else max_sel=4; col1=c_white;col2=c_white;col3=c_white;col4=c_white;col5=c_white;col6=c_white; if(SEL=0){col1=(16744448);} if(SEL=1){col2=(52235);} if(SEL=2){col3=(16742844);} if(SEL=3){col4=(49151);} if(SEL=4 && max_sel=4){col5=c_red;} if(SEL=4 && max_sel=5){col5=(65535);} if(SEL=5){col6=c_red;}  draw_text_color(160,74,text_op1,col1,col1,col1,col1,1); if(SEL=0)draw_text_color(160-1+random(2),74-1+random(2),text_op1,col1,col1,col1,col1,0.3); draw_text_color(160,92,text_op2,col2,col2,col2,col2,1); if(SEL=1)draw_text_color(160-1+random(2),92-1+random(2),text_op2,col2,col2,col2,col2,0.3); draw_text_color(160,110,text_op3,col3,col3,col3,col3,1); if(SEL=2)draw_text_color(160-1+random(2),110-1+random(2),text_op3,col3,col3,col3,col3,0.3); draw_text_color(160,128,text_op4,col4,col4,col4,col4,1); if(SEL=3)draw_text_color(160-1+random(2),128-1+random(2),text_op4,col4,col4,col4,col4,0.3); draw_text_color(160,146,text_op5,col5,col5,col5,col5,1); if(SEL=4)draw_text_color(160-1+random(2),146-1+random(2),text_op5,col5,col5,col5,col5,0.3); if(max_sel=5){ draw_text_color(160,164,text_op6,col6,col6,col6,col6,1); if(SEL=5)draw_text_color(160-1+random(2),164-1+random(2),text_op6,col6,col6,col6,col6,0.3);}  draw_set_halign(fa_left);  if(global.drawPriorModalSystem!=(-1)){ ex(7120); exit;} if(global.drawModalSystem!=(-1)){ ex(7076); exit;}'''

MAIN_MENU_MOUSE_SOURCE = r'''if(mouse_x>=62 && mouse_x<=178 && mouse_y>=75 && mouse_y<=88){ SEL=0; MOUSE=0; exit;} if(mouse_x>=62 && mouse_x<=178 && mouse_y>=93 && mouse_y<=106){ SEL=1; MOUSE=1; exit;} if(mouse_x>=62 && mouse_x<=178 && mouse_y>=111 && mouse_y<=124){ SEL=2; MOUSE=2; exit;} if(mouse_x>=62 && mouse_x<=178 && mouse_y>=129 && mouse_y<=142){ SEL=3; MOUSE=3; exit;} if(mouse_x>=62 && mouse_x<=178 && mouse_y>=147 && mouse_y<=160){ SEL=4; MOUSE=4; exit;} if(global.cheat_enabled=1 && mouse_x>=62 && mouse_x<=178 && mouse_y>=165 && mouse_y<=178){ SEL=5; MOUSE=5; exit;} MOUSE=(-1);'''

MAIN_MENU_KEYS_SOURCE = r'''var key, max_sel; key=false; if(global.cheat_enabled=1)max_sel=5; else max_sel=4;   if(keyboard_check(key_ini_info)){ ex(8218,key_ini_info); ex(9743,ex(7584,(1))); exit;}   if(keyboard_check(key_ini_accion)){ ex(8218,key_ini_accion); keyboard_key_press(key_ini_entrar); exit;}   if(keyboard_check(key_ini_entrar)){ ex(8218,key_ini_entrar); if(SEL=0){key=1;} if(SEL=1){key=2;} if(SEL=2){key=3;} if(SEL=3){key=4;} if(SEL=4 && max_sel=4){key=5;} if(SEL=4 && max_sel=5){key=6;} if(SEL=5){key=5;}}   if(keyboard_check(key_ini_cancelar)){ ex(8218,key_ini_cancelar); keyboard_key_press(key_ini_salir); exit;}   if(keyboard_check(key_ini_salir) || key=5){ ex(8218,key_ini_salir); ex(9192); exit;}   if(keyboard_check(key_ini_reinicio)){ ex(8218,key_ini_reinicio); ex(9103); exit;}   if(keyboard_check(key_ini_nueva) || key=1){ ex(8218,key_ini_nueva); if(!directory_exists("data")){ex(9743,ex(9928,57));exit;} valid=ex(10054); if(valid=0){ex(9744,msg_pre);exit;} if(valid=2){ex(9744,msg_limit);} if(valid=3){ex(9744,msg_post);exit;} if(ex(9747,ex(9928,58))){room=(4);} exit;}   if(keyboard_check(key_ini_cargar) || key=2){ ex(8218,key_ini_cargar); if(!directory_exists("data")){ex(9743,ex(9928,57));exit;} valid=ex(10054); if(valid=0){ex(9744,msg_pre);exit;} if(valid=2){ex(9744,msg_limit);} if(valid=3){ex(9744,msg_post);exit;} room=(48); exit;}   if(keyboard_check(key_ini_multi) || key=3){ ex(8218,key_ini_multi); if(!directory_exists("data")){ex(9743,ex(9928,57));exit;} if(ex(9747,ex(9923,10544))){ instance_create(16,0,(20)); instance_create(0,16,(3)); instance_create(16,16,(389)); instance_create(32,16,(319)); instance_create(16,32,(383)); instance_create(0,48,(587)); instance_create(32,48,(1305)); instance_create(16,64,(1440)); room=(479); }exit;}   if(keyboard_check(key_ini_opciones) || key=4){ ex(8218,key_ini_opciones); if(!directory_exists("data")){ex(9743,ex(9928,57));exit;} global.cheat_open_menu=false; room=(483); exit;}   if(key=6){ if(!directory_exists("data")){ex(9743,ex(9928,57));exit;} global.cheat_open_menu=true; room=(483); exit;}   if(keyboard_check(key_ini_subir)){ if(canshoot=false)exit; window_mouse_set(0,0); canshoot=false;alarm[0]=10; if(SEL=0)SEL=max_sel; else SEL-=1; exit;}   if(keyboard_check(key_ini_bajar)){ if(canshoot=false)exit; window_mouse_set(0,0); canshoot=false;alarm[0]=10; if(SEL=max_sel)SEL=0; else SEL+=1; exit;} '''

OPTIONS_DEFINE_SOURCE = r'''ABAJO=false;VIEW=0; canshoot=true; SEL=0;AVANCE=0;  col0=c_black;col1=c_black;col2=c_black; col3=c_black;col4=c_black;col5=c_black;  str0="";str1="";str2="";str3="";str4="";str5="";  val0="";val1="";val2="";val3="";val4="";val5="";  STR0="";STR1="";STR2="";STR3="";STR4="";STR5=""; STR6="";STR7="";STR8="";STR9="";STR10="";STR11=""; STR12="";STR13="";STR14="";STR15="";STR16="";STR17=""; STR18="";  VAL0="";VAL1="";VAL2="";VAL3="";VAL4="";VAL5=""; VAL6="";VAL7="";VAL8="";VAL9="";VAL10="";VAL11=""; VAL12="";VAL13="";VAL14="";VAL15="";VAL16="";VAL17=""; VAL18="";  f=file_text_open_read("data\text\lan.txt"); IDIOMA_ACTUAL=0;NUM_LAN=0; while(!file_text_eof(f)){NUM_LAN+=1;file_text_readln(f);} file_text_close(f);  f=file_text_open_read("data\text\lan.txt"); for(i=0;i<NUM_LAN;i+=1){ linea=file_text_read_string(f); LAN_FOL[i]=string_copy(linea,0,2); LAN_TXT[i]=string_copy(linea,4,ex(9827,linea)-1); if(global.language=LAN_FOL[i])IDIOMA_ACTUAL=i; file_text_readln(f);} file_text_close(f);  f=file_text_open_read("data\audio\musica\audio.txt"); FOLDERMUSIC_ACTUAL=0;NUM_FOLDER=0; while(!file_text_eof(f)){NUM_FOLDER+=1;file_text_readln(f);} file_text_close(f);  f=file_text_open_read("data\audio\musica\audio.txt"); for(i=0;i<NUM_FOLDER;i+=1){ linea=file_text_read_string(f); MUS_FOL[i]=string_copy(linea,0,2); MUS_TXT[i]=string_copy(linea,4,ex(9827,linea)-1); if(global.foldermusic=MUS_FOL[i])FOLDERMUSIC_ACTUAL=i; file_text_readln(f);} file_text_close(f);  ex(7829,ex(7836));  ex(9438);  PORCENTAJE=string(ex(8886))+"%"; if(global.cheat_open_menu=true){ VIEW=5; ABAJO=true; SEL=0; global.cheat_open_menu=false; }'''

OPTIONS_TEXTS_APPEND_OLD = 'txt_otr18=ex(9928,1499); txt_otr19=ex(9928,1500); txt_otr20=ex(9928,1501); txt_otr21=ex(9928,2454);  acc=195;'
OPTIONS_TEXTS_APPEND_NEW = 'txt_otr18=ex(9928,1499); txt_otr19=ex(9928,1500); txt_otr20=ex(9928,1501); txt_otr21=ex(9928,2454); txt_cht1="One-Key Cheat"; txt_cht2="No Player Damage"; txt_cht3="One Hit Kill"; txt_cht4="Enemy Cannot Act"; txt_cht5="Enemy Start With 1 HP"; txt_cht6="Always Catch"; txt_locked="Locked";  acc=195;'

OPTIONS_VALUES_INSERT_OLD = ' if(VIEW=4){ if(global.primerosiempreactual=false){STR0=txt_otr1;VAL0=txt_otr2;} else {STR0=txt_otr1;VAL0=txt_otr3;} if(global.show_ponermote=true){STR1=txt_otr7;VAL1=txt_on;} else {STR1=txt_otr7;VAL1=txt_off;} if(global.show_avisos_mision=true){STR2=txt_avmis;VAL2=txt_on;} else {STR2=txt_avmis;VAL2=txt_off;} if(global.show_avisos_objetivo=true){STR3=txt_avobj;VAL3=txt_on;} else {STR3=txt_avobj;VAL3=txt_off;} STR4=txt_otr18; if(global.sistema_medida=0)VAL4=txt_otr19; else VAL4=txt_otr20; if(global.dificultad=1)DIF=txt_otr11;if(global.dificultad=2)DIF=txt_otr12;if(global.dificultad=3)DIF=txt_otr13; if(global.dificultad=4)DIF=txt_otr21;if(global.dificultad=5)DIF=txt_otr15;if(global.dificultad=6)DIF=txt_otr14; STR5=txt_otr16;VAL5=DIF; STR6=txt_otr17;VAL6=PORCENTAJE; if(SEL>=4){AVANCE=1;} }  if(AVANCE=0){'
OPTIONS_VALUES_INSERT_NEW = ' if(VIEW=4){ if(global.primerosiempreactual=false){STR0=txt_otr1;VAL0=txt_otr2;} else {STR0=txt_otr1;VAL0=txt_otr3;} if(global.show_ponermote=true){STR1=txt_otr7;VAL1=txt_on;} else {STR1=txt_otr7;VAL1=txt_off;} if(global.show_avisos_mision=true){STR2=txt_avmis;VAL2=txt_on;} else {STR2=txt_avmis;VAL2=txt_off;} if(global.show_avisos_objetivo=true){STR3=txt_avobj;VAL3=txt_on;} else {STR3=txt_avobj;VAL3=txt_off;} STR4=txt_otr18; if(global.sistema_medida=0)VAL4=txt_otr19; else VAL4=txt_otr20; if(global.dificultad=1)DIF=txt_otr11;if(global.dificultad=2)DIF=txt_otr12;if(global.dificultad=3)DIF=txt_otr13; if(global.dificultad=4)DIF=txt_otr21;if(global.dificultad=5)DIF=txt_otr15;if(global.dificultad=6)DIF=txt_otr14; STR5=txt_otr16;VAL5=DIF; STR6=txt_otr17;VAL6=PORCENTAJE; if(SEL>=4){AVANCE=1;} }  if(VIEW=5){ STR0=txt_cht1; if(global.cheat_one_key=1)VAL0=txt_on; else VAL0=txt_off; STR1=txt_cht2; STR2=txt_cht3; STR3=txt_cht4; STR4=txt_cht5; STR5=txt_cht6; if(global.cheat_one_key=1){VAL1=txt_on;VAL2=txt_on;VAL3=txt_on;VAL4=txt_on;VAL5=txt_on;} else { if(global.cheat_no_player_damage=1)VAL1=txt_on; else VAL1=txt_off; if(global.cheat_one_hit_kill=1)VAL2=txt_on; else VAL2=txt_off; if(global.cheat_enemy_cannot_act=1)VAL3=txt_on; else VAL3=txt_off; if(global.cheat_enemy_start_with_1hp=1)VAL4=txt_on; else VAL4=txt_off; if(global.cheat_always_catch=1)VAL5=txt_on; else VAL5=txt_off; } if(SEL>=4){AVANCE=SEL-3;} }  if(AVANCE=0){'

OPTIONS_ACTION_INSERT_OLD = ' if(VIEW=4){ if(SEL=0){if(global.primerosiempreactual=true){global.primerosiempreactual=false;} else {global.primerosiempreactual=true;}} if(SEL=1){if(global.show_ponermote=true)global.show_ponermote=false; else global.show_ponermote=true;} if(SEL=2){if(global.show_avisos_mision=true){global.show_avisos_mision=false;} else {global.show_avisos_mision=true;}} if(SEL=3){if(global.show_avisos_objetivo=true){global.show_avisos_objetivo=false;} else {global.show_avisos_objetivo=true;}} if(SEL=4){ if(global.sistema_medida=0)global.sistema_medida=1; else global.sistema_medida=0;} if(SEL=5){ if(global.dificultad=6)global.dificultad=1;else global.dificultad+=1; if((20).MEDALLA_STAR[1]!=false && global.dificultad=1)global.dificultad=2; if(global.dificultad=1){global.PowDif1=2;global.PowDif2=4;exit;}if(global.dificultad=2){global.PowDif1=4;global.PowDif2=4;exit;}if(global.dificultad=3){global.PowDif1=4;global.PowDif2=2;exit;}if(global.dificultad=4){global.PowDif1=2;global.PowDif2=2;exit;}if(global.dificultad=5){global.PowDif1=1;global.PowDif2=1;exit;}if(global.dificultad=6){global.PowDif1=4;global.PowDif2=1;exit;}}} exit;}'
OPTIONS_ACTION_INSERT_NEW = ' if(VIEW=4){ if(SEL=0){if(global.primerosiempreactual=true){global.primerosiempreactual=false;} else {global.primerosiempreactual=true;}} if(SEL=1){if(global.show_ponermote=true)global.show_ponermote=false; else global.show_ponermote=true;} if(SEL=2){if(global.show_avisos_mision=true){global.show_avisos_mision=false;} else {global.show_avisos_mision=true;}} if(SEL=3){if(global.show_avisos_objetivo=true){global.show_avisos_objetivo=false;} else {global.show_avisos_objetivo=true;}} if(SEL=4){ if(global.sistema_medida=0)global.sistema_medida=1; else global.sistema_medida=0;} if(SEL=5){ if(global.dificultad=6)global.dificultad=1;else global.dificultad+=1; if((20).MEDALLA_STAR[1]!=false && global.dificultad=1)global.dificultad=2; if(global.dificultad=1){global.PowDif1=2;global.PowDif2=4;exit;}if(global.dificultad=2){global.PowDif1=4;global.PowDif2=4;exit;}if(global.dificultad=3){global.PowDif1=4;global.PowDif2=2;exit;}if(global.dificultad=4){global.PowDif1=2;global.PowDif2=2;exit;}if(global.dificultad=5){global.PowDif1=1;global.PowDif2=1;exit;}if(global.dificultad=6){global.PowDif1=4;global.PowDif2=1;exit;}}} if(VIEW=5){ if(SEL=0){ if(global.cheat_one_key=1)global.cheat_one_key=0; else global.cheat_one_key=1; } else if(global.cheat_one_key=0){ if(SEL=1){ if(global.cheat_no_player_damage=1)global.cheat_no_player_damage=0; else global.cheat_no_player_damage=1; } if(SEL=2){ if(global.cheat_one_hit_kill=1)global.cheat_one_hit_kill=0; else global.cheat_one_hit_kill=1; } if(SEL=3){ if(global.cheat_enemy_cannot_act=1)global.cheat_enemy_cannot_act=0; else global.cheat_enemy_cannot_act=1; } if(SEL=4){ if(global.cheat_enemy_start_with_1hp=1)global.cheat_enemy_start_with_1hp=0; else global.cheat_enemy_start_with_1hp=1; } if(SEL=5){ if(global.cheat_always_catch=1)global.cheat_always_catch=0; else global.cheat_always_catch=1; } } f=file_text_open_write("data\\cheat.ini"); file_text_write_string(f,"[cheat]"); file_text_writeln(f); file_text_write_string(f,"enabled="+string(global.cheat_enabled)); file_text_writeln(f); file_text_write_string(f,"one_key_cheat="+string(global.cheat_one_key)); file_text_writeln(f); file_text_write_string(f,"no_player_damage="+string(global.cheat_no_player_damage)); file_text_writeln(f); file_text_write_string(f,"one_hit_kill="+string(global.cheat_one_hit_kill)); file_text_writeln(f); file_text_write_string(f,"enemy_cannot_act="+string(global.cheat_enemy_cannot_act)); file_text_writeln(f); file_text_write_string(f,"enemy_start_with_1hp="+string(global.cheat_enemy_start_with_1hp)); file_text_writeln(f); file_text_write_string(f,"always_catch="+string(global.cheat_always_catch)); file_text_writeln(f); file_text_close(f); } exit;}'

OPTIONS_MAXNUM_OLD = ' if(VIEW=0)max_num=11; if(VIEW=1)max_num=18; if(VIEW=2)max_num=6; if(VIEW=3)max_num=12; if(VIEW=4)max_num=6;'
OPTIONS_MAXNUM_NEW = ' if(VIEW=0)max_num=11; if(VIEW=1)max_num=18; if(VIEW=2)max_num=6; if(VIEW=3)max_num=12; if(VIEW=4)max_num=6; if(VIEW=5)max_num=5;'

OPTIONS_VIEW_LEFT_OLD = ' if(ABAJO=false){ if(VIEW=0)VIEW=4; else VIEW-=1; exit;}'
OPTIONS_VIEW_LEFT_NEW = ' if(ABAJO=false){ if(global.cheat_enabled=1){ if(VIEW=0)VIEW=5; else VIEW-=1; } else { if(VIEW=0)VIEW=4; else VIEW-=1; } exit;}'

OPTIONS_VIEW_RIGHT_OLD = ' if(ABAJO=false){ if(VIEW=4)VIEW=0; else VIEW+=1; exit;}'
OPTIONS_VIEW_RIGHT_NEW = ' if(ABAJO=false){ if(global.cheat_enabled=1){ if(VIEW=5)VIEW=0; else VIEW+=1; } else { if(VIEW=4)VIEW=0; else VIEW+=1; } exit;}'


def patch_cheat_features(raw: bytes) -> bytes:
    patched = raw
    patched = patch_script_source(patched, 6348, CHEAT_LOAD_INITIO_CONTROL_SOURCE)
    patched = patch_script_source(patched, 7038, MAIN_MENU_DRAW_SOURCE)
    patched = patch_script_source(patched, 7991, MAIN_MENU_KEYS_SOURCE)
    patched = patch_script_source(patched, 8442, MAIN_MENU_MOUSE_SOURCE)
    patched = patch_script_source(patched, 9436, OPTIONS_DEFINE_SOURCE)
    patched = patch_script_source_replace(patched, 9438, OPTIONS_TEXTS_APPEND_OLD, OPTIONS_TEXTS_APPEND_NEW)
    patched = patch_script_source_replace(patched, 9442, OPTIONS_VALUES_INSERT_OLD, OPTIONS_VALUES_INSERT_NEW)
    patched = patch_script_source_replace(patched, 9441, OPTIONS_ACTION_INSERT_OLD, OPTIONS_ACTION_INSERT_NEW)
    patched = patch_script_source_replace(patched, 9441, OPTIONS_MAXNUM_OLD, OPTIONS_MAXNUM_NEW)
    patched = patch_script_source_replace(patched, 9441, OPTIONS_VIEW_LEFT_OLD, OPTIONS_VIEW_LEFT_NEW)
    patched = patch_script_source_replace(patched, 9441, OPTIONS_VIEW_RIGHT_OLD, OPTIONS_VIEW_RIGHT_NEW)

    patched = patch_script_source_replace(
        patched,
        5359,
        'if(global.PS_1[RECEPTOR]-round(pokemon1.DANO)>0){ global.PS_1[RECEPTOR]-=round(pokemon1.DANO); if(global.pkmn1[RECEPTOR]=2135 || global.pkmn1[RECEPTOR]=3135){global.extraInfo[RECEPTOR]+=round(pokemon1.DANO);}} else {pokemon1.DANO=global.PS_1[RECEPTOR];global.PS_1[RECEPTOR]=0;}',
        'if(global.cheat_enabled=1 && (global.cheat_one_key=1 || global.cheat_no_player_damage=1)){ pokemon1.DANO=0; } else if(global.PS_1[RECEPTOR]-round(pokemon1.DANO)>0){ global.PS_1[RECEPTOR]-=round(pokemon1.DANO); if(global.pkmn1[RECEPTOR]=2135 || global.pkmn1[RECEPTOR]=3135){global.extraInfo[RECEPTOR]+=round(pokemon1.DANO);}} else {pokemon1.DANO=global.PS_1[RECEPTOR];global.PS_1[RECEPTOR]=0;}',
    )
    patched = patch_script_source_replace(
        patched,
        5348,
        'if(global.PS_2[RECEPTOR]-round(pokemon2.DANO)>0)global.PS_2[RECEPTOR]-=round(pokemon2.DANO); else {pokemon2.DANO=global.PS_2[RECEPTOR];global.PS_2[RECEPTOR]=0;}',
        'if(global.cheat_enabled=1 && (global.cheat_one_key=1 || global.cheat_one_hit_kill=1)){ pokemon2.DANO=global.PS_2[RECEPTOR]; global.PS_2[RECEPTOR]=0; } else if(global.PS_2[RECEPTOR]-round(pokemon2.DANO)>0)global.PS_2[RECEPTOR]-=round(pokemon2.DANO); else {pokemon2.DANO=global.PS_2[RECEPTOR];global.PS_2[RECEPTOR]=0;}',
    )
    patched = patch_script_source_replace(
        patched,
        5782,
        'if(ACTION2=0){ ACTION2=0;cont=0; while(ACTION2=0){',
        'if(global.cheat_enabled=1 && (global.cheat_one_key=1 || global.cheat_enemy_cannot_act=1)){ ACTION2=0; } if(ACTION2=0){ ACTION2=0;cont=0; while(ACTION2=0){',
    )
    patched = patch_script_source_replace(
        patched,
        7859,
        'if(global.battle=0){',
        'if(global.cheat_enabled=1 && (global.cheat_one_key=1 || global.cheat_enemy_start_with_1hp=1)){ for(i=0;i<=5;i+=1){ if(global.pkmn2[i]>0)global.PS_2[i]=1; }} if(global.battle=0){',
    )
    patched = patch_script_source_replace(
        patched,
        8726,
        'if(timer!=(-1) && timerT-timer<=0){',
        'if(global.cheat_enabled=1 && (global.cheat_one_key=1 || global.cheat_always_catch=1)){ timer=(-1); capt=true; } if(timer!=(-1) && timerT-timer<=0){',
    )
    return patched


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
