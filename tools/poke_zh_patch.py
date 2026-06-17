from __future__ import annotations

from pathlib import Path
import argparse

try:
    from tools.poke_gm80 import patch_script_batch, patch_script_source, patch_script_source_replace
except ModuleNotFoundError:
    from poke_gm80 import patch_script_batch, patch_script_source, patch_script_source_replace


DRAW_GRAFITI_EXT_SOURCE = (
    'if(argument0="")exit;  var col, st, X, Y, shadow, alpha, align, key, path, spr, drawX, layout_path, layout_key, key_no_page, page_suffix, base_no_page, suffix, token, rest, cut, item_key, item_text, component_text, item_w, item_h, totalw, totalh, linew, lineh, surf, xpos, ypos, entry_spr, param1kind, param1value, param2kind, param2value, param3kind, param3value, pos_page, pos_par, f; '
    "st=argument0; shadow=c_black; X=argument1;Y=argument2; "
    "col=argument3;align=argument4;alpha=argument5; "
    'if(!variable_global_exists("zh_text_key_map"))global.zh_text_key_map=(-1); '
    'if(!variable_global_exists("zh_sprite_cache"))global.zh_sprite_cache=(-1); '
    "if((color_get_red(col)+color_get_green(col)+color_get_blue(col))/3<60)shadow=c_white; "
    'if(global.language="zh" && global.zh_text_key_map!=(-1)){ '
    "if(ds_map_exists(global.zh_text_key_map,st)){ "
    "key=ds_map_find_value(global.zh_text_key_map,st); "
    "spr=(-1); "
    "if(global.zh_sprite_cache=(-1))global.zh_sprite_cache=ds_map_create(); "
    "if(ds_map_exists(global.zh_sprite_cache,key))spr=ds_map_find_value(global.zh_sprite_cache,key); "
    "if(spr=(-1) || !sprite_exists(spr)){ "
    'path=working_directory+"\\\\data\\\\text\\\\zh\\\\render\\\\"+key+".png"; '
    "if(file_exists(path)){ "
    "spr=sprite_add(path,-1,0,0,0,0); "
    "if(ds_map_exists(global.zh_sprite_cache,key))ds_map_replace(global.zh_sprite_cache,key,spr); "
    "else ds_map_add(global.zh_sprite_cache,key,spr); "
    "} else { "
    'page_suffix=""; key_no_page=key; pos_page=string_pos("__page__",key); '
    'if(pos_page>0){ page_suffix=string_copy(key,pos_page,ex(9827,key)-pos_page+1); key_no_page=string_copy(key,1,pos_page-1);} '
    'pos_par=string_pos("__par",key_no_page); base_no_page=key_no_page; '
    'if(pos_par>0)base_no_page=string_copy(key_no_page,1,pos_par-1); '
    'layout_key=base_no_page+page_suffix; '
    'layout_path=working_directory+"\\\\data\\\\text\\\\zh\\\\render\\\\"+layout_key+"__layout.txt"; '
    "if(file_exists(layout_path)){ "
    'param1kind=""; param1value=""; param2kind=""; param2value=""; param3kind=""; param3value=""; '
    'suffix=string_delete(key_no_page,1,ex(9827,base_no_page)); '
    'if(string_copy(suffix,1,11)="__par1raw__"){ param1kind="raw"; suffix=string_delete(suffix,1,11); cut=string_pos("__par2__",suffix); if(cut=0 || (string_pos("__par2raw__",suffix)>0 && string_pos("__par2raw__",suffix)<cut))cut=string_pos("__par2raw__",suffix); if(cut=0 || (string_pos("__par3__",suffix)>0 && string_pos("__par3__",suffix)<cut))cut=string_pos("__par3__",suffix); if(cut=0 || (string_pos("__par3raw__",suffix)>0 && string_pos("__par3raw__",suffix)<cut))cut=string_pos("__par3raw__",suffix); if(cut=0){ param1value=suffix; suffix=""; } else { param1value=string_copy(suffix,1,cut-1); suffix=string_delete(suffix,1,cut-1); }} '
    'else if(string_copy(suffix,1,8)="__par1__"){ param1kind="key"; suffix=string_delete(suffix,1,8); cut=string_pos("__par2__",suffix); if(cut=0 || (string_pos("__par2raw__",suffix)>0 && string_pos("__par2raw__",suffix)<cut))cut=string_pos("__par2raw__",suffix); if(cut=0 || (string_pos("__par3__",suffix)>0 && string_pos("__par3__",suffix)<cut))cut=string_pos("__par3__",suffix); if(cut=0 || (string_pos("__par3raw__",suffix)>0 && string_pos("__par3raw__",suffix)<cut))cut=string_pos("__par3raw__",suffix); if(cut=0){ param1value=suffix; suffix=""; } else { param1value=string_copy(suffix,1,cut-1); suffix=string_delete(suffix,1,cut-1); }} '
    'if(string_copy(suffix,1,11)="__par2raw__"){ param2kind="raw"; suffix=string_delete(suffix,1,11); cut=string_pos("__par3__",suffix); if(cut=0 || (string_pos("__par3raw__",suffix)>0 && string_pos("__par3raw__",suffix)<cut))cut=string_pos("__par3raw__",suffix); if(cut=0){ param2value=suffix; suffix=""; } else { param2value=string_copy(suffix,1,cut-1); suffix=string_delete(suffix,1,cut-1); }} '
    'else if(string_copy(suffix,1,8)="__par2__"){ param2kind="key"; suffix=string_delete(suffix,1,8); cut=string_pos("__par3__",suffix); if(cut=0 || (string_pos("__par3raw__",suffix)>0 && string_pos("__par3raw__",suffix)<cut))cut=string_pos("__par3raw__",suffix); if(cut=0){ param2value=suffix; suffix=""; } else { param2value=string_copy(suffix,1,cut-1); suffix=string_delete(suffix,1,cut-1); }} '
    'if(string_copy(suffix,1,11)="__par3raw__"){ param3kind="raw"; param3value=string_delete(suffix,1,11);} '
    'else if(string_copy(suffix,1,8)="__par3__"){ param3kind="key"; param3value=string_delete(suffix,1,8);} '
    "f=file_text_open_read(layout_path); layout=file_text_read_string(f); file_text_close(f); "
    "draw_set_font((3)); draw_set_halign(fa_left); "
    'rest=layout; totalw=0; totalh=0; linew=0; lineh=0; '
    "while(true){ "
    'cut=string_pos("|",rest); if(cut>0){ token=string_copy(rest,1,cut-1); rest=string_delete(rest,1,cut); } else { token=rest; rest=""; } '
    'if(token!="" && string_copy(token,1,1)!="w"){ '
    'if(token="br"){ if(lineh<=0)lineh=string_height(" "); if(linew>totalw)totalw=linew; if(totalh>0)totalh+=4; totalh+=lineh; linew=0; lineh=0; } '
    'else { item_key=""; item_text=""; item_w=0; item_h=0; entry_spr=(-1); '
    'if(string_copy(token,1,3)="seg"){ item_key=layout_key+"__seg__"+string_delete(token,1,3); } '
    'else if(token="par1"){ if(param1kind="key")item_key=param1value; else item_text=param1value; } '
    'else if(token="par2"){ if(param2kind="key")item_key=param2value; else item_text=param2value; } '
    'else if(token="par3"){ if(param3kind="key")item_key=param3value; else item_text=param3value; } '
    'if(item_key!=""){ if(ds_map_exists(global.zh_sprite_cache,item_key))entry_spr=ds_map_find_value(global.zh_sprite_cache,item_key); if(entry_spr=(-1) || !sprite_exists(entry_spr)){ path=working_directory+"\\\\data\\\\text\\\\zh\\\\render\\\\"+item_key+".png"; if(file_exists(path)){ entry_spr=sprite_add(path,-1,0,0,0,0); if(ds_map_exists(global.zh_sprite_cache,item_key))ds_map_replace(global.zh_sprite_cache,item_key,entry_spr); else ds_map_add(global.zh_sprite_cache,item_key,entry_spr); }} if(entry_spr!=(-1) && sprite_exists(entry_spr)){ item_w=sprite_get_width(entry_spr); item_h=sprite_get_height(entry_spr); }} '
    'else if(item_text!=""){ item_w=string_width(item_text); item_h=string_height(item_text); } '
    'linew+=item_w; if(item_h>lineh)lineh=item_h; }} '
    'if(rest="")break; } '
    'if(lineh<=0)lineh=string_height(" "); if(linew>totalw)totalw=linew; if(totalh>0)totalh+=4; totalh+=lineh; '
    "if(totalw<1)totalw=1; if(totalh<1)totalh=1; "
    "surf=surface_create(totalw,totalh); "
    "if(surface_exists(surf)){ "
    "surface_set_target(surf); draw_clear_alpha(c_black,0); draw_set_color(c_white); draw_set_font((3)); draw_set_halign(fa_left); "
    'rest=layout; xpos=0; ypos=0; lineh=0; '
    "while(true){ "
    'cut=string_pos("|",rest); if(cut>0){ token=string_copy(rest,1,cut-1); rest=string_delete(rest,1,cut); } else { token=rest; rest=""; } '
    'if(token!="" && string_copy(token,1,1)!="w"){ '
    'if(token="br"){ if(lineh<=0)lineh=string_height(" "); ypos+=lineh+4; xpos=0; lineh=0; } '
    'else { item_key=""; item_text=""; item_w=0; item_h=0; entry_spr=(-1); '
    'if(string_copy(token,1,3)="seg"){ item_key=layout_key+"__seg__"+string_delete(token,1,3); } '
    'else if(token="par1"){ if(param1kind="key")item_key=param1value; else item_text=param1value; } '
    'else if(token="par2"){ if(param2kind="key")item_key=param2value; else item_text=param2value; } '
    'else if(token="par3"){ if(param3kind="key")item_key=param3value; else item_text=param3value; } '
    'if(item_key!=""){ if(ds_map_exists(global.zh_sprite_cache,item_key))entry_spr=ds_map_find_value(global.zh_sprite_cache,item_key); if(entry_spr=(-1) || !sprite_exists(entry_spr)){ path=working_directory+"\\\\data\\\\text\\\\zh\\\\render\\\\"+item_key+".png"; if(file_exists(path)){ entry_spr=sprite_add(path,-1,0,0,0,0); if(ds_map_exists(global.zh_sprite_cache,item_key))ds_map_replace(global.zh_sprite_cache,item_key,entry_spr); else ds_map_add(global.zh_sprite_cache,item_key,entry_spr); }} if(entry_spr!=(-1) && sprite_exists(entry_spr)){ item_w=sprite_get_width(entry_spr); item_h=sprite_get_height(entry_spr); draw_sprite(entry_spr,0,xpos,ypos); }} '
    'else if(item_text!=""){ item_w=string_width(item_text); item_h=string_height(item_text); component_text=item_text; draw_text(xpos,ypos,component_text); } '
    'xpos+=item_w; if(item_h>lineh)lineh=item_h; }} '
    'if(rest="")break; } '
    "surface_reset_target(); spr=sprite_create_from_surface(surf,0,0,totalw,totalh,0,0,0,0); surface_free(surf); "
    "if(spr!=(-1)){ if(ds_map_exists(global.zh_sprite_cache,key))ds_map_replace(global.zh_sprite_cache,key,spr); else ds_map_add(global.zh_sprite_cache,key,spr); } "
    "} "
    "} "
    "} "
    "} "
    "if(spr!=(-1) && sprite_exists(spr)){ "
    "drawX=X; "
    "if(align=fa_center)drawX-=sprite_get_width(spr)/2; "
    "if(align=fa_right)drawX-=sprite_get_width(spr); "
    "draw_sprite_ext(spr,0,drawX+1,Y+1,1,1,0,shadow,alpha); "
    "draw_sprite_ext(spr,0,drawX,Y+1,1,1,0,shadow,alpha); "
    "draw_sprite_ext(spr,0,drawX+1,Y,1,1,0,shadow,alpha); "
    "draw_sprite_ext(spr,0,drawX,Y,1,1,0,col,alpha); "
    "exit; "
    "} "
    "} "
    "} "
    "draw_set_font((3)); draw_set_halign(argument4); "
    "draw_text_color(X+1,Y+1,st,shadow,shadow,shadow,shadow,alpha); "
    "draw_text_color(X,Y+1,st,shadow,shadow,shadow,shadow,alpha); "
    "draw_text_color(X+1,Y,st,shadow,shadow,shadow,shadow,alpha); "
    "draw_text_color(X,Y,st,col,col,col,col,alpha); "
)

DRAW_TEXT_SHADOW_SOURCE = (
    'if(argument2="")exit; if(!variable_global_exists("zh_text_key_map"))global.zh_text_key_map=(-1); '
    'if(global.language="zh" && global.zh_text_key_map!=(-1) && ds_map_exists(global.zh_text_key_map,argument2)){ '
    "ex(7028,argument2,argument0,argument1,argument3,fa_left,1); exit; } "
    'if(argument5=false){ if((color_get_red(argument3)+color_get_green(argument3)+color_get_blue(argument3))/3<60)argument4=c_white; } '
    "draw_text_color(argument0+1,argument1+1,argument2,argument4,argument4,argument4,argument4,1); "
    "draw_text_color(argument0,argument1+1,argument2,argument4,argument4,argument4,argument4,1); "
    "draw_text_color(argument0+1,argument1,argument2,argument4,argument4,argument4,argument4,1); "
    "draw_text_color(argument0,argument1,argument2,argument3,argument3,argument3,argument3,1); "
)

TEXT_READER_SOURCE = (
    "var f, i, txt, txt_final, filename, line, folder; filename=argument0; line=argument1; folder=global.language; txt=\"\";txt_final=\"\"; "
    'if(!variable_global_exists("zh_text_key_map"))global.zh_text_key_map=(-1); '
    'if(!variable_global_exists("zh_text_last_key"))global.zh_text_last_key=""; '
    "if(filename=\"ordenPokemonExtended\")folder=\"zz\"; if(filename=\"dex_height_ft\")folder=\"zz\"; if(filename=\"dex_height_m\")folder=\"zz\"; "
    "if(filename=\"dex_weight_kg\")folder=\"zz\"; if(filename=\"dex_weight_lb\")folder=\"zz\";  "
    'if(!file_exists("data\\\\text\\\\"+folder+"\\\\"+filename+".dll"))return("???"); '
    'f=file_text_open_read("data\\\\text\\\\"+folder+"\\\\"+filename+".dll");  '
    "for(i=1;i<line;i+=1){ "
    "if(file_text_eof(f))"
    "{"
    "file_text_close(f);"
    'return"???";'
    "} "
    "file_text_readln(f); } "
    "txt=txt+file_text_read_string(f); file_text_close(f);  "
    'if(txt="")return"???"; else if(txt=" ")return("");  '
    "for(i=1;i<=ex(9827,txt);i+=1){ txt_final+=chr(ex(10060,ord(string_char_at(txt,i))));} "
    "txt_final=ex(9802,txt_final); "
    'if(global.language="zh"){ '
    "if(global.zh_text_key_map=(-1))global.zh_text_key_map=ds_map_create(); "
    'global.zh_text_last_key=folder+"__"+filename+"__"+string(line); '
    "if(ds_map_exists(global.zh_text_key_map,txt_final))ds_map_replace(global.zh_text_key_map,txt_final,global.zh_text_last_key); "
    "else ds_map_add(global.zh_text_key_map,txt_final,global.zh_text_last_key); "
    "} "
    "return(txt_final); "
)

TEXT_DIALOG_SOURCE = (
    'var txt; txt=ex(9942,"txt_dialog",argument0); txt=string_replace_all(txt, "$prota$", ex(9202)); '
    'txt=string_replace_all(txt, "$rival$", global.rivalname); txt=string_replace_all(txt,"...","\\x85"); '
    'if(!variable_global_exists("zh_text_key_map"))global.zh_text_key_map=(-1); '
    'if(!variable_global_exists("zh_text_last_key"))global.zh_text_last_key=""; '
    'if(global.language="zh" && global.zh_text_key_map!=(-1)){ '
    "if(ds_map_exists(global.zh_text_key_map,txt))ds_map_replace(global.zh_text_key_map,txt,global.zh_text_last_key); "
    "else ds_map_add(global.zh_text_key_map,txt,global.zh_text_last_key); "
    "} "
    "return(txt); "
)

TEXT_MENU_SOURCE = (
    'var txt; txt=ex(9942,"txt_menu",argument0); txt=string_replace_all(txt, "$prota$", ex(9202)); '
    'txt=string_replace_all(txt, "$rival$", global.rivalname); '
    'if(!variable_global_exists("zh_text_key_map"))global.zh_text_key_map=(-1); '
    'if(!variable_global_exists("zh_text_last_key"))global.zh_text_last_key=""; '
    'if(global.language="zh" && global.zh_text_key_map!=(-1)){ '
    "if(ds_map_exists(global.zh_text_key_map,txt))ds_map_replace(global.zh_text_key_map,txt,global.zh_text_last_key); "
    "else ds_map_add(global.zh_text_key_map,txt,global.zh_text_last_key); "
    "} "
    "return(txt); "
)

TEXT_CARTEL_SOURCE = (
    'var txt; txt=ex(9942,"txt_cartel",argument0); txt=string_replace_all(txt, "$prota$", ex(9202)); '
    'txt=string_replace_all(txt, "$rival$", global.rivalname); '
    'if(!variable_global_exists("zh_text_key_map"))global.zh_text_key_map=(-1); '
    'if(!variable_global_exists("zh_text_last_key"))global.zh_text_last_key=""; '
    'if(global.language="zh" && global.zh_text_key_map!=(-1)){ '
    "if(ds_map_exists(global.zh_text_key_map,txt))ds_map_replace(global.zh_text_key_map,txt,global.zh_text_last_key); "
    "else ds_map_add(global.zh_text_key_map,txt,global.zh_text_last_key); "
    "} "
    "return(txt); "
)

AJUSTAR_TEXTO_SOURCE = (
    'var info, ancho, i, cont, pos_last_space, pos_salto, cut, fin, substring, key; info=argument0+" ";ancho=argument1;  fin=0; '
    "while(fin=false){ "
    "pos_last_space=0; "
    "fin=true; "
    "for(i=0;i<=ex(9827,info);i+=1){ "
    'if(string_char_at(info,i)=" "){ '
    "if(string_width(string_copy(info,pos_last_space,i-pos_last_space))>ancho){ "
    "fin=false; "
    "cut=pos_last_space+floor((i-pos_last_space)/2); "
    'info=string_copy(info,1,cut)+" "+string_copy(info,cut+1,ex(9827,info)-cut+1); '
    "i=1000000; "
    "} "
    "pos_last_space=i; "
    "} "
    "} "
    "} "
    'cont=0;pos_last_space=0;pos_salto=0;substring=""; draw_set_font(argument2); '
    "for(i=0;i<=ex(9827,info);i+=1){ "
    'if(string_char_at(info,i)=" "){ '
    "if(string_width(string_copy(info,pos_salto,i-pos_salto))>ancho){ "
    'info=string_copy(info,0,pos_last_space) + "#" + string_copy(info,pos_last_space+1,ex(9827,info)-pos_last_space+1); '
    'info=string_replace_all(info,"# ","#"); '
    "pos_salto=pos_last_space; "
    "i=pos_last_space; "
    "cont+=1; "
    "} "
    "else { "
    "pos_last_space=i; "
    "} "
    "} "
    "} "
    'if(!variable_global_exists("zh_text_key_map"))global.zh_text_key_map=(-1); '
    'if(global.language="zh" && global.zh_text_key_map!=(-1) && ds_map_exists(global.zh_text_key_map,argument0)){ '
    "key=ds_map_find_value(global.zh_text_key_map,argument0); "
    "if(ds_map_exists(global.zh_text_key_map,info))ds_map_replace(global.zh_text_key_map,info,key); "
    "else ds_map_add(global.zh_text_key_map,info,key); "
    "} "
    "return info; "
)

TEXT_PAR1_SOURCE = (
    'var texto, parametro1, textofinal, key, parametro1key; texto=argument0; parametro1=argument1; textofinal=string_replace_all(texto,"$par1$",parametro1); '
    'if(!variable_global_exists("zh_text_key_map"))global.zh_text_key_map=(-1); '
    'if(!variable_global_exists("zh_text_last_key"))global.zh_text_last_key=""; '
    'if(global.language="zh" && global.zh_text_key_map!=(-1)){ '
    'key=global.zh_text_last_key; parametro1key=""; if(ds_map_exists(global.zh_text_key_map,texto))key=ds_map_find_value(global.zh_text_key_map,texto); if(ds_map_exists(global.zh_text_key_map,parametro1))parametro1key=ds_map_find_value(global.zh_text_key_map,parametro1); '
    'if(key="zh__txt_dialog__5")key=key+"__slot__"+parametro1; '
    'else if(parametro1key!="")key=key+"__par1__"+parametro1key; '
    'else key=key+"__par1raw__"+parametro1; '
    "if(ds_map_exists(global.zh_text_key_map,textofinal))ds_map_replace(global.zh_text_key_map,textofinal,key); "
    "else ds_map_add(global.zh_text_key_map,textofinal,key); "
    "} "
    "return textofinal;  "
)

DEX_ESPECIE_SOURCE = (
    'var PK, infoFinal; PK=ex(7621,argument0); if(PK=0 || PK>(945))PK=ex(7622,argument0); '
    'if(PK=0)return("???"); '
    'infoFinal=ex(9942,"dex_espec",PK); '
    'if(infoFinal="???" || infoFinal="")return("???"); '
    "return(infoFinal); "
)

DEX_INFO_SOURCE = (
    'var PK, infoFinal; PK=ex(7621,argument0); if(PK=0 || PK>(945))PK=ex(7622,argument0); '
    "if(PK=0)return(ex(9928,272)); "
    'infoFinal=ex(9942,"dex_info",PK); '
    'if(infoFinal="???" || infoFinal="")return(ex(9928,272)); '
    "return(ex(5229,infoFinal,288,(4))); "
)

DRAW_BUTTON_DETAIL_POKEDEX_SOURCE = (
    "if(!instance_exists((90)))exit; var i, col1, col2, col3, col4, col5, col6; "
    "col1=c_black;col2=c_black;col3=c_black;col4=c_black;col5=c_black;col6=c_black; "
    "if((90).VIEW=3)draw_sprite((375),4,x,y); else if((90).VIEW=4)draw_sprite((375),3,x,y); else draw_sprite((375),(90).VIEW,x,y); "
    "draw_set_font((18)); draw_set_halign(fa_left); "
    "if((90).MENU_SEL=0)col1=c_white; if((90).MENU_SEL=1)col2=c_white; if((90).MENU_SEL=2)col3=c_white; if((90).MENU_SEL=3)col4=c_white; if((90).MENU_SEL=4)col5=c_white; if((90).MENU_SEL=13)col6=c_white; "
    "ex(7028,txt_op1,x+3,y+1,col1,fa_left,1); ex(7028,txt_op2,x+48,y+1,col2,fa_left,1); ex(7028,txt_op3,x+93,y+1,col3,fa_left,1); "
    "ex(7028,txt_op4,x+138,y+1,col4,fa_left,1); ex(7028,txt_op5,x+183,y+1,col5,fa_left,1); ex(7028,txt_op6,x+228,y+1,col6,fa_left,1); "
)

DRAW_CARTEL_DIRECTO_SOURCE = (
    "if(global.wait!=false)exit; if(global.hideCartelD)exit; if(instance_exists((447)))exit; if(instance_exists((327)))exit; "
    "if(canshow=true){ draw_set_font((2)); draw_set_halign(fa_left); draw_sprite((98),global.cuadrodialogo,view_xview,view_yview); "
    "ex(7028,spr,view_xview+15,view_yview+142,global.colordialogo,fa_left,1);} "
)

TEXT_PAR2_SOURCE = (
    'var texto, parametro1, parametro2, textofinal, parametro1key, parametro2key, key, basekey; texto=argument0; parametro1=argument1; parametro2=argument2; '
    'textofinal=string_replace_all(texto,"$par1$",parametro1); textofinal=string_replace_all(textofinal,"$par2$",parametro2); '
    'if(!variable_global_exists("zh_text_key_map"))global.zh_text_key_map=(-1); '
    'if(!variable_global_exists("zh_text_last_key"))global.zh_text_last_key=""; '
    'if(!variable_global_exists("zh_text_page3_suffix"))global.zh_text_page3_suffix=""; '
    'if(!variable_global_exists("zh_text_page4_suffix"))global.zh_text_page4_suffix=""; '
    'global.zh_text_page3_suffix=""; global.zh_text_page4_suffix=""; '
    'if(global.language="zh" && global.zh_text_key_map!=(-1)){ '
    'basekey=global.zh_text_last_key; key=""; parametro1key=""; parametro2key=""; '
    'if(ds_map_exists(global.zh_text_key_map,texto))basekey=ds_map_find_value(global.zh_text_key_map,texto); '
    'if(ds_map_exists(global.zh_text_key_map,parametro1))parametro1key=ds_map_find_value(global.zh_text_key_map,parametro1); '
    'if(ds_map_exists(global.zh_text_key_map,parametro2))parametro2key=ds_map_find_value(global.zh_text_key_map,parametro2); '
    'if(parametro1key!="")global.zh_text_page3_suffix="__par1__"+parametro1key; '
    'else global.zh_text_page3_suffix="__par1raw__"+parametro1; '
    'if(parametro2key!="")global.zh_text_page4_suffix="__par2__"+parametro2key; '
    'else global.zh_text_page4_suffix="__par2raw__"+parametro2; '
    'key=basekey; '
    'if(parametro1key!="")key+="__par1__"+parametro1key; else key+="__par1raw__"+parametro1; '
    'if(parametro2key!="")key+="__par2__"+parametro2key; else key+="__par2raw__"+parametro2; '
    "if(ds_map_exists(global.zh_text_key_map,textofinal))ds_map_replace(global.zh_text_key_map,textofinal,key); "
    "else ds_map_add(global.zh_text_key_map,textofinal,key); "
    "} "
    "return(textofinal);  "
)

TEXT_PAR3_SOURCE = (
    'var texto, parametro1, parametro2, parametro3, textofinal, parametro1key, parametro2key, parametro3key, key, basekey; texto=argument0; parametro1=argument1; parametro2=argument2; parametro3=argument3; '
    'textofinal=string_replace_all(texto,"$par1$",parametro1); textofinal=string_replace_all(textofinal,"$par2$",parametro2); '
    'textofinal=string_replace_all(textofinal,"$par3$",parametro3); '
    'if(!variable_global_exists("zh_text_key_map"))global.zh_text_key_map=(-1); '
    'if(!variable_global_exists("zh_text_last_key"))global.zh_text_last_key=""; '
    'if(global.language="zh" && global.zh_text_key_map!=(-1)){ '
    'basekey=global.zh_text_last_key; key=""; parametro1key=""; parametro2key=""; parametro3key=""; '
    'if(ds_map_exists(global.zh_text_key_map,texto))basekey=ds_map_find_value(global.zh_text_key_map,texto); '
    'if(ds_map_exists(global.zh_text_key_map,parametro1))parametro1key=ds_map_find_value(global.zh_text_key_map,parametro1); '
    'if(ds_map_exists(global.zh_text_key_map,parametro2))parametro2key=ds_map_find_value(global.zh_text_key_map,parametro2); '
    'if(ds_map_exists(global.zh_text_key_map,parametro3))parametro3key=ds_map_find_value(global.zh_text_key_map,parametro3); '
    'key=basekey; '
    'if(parametro1key!="")key+="__par1__"+parametro1key; else key+="__par1raw__"+parametro1; '
    'if(parametro2key!="")key+="__par2__"+parametro2key; else key+="__par2raw__"+parametro2; '
    'if(parametro3key!="")key+="__par3__"+parametro3key; else key+="__par3raw__"+parametro3; '
    "if(ds_map_exists(global.zh_text_key_map,textofinal))ds_map_replace(global.zh_text_key_map,textofinal,key); "
    "else ds_map_add(global.zh_text_key_map,textofinal,key); "
    "} "
    "return(textofinal);  "
)

DIALOGO_MULTIPLE_SOURCE = (
    'var remaining, page, text_page, key, pos, map_pages, base_key; remaining=argument0; page=1; map_pages=false; base_key=""; '
    'if(!variable_global_exists("zh_text_key_map"))global.zh_text_key_map=(-1); '
    'if(!variable_global_exists("zh_text_last_key"))global.zh_text_last_key=""; '
    'if(global.language="zh" && global.zh_text_key_map!=(-1) && ds_map_exists(global.zh_text_key_map,argument0)){ map_pages=true; base_key=ds_map_find_value(global.zh_text_key_map,argument0); } '
    "while(true){ "
    "pos=string_pos(\"@\",remaining); "
    "if(pos>0){ text_page=string_copy(remaining,1,pos-1); remaining=string_delete(remaining,1,pos); } "
    'else { text_page=remaining; remaining=""; } '
    "if(map_pages){ "
    'key=base_key+"__page__"+string(page); '
    'if(base_key="zh__txt_dialog__6841"){ '
    'if(page=3 && variable_global_exists("zh_text_page3_suffix") && global.zh_text_page3_suffix!="")key+=global.zh_text_page3_suffix; '
    'else if(page=4 && variable_global_exists("zh_text_page4_suffix") && global.zh_text_page4_suffix!="")key+=global.zh_text_page4_suffix; '
    '} '
    "if(ds_map_exists(global.zh_text_key_map,text_page))ds_map_replace(global.zh_text_key_map,text_page,key); "
    "else ds_map_add(global.zh_text_key_map,text_page,key); "
    "} "
    "ex(6834,text_page,argument1,argument2); "
    'if(remaining="")exit; '
    "page+=1; "
    "} "
)

DIALOGO_SIMPLE_MULTIPLE_SOURCE = (
    'var remaining, page, text_page, key, pos, map_pages, base_key; remaining=argument0; page=1; map_pages=false; base_key=""; '
    'if(!variable_global_exists("zh_text_key_map"))global.zh_text_key_map=(-1); '
    'if(!variable_global_exists("zh_text_last_key"))global.zh_text_last_key=""; '
    'if(global.language="zh" && global.zh_text_key_map!=(-1) && ds_map_exists(global.zh_text_key_map,argument0)){ map_pages=true; base_key=ds_map_find_value(global.zh_text_key_map,argument0); } '
    "while(true){ "
    "pos=string_pos(\"@\",remaining); "
    "if(pos>0){ text_page=string_copy(remaining,1,pos-1); remaining=string_delete(remaining,1,pos); } "
    'else { text_page=remaining; remaining=""; } '
    "if(map_pages){ "
    'key=base_key+"__page__"+string(page); '
    'if(base_key="zh__txt_dialog__6841"){ '
    'if(page=3 && variable_global_exists("zh_text_page3_suffix") && global.zh_text_page3_suffix!="")key+=global.zh_text_page3_suffix; '
    'else if(page=4 && variable_global_exists("zh_text_page4_suffix") && global.zh_text_page4_suffix!="")key+=global.zh_text_page4_suffix; '
    '} '
    "if(ds_map_exists(global.zh_text_key_map,text_page))ds_map_replace(global.zh_text_key_map,text_page,key); "
    "else ds_map_add(global.zh_text_key_map,text_page,key); "
    "} "
    "ex(6846,text_page); "
    'if(remaining="")exit; '
    "page+=1; "
    "} "
)

DRAW_INICIO_CONTROL_SOURCE = (
    "draw_set_font((0)); draw_set_halign(fa_center);  "
    'if(!variable_global_exists("zh_menu_0"))global.zh_menu_0=(-1); if(!variable_global_exists("zh_menu_1"))global.zh_menu_1=(-1); if(!variable_global_exists("zh_menu_2"))global.zh_menu_2=(-1); if(!variable_global_exists("zh_menu_3"))global.zh_menu_3=(-1); if(!variable_global_exists("zh_menu_4"))global.zh_menu_4=(-1); '
    "var max_sel; if(global.cheat_enabled=1)max_sel=5; else max_sel=4; "
    "col1=c_white;col2=c_white;col3=c_white;col4=c_white;col5=c_white;col6=c_white; "
    "if(SEL=0){col1=(16744448);} "
    "if(SEL=1){col2=(52235);} "
    "if(SEL=2){col3=(16742844);} "
    "if(SEL=3){col4=(49151);} "
    "if(SEL=4 && max_sel=4){col5=c_red;} "
    "if(SEL=4 && max_sel=5){col5=(65535);} "
    "if(SEL=5){col6=c_red;}  "
    'if(global.language="zh" && global.zh_menu_0=(-1)){ global.zh_menu_0=sprite_add(working_directory+"\\\\data\\\\text\\\\zh\\\\menu_zh_parts\\\\menu_0.png",0,0,0,64,10); global.zh_menu_1=sprite_add(working_directory+"\\\\data\\\\text\\\\zh\\\\menu_zh_parts\\\\menu_1.png",0,0,0,64,10); global.zh_menu_2=sprite_add(working_directory+"\\\\data\\\\text\\\\zh\\\\menu_zh_parts\\\\menu_2.png",0,0,0,64,10); global.zh_menu_3=sprite_add(working_directory+"\\\\data\\\\text\\\\zh\\\\menu_zh_parts\\\\menu_3.png",0,0,0,64,10); global.zh_menu_4=sprite_add(working_directory+"\\\\data\\\\text\\\\zh\\\\menu_zh_parts\\\\menu_4.png",0,0,0,64,10); } '
    'if(global.language="zh" && sprite_exists(global.zh_menu_0) && sprite_exists(global.zh_menu_1) && sprite_exists(global.zh_menu_2) && sprite_exists(global.zh_menu_3) && sprite_exists(global.zh_menu_4)){ '
    "draw_set_halign(fa_center); "
    "draw_sprite_ext(global.zh_menu_0,0,160,74,1,1,0,col1,1); if(SEL=0)draw_sprite_ext(global.zh_menu_0,0,160-1+random(2),74-1+random(2),1,1,0,col1,0.3); "
    "draw_sprite_ext(global.zh_menu_1,0,160,92,1,1,0,col2,1); if(SEL=1)draw_sprite_ext(global.zh_menu_1,0,160-1+random(2),92-1+random(2),1,1,0,col2,0.3); "
    "draw_sprite_ext(global.zh_menu_2,0,160,110,1,1,0,col3,1); if(SEL=2)draw_sprite_ext(global.zh_menu_2,0,160-1+random(2),110-1+random(2),1,1,0,col3,0.3); "
    "draw_sprite_ext(global.zh_menu_3,0,160,128,1,1,0,col4,1); if(SEL=3)draw_sprite_ext(global.zh_menu_3,0,160-1+random(2),128-1+random(2),1,1,0,col4,0.3); "
    "draw_sprite_ext(global.zh_menu_4,0,160,146,1,1,0,col5,1); if(SEL=4)draw_sprite_ext(global.zh_menu_4,0,160-1+random(2),146-1+random(2),1,1,0,col5,0.3); "
    "if(max_sel=5){ draw_text_color(160,164,text_op6,col6,col6,col6,col6,1); if(SEL=5)draw_text_color(160-1+random(2),164-1+random(2),text_op6,col6,col6,col6,col6,0.3);} "
    "draw_set_halign(fa_left); if(global.drawPriorModalSystem!=(-1)){ ex(7120); exit;} if(global.drawModalSystem!=(-1)){ ex(7076); exit;} exit;} "
    "draw_text_color(160,74,text_op1,col1,col1,col1,col1,1); if(SEL=0)draw_text_color(160-1+random(2),74-1+random(2),text_op1,col1,col1,col1,col1,0.3); "
    "draw_text_color(160,92,text_op2,col2,col2,col2,col2,1); if(SEL=1)draw_text_color(160-1+random(2),92-1+random(2),text_op2,col2,col2,col2,col2,0.3); "
    "draw_text_color(160,110,text_op3,col3,col3,col3,col3,1); if(SEL=2)draw_text_color(160-1+random(2),110-1+random(2),text_op3,col3,col3,col3,col3,0.3); "
    "draw_text_color(160,128,text_op4,col4,col4,col4,col4,1); if(SEL=3)draw_text_color(160-1+random(2),128-1+random(2),text_op4,col4,col4,col4,col4,0.3); "
    "draw_text_color(160,146,text_op5,col5,col5,col5,col5,1); if(SEL=4)draw_text_color(160-1+random(2),146-1+random(2),text_op5,col5,col5,col5,col5,0.3); "
    "if(max_sel=5){ draw_text_color(160,164,text_op6,col6,col6,col6,col6,1); if(SEL=5)draw_text_color(160-1+random(2),164-1+random(2),text_op6,col6,col6,col6,col6,0.3);} "
    "draw_set_halign(fa_left); if(global.drawPriorModalSystem!=(-1)){ ex(7120); exit;} if(global.drawModalSystem!=(-1)){ ex(7076); exit;} "
)

ADD_TEXT_TO_BUFFER_SOURCE = (
    'if(!instance_exists((6)))exit; if(global.showbattleevents=false)exit; if(argument0="")exit; '
    'if(!variable_global_exists("zh_text_key_map"))global.zh_text_key_map=(-1); '
    'if(global.language="zh"){ '
    'if(global.zh_text_key_map=(-1))global.zh_text_key_map=ds_map_create(); '
    'if(!ds_map_exists(global.zh_text_key_map,argument0)){ '
    'var dash_pos, part1, part2, key1, key2, pair_key; dash_pos=string_pos(" - ",argument0); '
    'if(dash_pos>0){ part1=string_copy(argument0,1,dash_pos-1); part2=string_delete(argument0,1,dash_pos+2); '
    'if(part1!="" && part2!=""){ key1=""; key2=""; '
    'if(ds_map_exists(global.zh_text_key_map,part1))key1=ds_map_find_value(global.zh_text_key_map,part1); '
    'if(ds_map_exists(global.zh_text_key_map,part2))key2=ds_map_find_value(global.zh_text_key_map,part2); '
    'pair_key="zh__custom__pair_dash"; '
    'if(key1!="")pair_key+="__par1__"+key1; else pair_key+="__par1raw__"+part1; '
    'if(key2!="")pair_key+="__par2__"+key2; else pair_key+="__par2raw__"+part2; '
    'if(ds_map_exists(global.zh_text_key_map,argument0))ds_map_replace(global.zh_text_key_map,argument0,pair_key); '
    'else ds_map_add(global.zh_text_key_map,argument0,pair_key); }}}} '
    'var i, f; for(i=0;i<=(6).TAM_BUFFER;i+=1){ if((6).buffer[i]=""){ (6).buffer[i]=argument0;i=((6).TAM_BUFFER+1); '
    'if(global.saveLogBattle){ f=file_text_open_append("LogBattle.txt"); file_text_write_string(f,argument0);file_text_writeln(f); file_text_close(f);} exit;}} '
)

DRAW_PANEL_INFORMATIVO_SOURCE = (
    "draw_set_font((0)); draw_set_halign(fa_left); draw_set_color(0); "
    "if(global.showbattleevents=false)exit; if(instance_exists((1679))){if((1679).PISO=38)exit;} "
    "draw_set_halign(fa_left); draw_set_alpha(ALPHA-0.25); draw_rectangle_color(69,279,507,316,c_black,c_black,c_black,c_black,false); draw_set_alpha(ALPHA); "
    "if(movimiento!=false){ "
    "ex(7028,buffer[0],80,268+movimiento,(13160656),fa_left,ALPHA*movimiento/16); "
    "ex(7028,spr1,80,282+movimiento,(13160656),fa_left,ALPHA); "
    "ex(7028,spr2,80,298+movimiento,(13160656),fa_left,ALPHA-(ALPHA*movimiento/16)); "
    "} else{ "
    "ex(7028,spr1,80,282,(13160656),fa_left,ALPHA); "
    "ex(7028,spr2,80,298,(13160656),fa_left,ALPHA); "
    "} draw_set_alpha(1); "
)

STARTUP_VALIDATION_BYPASS_SOURCE = "return 1; "
SAVE_ISOLATION_OLD_PREFIX = r"data\partidas\reloaded"
SAVE_ISOLATION_NEW_PREFIX = r"data\partidas\reloaded_zhcn_"
SAVE_ISOLATION_SCRIPT_IDS = (
    7477,
    7657,
    7680,
    7759,
    7981,
    7993,
    8008,
    8243,
    8613,
    9200,
    9201,
    9440,
    9624,
    9777,
    9779,
)


def _replace(raw: bytes, script_index: int, old: str, new: str) -> bytes:
    try:
        return patch_script_source_replace(raw, script_index, old, new)
    except ValueError:
        return raw


def _replace_all(raw: bytes, script_index: int, old: str, new: str) -> bytes:
    patched = raw
    while True:
        updated = _replace(patched, script_index, old, new)
        if updated == patched:
            return patched
        patched = updated


def patch_dialog_bitmap_runtime(raw: bytes) -> bytes:
    patched = raw

    patched = _replace(
        patched,
        7879,
        'global.language=LAN_FOLDER[SEL_LAN]; if(global.language="en")global.sistema_medida=1;else global.sistema_medida=0; IMAGE_FLAG=sprite_add(working_directory+"\\data\\text\\"+global.language+"\\_flag.png",-1,0,0,0,0);',
        'global.language=LAN_FOLDER[SEL_LAN]; global.zh_text_key_map=(-1);global.zh_sprite_cache=(-1);global.zh_text_last_key=""; if(global.language="en")global.sistema_medida=1;else global.sistema_medida=0; IMAGE_FLAG=sprite_add(working_directory+"\\\\data\\\\text\\\\"+global.language+"\\\\_flag.png",-1,0,0,0,0); global.zh_menu_0=(-1);global.zh_menu_1=(-1);global.zh_menu_2=(-1);global.zh_menu_3=(-1);global.zh_menu_4=(-1); if(global.language="zh"){ global.zh_menu_0=sprite_add(working_directory+"\\\\data\\\\text\\\\zh\\\\menu_zh_parts\\\\menu_0.png",0,0,0,64,10); global.zh_menu_1=sprite_add(working_directory+"\\\\data\\\\text\\\\zh\\\\menu_zh_parts\\\\menu_1.png",0,0,0,64,10); global.zh_menu_2=sprite_add(working_directory+"\\\\data\\\\text\\\\zh\\\\menu_zh_parts\\\\menu_2.png",0,0,0,64,10); global.zh_menu_3=sprite_add(working_directory+"\\\\data\\\\text\\\\zh\\\\menu_zh_parts\\\\menu_3.png",0,0,0,64,10); global.zh_menu_4=sprite_add(working_directory+"\\\\data\\\\text\\\\zh\\\\menu_zh_parts\\\\menu_4.png",0,0,0,64,10); }',
    )
    patched = patch_script_source(patched, 7038, DRAW_INICIO_CONTROL_SOURCE)
    patched = patch_script_source(patched, 7028, DRAW_GRAFITI_EXT_SOURCE)
    patched = patch_script_source(patched, 6901, DRAW_TEXT_SHADOW_SOURCE)
    patched = patch_script_source(patched, 5211, ADD_TEXT_TO_BUFFER_SOURCE)
    patched = patch_script_source(patched, 7089, DRAW_PANEL_INFORMATIVO_SOURCE)
    patched = patch_script_source(
        patched,
        6983,
        "draw_set_font((2)); draw_set_halign(fa_left); draw_sprite_ext(sprite_index,image_index,x,y,image_xscale,image_yscale,image_angle,image_blend,image_alpha); ex(7028,str,letraX,letraY,c_white,fa_left,1); ",
    )
    patched = patch_script_source(patched, 5229, AJUSTAR_TEXTO_SOURCE)
    patched = patch_script_source(patched, 9942, TEXT_READER_SOURCE)
    patched = patch_script_source(patched, 9923, TEXT_DIALOG_SOURCE)
    patched = patch_script_source(patched, 9928, TEXT_MENU_SOURCE)
    patched = patch_script_source(patched, 9919, TEXT_CARTEL_SOURCE)
    patched = patch_script_source(patched, 9935, TEXT_PAR1_SOURCE)
    patched = patch_script_source(patched, 9936, TEXT_PAR2_SOURCE)
    patched = patch_script_source(patched, 9937, TEXT_PAR3_SOURCE)
    patched = patch_script_source(patched, 6841, DIALOGO_MULTIPLE_SOURCE)
    patched = patch_script_source(patched, 6848, DIALOGO_SIMPLE_MULTIPLE_SOURCE)
    patched = patch_script_source(patched, 6814, DEX_ESPECIE_SOURCE)
    patched = patch_script_source(patched, 6819, DEX_INFO_SOURCE)
    patched = patch_script_source(patched, 6948, DRAW_BUTTON_DETAIL_POKEDEX_SOURCE)
    patched = patch_script_source(patched, 6956, DRAW_CARTEL_DIRECTO_SOURCE)
    patched = _replace(
        patched,
        6802,
        'if(c>=3){aux=-1;c=0; while(c<3){aux+=1; if(string_char_at(InfoDex,aux)=\'#\')c+=1;} InfoDex1=string_copy(InfoDex,0,aux); InfoDex2=string_copy(InfoDex,aux+1,ex(9827,InfoDex)-aux+1);} else{pag2=false; InfoDex1=InfoDex; InfoDex2="";}',
        'if(c>=3){aux=-1;c=0; while(c<3){aux+=1; if(string_char_at(InfoDex,aux)=\'#\')c+=1;} InfoDex1=string_copy(InfoDex,0,aux); InfoDex2=string_copy(InfoDex,aux+1,ex(9827,InfoDex)-aux+1);} else{pag2=false; InfoDex1=InfoDex; InfoDex2="";} if(global.language="zh" && global.zh_text_key_map!=(-1) && variable_global_exists("zh_text_last_key") && global.zh_text_last_key!=""){ if(InfoDex1!=""){ if(ds_map_exists(global.zh_text_key_map,InfoDex1))ds_map_replace(global.zh_text_key_map,InfoDex1,global.zh_text_last_key+"__page__1"); else ds_map_add(global.zh_text_key_map,InfoDex1,global.zh_text_last_key+"__page__1"); } if(InfoDex2!=""){ if(ds_map_exists(global.zh_text_key_map,InfoDex2))ds_map_replace(global.zh_text_key_map,InfoDex2,global.zh_text_last_key+"__page__2"); else ds_map_add(global.zh_text_key_map,InfoDex2,global.zh_text_last_key+"__page__2"); }}',
    )

    patched = _replace(
        patched,
        5641,
        "var f, i, txt, txtFinal;",
        'var f, i, j, txt, txtFinal; if(!variable_global_exists("zh_text_key_map"))global.zh_text_key_map=(-1);',
    )
    patched = _replace(
        patched,
        5641,
        "global.STR_LUG[i]=ex(9802,txtFinal);",
        'global.STR_LUG[i]=ex(9802,txtFinal); if(global.language="zh"){ if(global.zh_text_key_map=(-1))global.zh_text_key_map=ds_map_create(); if(ds_map_exists(global.zh_text_key_map,global.STR_LUG[i]))ds_map_replace(global.zh_text_key_map,global.STR_LUG[i],"zh__txt_map__"+string(i)); else ds_map_add(global.zh_text_key_map,global.STR_LUG[i],"zh__txt_map__"+string(i)); }',
    )
    patched = _replace(
        patched,
        5641,
        "global.STR_POK[i]=ex(9802,txtFinal);",
        'global.STR_POK[i]=ex(9802,txtFinal); if(global.language="zh"){ if(global.zh_text_key_map=(-1))global.zh_text_key_map=ds_map_create(); if(ds_map_exists(global.zh_text_key_map,global.STR_POK[i]))ds_map_replace(global.zh_text_key_map,global.STR_POK[i],"zh__txt_pkmn__"+string(i)); else ds_map_add(global.zh_text_key_map,global.STR_POK[i],"zh__txt_pkmn__"+string(i)); }',
    )
    patched = _replace(
        patched,
        5641,
        "global.STR_ATK[i]=ex(9802,txtFinal);",
        'global.STR_ATK[i]=ex(9802,txtFinal); if(global.language="zh"){ if(global.zh_text_key_map=(-1))global.zh_text_key_map=ds_map_create(); if(ds_map_exists(global.zh_text_key_map,global.STR_ATK[i]))ds_map_replace(global.zh_text_key_map,global.STR_ATK[i],"zh__txt_attack__"+string(i)); else ds_map_add(global.zh_text_key_map,global.STR_ATK[i],"zh__txt_attack__"+string(i)); }',
    )
    patched = _replace(
        patched,
        5641,
        "global.STR_OBJ[i]=ex(9802,txtFinal);",
        'global.STR_OBJ[i]=ex(9802,txtFinal); if(global.language="zh"){ if(global.zh_text_key_map=(-1))global.zh_text_key_map=ds_map_create(); if(ds_map_exists(global.zh_text_key_map,global.STR_OBJ[i]))ds_map_replace(global.zh_text_key_map,global.STR_OBJ[i],"zh__txt_obj__"+string(i)); else ds_map_add(global.zh_text_key_map,global.STR_OBJ[i],"zh__txt_obj__"+string(i)); }',
    )
    patched = _replace(
        patched,
        5641,
        "global.STR_OBJ_BASE[i]=ex(9802,txtFinal);",
        'global.STR_OBJ_BASE[i]=ex(9802,txtFinal); if(global.language="zh"){ if(global.zh_text_key_map=(-1))global.zh_text_key_map=ds_map_create(); if(ds_map_exists(global.zh_text_key_map,global.STR_OBJ_BASE[i]))ds_map_replace(global.zh_text_key_map,global.STR_OBJ_BASE[i],"zh__txt_obj_secret_base__"+string(i)); else ds_map_add(global.zh_text_key_map,global.STR_OBJ_BASE[i],"zh__txt_obj_secret_base__"+string(i)); }',
    )
    patched = _replace(
        patched,
        5641,
        "global.STR_HAB[i]=ex(9802,txtFinal);",
        'global.STR_HAB[i]=ex(9802,txtFinal); if(global.language="zh"){ if(global.zh_text_key_map=(-1))global.zh_text_key_map=ds_map_create(); if(ds_map_exists(global.zh_text_key_map,global.STR_HAB[i]))ds_map_replace(global.zh_text_key_map,global.STR_HAB[i],"zh__txt_abilities__"+string(i)); else ds_map_add(global.zh_text_key_map,global.STR_HAB[i],"zh__txt_abilities__"+string(i)); }',
    )
    patched = _replace(
        patched,
        5641,
        "global.STR_BAT[i]=ex(9802,txtFinal);",
        'global.STR_BAT[i]=ex(9802,txtFinal); if(global.language="zh"){ if(global.zh_text_key_map=(-1))global.zh_text_key_map=ds_map_create(); if(ds_map_exists(global.zh_text_key_map,global.STR_BAT[i]))ds_map_replace(global.zh_text_key_map,global.STR_BAT[i],"zh__txt_battle__"+string(i)); else ds_map_add(global.zh_text_key_map,global.STR_BAT[i],"zh__txt_battle__"+string(i)); }',
    )
    patched = _replace(
        patched,
        6442,
        'txt_asignaBall=string_replace(ex(9928,1178),"$t1$",ex(8492,(3).key_obj_asignarBall));',
        'txt_asignaBall=string_replace(ex(9928,1178),"$t1$",ex(8492,(3).key_obj_asignarBall)); if(global.language="zh" && global.zh_text_key_map!=(-1)){ var keyBall, keyBallBase; keyBall=ex(8492,(3).key_obj_asignarBall); if(ds_map_exists(global.zh_text_key_map,keyBall))keyBallBase="zh__txt_menu__1178__par2__"+ds_map_find_value(global.zh_text_key_map,keyBall); else keyBallBase="zh__txt_menu__1178__par2raw__"+keyBall; if(ds_map_exists(global.zh_text_key_map,txt_asignaBall))ds_map_replace(global.zh_text_key_map,txt_asignaBall,keyBallBase); else ds_map_add(global.zh_text_key_map,txt_asignaBall,keyBallBase); }',
    )

    patched = _replace(
        patched,
        6834,
        "ANCHO=290; if(string_width(argument0)>ANCHO){",
        'ANCHO=290; if(global.language!="zh" && string_width(argument0)>ANCHO){',
    )
    patched = _replace(
        patched,
        6834,
        "for(i=1;i<=string_length(argument0);i+=1){ global.drawModalText=string_copy(argument0,1,i); ex(9774,global.vel_text); }",
        'if(global.language="zh"){ global.drawModalText=argument0; ex(9774,global.vel_text); } else for(i=1;i<=string_length(argument0);i+=1){ global.drawModalText=string_copy(argument0,1,i); ex(9774,global.vel_text); }',
    )
    patched = _replace(
        patched,
        6846,
        "ANCHO=290;  if(string_width(argument0)>ANCHO){",
        'ANCHO=290;  if(global.language!="zh" && string_width(argument0)>ANCHO){',
    )
    patched = _replace(
        patched,
        6846,
        "for(i=1;i<=string_length(argument0);i+=1){ global.drawModalText=string_copy(argument0,1,i); ex(9774,global.vel_text); }",
        'if(global.language="zh"){ global.drawModalText=argument0; ex(9774,global.vel_text); } else for(i=1;i<=string_length(argument0);i+=1){ global.drawModalText=string_copy(argument0,1,i); ex(9774,global.vel_text); }',
    )
    patched = _replace(
        patched,
        6835,
        "if(global.snd_SE=(1))sound_play((4)); for(i=1;i<=ex(9827,argument0);i+=1){ global.drawModalText=string_copy(argument0,1,i); ex(9774,global.vel_text);} ",
        'if(global.snd_SE=(1))sound_play((4)); if(global.language="zh"){ global.drawModalText=argument0; ex(9774,global.vel_text);} else for(i=1;i<=ex(9827,argument0);i+=1){ global.drawModalText=string_copy(argument0,1,i); ex(9774,global.vel_text);} ',
    )
    patched = _replace(
        patched,
        6847,
        "if(string_char_at(argument0,0)=' ')argument0=string_replace(argument0,' ',\"\"); if(global.snd_SE=(1))sound_play((4)); for(i=1;i<=ex(9827,argument0);i+=1){ global.drawModalText=string_copy(argument0,1,i); ex(9774,global.vel_text); }",
        'if(string_char_at(argument0,0)=\' \')argument0=string_replace(argument0,\' \',""); if(global.snd_SE=(1))sound_play((4)); if(global.language="zh"){ global.drawModalText=argument0; ex(9774,global.vel_text); } else for(i=1;i<=ex(9827,argument0);i+=1){ global.drawModalText=string_copy(argument0,1,i); ex(9774,global.vel_text); }',
    )
    patched = _replace(
        patched,
        7578,
        "var text, i, Col, sale, offX, offY;",
        "var text, i, Col, sale, offX, offY, key;",
    )
    patched = _replace(
        patched,
        7578,
        "text=ex(5229,argument[0],290,(2)); offX=(view_wview/2)-120; offY=ex(7818,ex(7939),99,0);  global.drawModalParam=argument[1];",
        'text=ex(5229,argument[0],290,(2)); if(!variable_global_exists("zh_text_key_map"))global.zh_text_key_map=(-1); if(global.language="zh" && global.zh_text_key_map!=(-1) && ds_map_exists(global.zh_text_key_map,argument[0])){ key=ds_map_find_value(global.zh_text_key_map,argument[0]); if(ds_map_exists(global.zh_text_key_map,text))ds_map_replace(global.zh_text_key_map,text,key); else ds_map_add(global.zh_text_key_map,text,key);} offX=(view_wview/2)-120; offY=ex(7818,ex(7939),99,0);  global.drawModalParam=argument[1];',
    )
    patched = _replace(
        patched,
        7578,
        "if(global.snd_SE=(1))sound_play((4)); for(i=1;i<=ex(9827,text);i+=1){ global.drawModalText=string_copy(text,1,i); ex(9774,1); if(global.selectionTextNoSleep=false)ex(9774,global.vel_text);} global.drawModalMayus=true;screen_redraw();",
        'if(global.snd_SE=(1))sound_play((4)); if(global.language="zh"){ global.drawModalText=text; ex(9774,1); } else for(i=1;i<=ex(9827,text);i+=1){ global.drawModalText=string_copy(text,1,i); ex(9774,1); if(global.selectionTextNoSleep=false)ex(9774,global.vel_text);} global.drawModalMayus=true;screen_redraw();',
    )
    patched = _replace(
        patched,
        7666,
        "var i, text, sale, offX, offY;",
        "var i, text, sale, offX, offY, key;",
    )
    patched = _replace(
        patched,
        7666,
        "text=ex(5229,argument[0],290,(2)); offX=ex(7818,ex(7939),88,40); offY=ex(7818,ex(7939),99,0);  global.drawModalSel=1; global.drawModalParam=argument[1];",
        'text=ex(5229,argument[0],290,(2)); if(!variable_global_exists("zh_text_key_map"))global.zh_text_key_map=(-1); if(global.language="zh" && global.zh_text_key_map!=(-1) && ds_map_exists(global.zh_text_key_map,argument[0])){ key=ds_map_find_value(global.zh_text_key_map,argument[0]); if(ds_map_exists(global.zh_text_key_map,text))ds_map_replace(global.zh_text_key_map,text,key); else ds_map_add(global.zh_text_key_map,text,key);} offX=ex(7818,ex(7939),88,40); offY=ex(7818,ex(7939),99,0);  global.drawModalSel=1; global.drawModalParam=argument[1];',
    )
    patched = _replace(
        patched,
        7666,
        "if(global.snd_SE=(1))sound_play((4)); for(i=1;i<=ex(9827,text);i+=1){ global.drawModalText=string_copy(text,1,i); ex(9774,1); if(global.selectionTextNoSleep=false)ex(9774,global.vel_text);} global.drawModalMayus=true;screen_redraw();",
        'if(global.snd_SE=(1))sound_play((4)); if(global.language="zh"){ global.drawModalText=text; ex(9774,1); } else for(i=1;i<=ex(9827,text);i+=1){ global.drawModalText=string_copy(text,1,i); ex(9774,1); if(global.selectionTextNoSleep=false)ex(9774,global.vel_text);} global.drawModalMayus=true;screen_redraw();',
    )
    patched = _replace(
        patched,
        7672,
        "var i, sale, Col, offX, offY;",
        "var i, sale, Col, offX, offY, key;",
    )
    patched = _replace(
        patched,
        7672,
        "text=ex(5229,argument[0],290,(2)); offX=(view_wview/2)-120; offY=ex(7818,ex(7939),99,0);  if(global.hideCartelD)exit;",
        'text=ex(5229,argument[0],290,(2)); if(!variable_global_exists("zh_text_key_map"))global.zh_text_key_map=(-1); if(global.language="zh" && global.zh_text_key_map!=(-1) && ds_map_exists(global.zh_text_key_map,argument[0])){ key=ds_map_find_value(global.zh_text_key_map,argument[0]); if(ds_map_exists(global.zh_text_key_map,text))ds_map_replace(global.zh_text_key_map,text,key); else ds_map_add(global.zh_text_key_map,text,key);} offX=(view_wview/2)-120; offY=ex(7818,ex(7939),99,0);  if(global.hideCartelD)exit;',
    )
    patched = _replace(
        patched,
        7672,
        "if(global.snd_SE=(1))sound_play((4)); for(i=1;i<=ex(9827,argument[0]);i+=1){ global.drawModalText=string_copy(argument[0],1,i); ex(9774,1); if(global.selectionTextNoSleep=false)ex(9774,global.vel_text);} global.drawModalMenuText=ex(9928,60);screen_redraw();",
        'if(global.snd_SE=(1))sound_play((4)); if(global.language="zh"){ global.drawModalText=text; ex(9774,1); } else for(i=1;i<=ex(9827,argument[0]);i+=1){ global.drawModalText=string_copy(argument[0],1,i); ex(9774,1); if(global.selectionTextNoSleep=false)ex(9774,global.vel_text);} global.drawModalMenuText=ex(9928,60);screen_redraw();',
    )

    patched = _replace(
        patched,
        7076,
        "draw_text_color(view_xview+57,view_yview+118,global.drawModalMenuText, global.colorpersonaje,global.colorpersonaje, global.colorpersonaje,global.colorpersonaje,1); draw_text_color(view_xview+15,view_yview+142,global.drawModalText, global.colordialogo,global.colordialogo,global.colordialogo,global.colordialogo,1);",
        "ex(7028,global.drawModalMenuText,view_xview+57,view_yview+118,global.colorpersonaje,fa_left,1); ex(7028,global.drawModalText,view_xview+15,view_yview+142,global.colordialogo,fa_left,1);",
    )
    patched = _replace_all(
        patched,
        7076,
        "draw_text_color(view_xview+15,view_yview+142,global.drawModalText, global.colordialogo,global.colordialogo,global.colordialogo,global.colordialogo,1);",
        "ex(7028,global.drawModalText,view_xview+15,view_yview+142,global.colordialogo,fa_left,1);",
    )
    patched = _replace(
        patched,
        7076,
        "draw_text_color(view_xview+58,view_yview+21,global.drawModalText, global.drawModalParam,global.drawModalParam,global.drawModalParam,global.drawModalParam,1);",
        "ex(7028,global.drawModalText,view_xview+58,view_yview+21,global.drawModalParam,fa_left,1);",
    )
    patched = _replace_all(
        patched,
        7076,
        "draw_text_color(view_xview+15+offX-40,view_yview+142+offY,global.drawModalText, global.colordialogo,global.colordialogo,global.colordialogo,global.colordialogo,1);",
        "ex(7028,global.drawModalText,view_xview+15+offX-40,view_yview+142+offY,global.colordialogo,fa_left,1);",
    )
    patched = _replace_all(
        patched,
        7076,
        "ex(6901,view_xview+114+offX,view_yview+global.drawModalOffset+offY, global.optionSelection[i],Col,0,0);",
        "ex(7028,global.optionSelection[i],view_xview+114+offX,view_yview+global.drawModalOffset+offY,Col,fa_center,1);",
    )
    patched = _replace_all(
        patched,
        7076,
        "ex(6901,view_xview+122+offX,view_yview+global.drawModalOffset+offY, global.drawModalText,ex(5971,global.cuadrodialogo),0,0);",
        "ex(7028,global.drawModalText,view_xview+122+offX,view_yview+global.drawModalOffset+offY,ex(5971,global.cuadrodialogo),fa_center,1);",
    )
    patched = _replace_all(
        patched,
        7076,
        "ex(6901,view_xview+122+offX,view_yview+global.drawModalOffset+offY,global.drawModalText, ex(5971,global.cuadrodialogo),0,0);",
        "ex(7028,global.drawModalText,view_xview+122+offX,view_yview+global.drawModalOffset+offY,ex(5971,global.cuadrodialogo),fa_center,1);",
    )
    patched = _replace_all(
        patched,
        7076,
        "ex(6901,view_xview+120+offX,view_yview+107+offY,global.optionSelection[1],Col,0,0);",
        "ex(7028,global.optionSelection[1],view_xview+120+offX,view_yview+107+offY,Col,fa_center,1);",
    )
    patched = _replace_all(
        patched,
        7076,
        "ex(6901,view_xview+69+offX,view_yview+107+offY,global.optionSelection[1],Col,0,0);",
        "ex(7028,global.optionSelection[1],view_xview+69+offX,view_yview+107+offY,Col,fa_center,1);",
    )
    patched = _replace_all(
        patched,
        7076,
        "ex(6901,view_xview+170+offX,view_yview+107+offY,global.optionSelection[2],Col,0,0);",
        "ex(7028,global.optionSelection[2],view_xview+170+offX,view_yview+107+offY,Col,fa_center,1);",
    )
    patched = _replace_all(
        patched,
        7076,
        "ex(6901,view_xview+114+offX,view_yview+global.drawModalOffset+offY, global.drawModalMenuText,Col,0,0);",
        "ex(7028,global.drawModalMenuText,view_xview+114+offX,view_yview+global.drawModalOffset+offY,Col,fa_center,1);",
    )
    patched = _replace_all(
        patched,
        7076,
        "ex(6901,view_xview+122+offX,view_yview+descPosY+offY,global.drawModalText,ex(5973,global.cuadrodialogo),0,0);",
        "ex(7028,global.drawModalText,view_xview+122+offX,view_yview+descPosY+offY,ex(5973,global.cuadrodialogo),fa_center,1);",
    )
    patched = _replace_all(
        patched,
        7076,
        "ex(6901,view_xview+120+offX,view_yview+107+offY,global.drawModalMenuText,(16744448),0,0);",
        "ex(7028,global.drawModalMenuText,view_xview+120+offX,view_yview+107+offY,(16744448),fa_center,1);",
    )
    patched = _replace_all(
        patched,
        7120,
        "ex(6901,view_xview+122+offX,view_yview+global.drawModalQuestionOffset+offY,global.drawModalQuestionText, ex(5971,global.cuadrodialogo),0,0);",
        "ex(7028,global.drawModalQuestionText,view_xview+122+offX,view_yview+global.drawModalQuestionOffset+offY,ex(5971,global.cuadrodialogo),fa_center,1);",
    )
    patched = _replace_all(
        patched,
        7120,
        "ex(6901,view_xview+122+offX,view_yview+global.drawModalQuestionOffset+offY, global.drawModalQuestionText,ex(5971,global.cuadrodialogo),0,0);",
        "ex(7028,global.drawModalQuestionText,view_xview+122+offX,view_yview+global.drawModalQuestionOffset+offY,ex(5971,global.cuadrodialogo),fa_center,1);",
    )
    patched = _replace_all(
        patched,
        7120,
        "ex(6901,view_xview+69+offX,view_yview+107+offY,global.optionSelection[49],Col,0,0);",
        "ex(7028,global.optionSelection[49],view_xview+69+offX,view_yview+107+offY,Col,fa_center,1);",
    )
    patched = _replace_all(
        patched,
        7120,
        "ex(6901,view_xview+170+offX,view_yview+107+offY,global.optionSelection[50],Col,0,0);",
        "ex(7028,global.optionSelection[50],view_xview+170+offX,view_yview+107+offY,Col,fa_center,1);",
    )
    patched = _replace_all(
        patched,
        7120,
        "ex(6901,view_xview+120+offX,view_yview+107+offY,global.optionSelection[50],Col,0,0);",
        "ex(7028,global.optionSelection[50],view_xview+120+offX,view_yview+107+offY,Col,fa_center,1);",
    )
    patched = _replace(
        patched,
        7124,
        "if((54).VIEWINDEX && char<10)draw_text(x,y+42,string(char)+\" \"+global.protaname); else if((54).VIEWINDEX && char=10)draw_text(x,y+42,string(char2)+\" \"+global.protaname); else draw_text(x,y+42,global.protaname);",
        "if((54).VIEWINDEX && char<10)draw_text(x,y+42,string(char)+\" \"+global.protaname); else if((54).VIEWINDEX && char=10)draw_text(x,y+42,string(char2)+\" \"+global.protaname); else ex(7028,global.protaname,x,y+42,c_white,fa_center,1);",
    )
    patched = _replace(
        patched,
        7135,
        "if((54).VIEWINDEX && char<10)draw_text(x,y+42,string(char)+\" \"+global.rivalname); else if((54).VIEWINDEX && char=10)draw_text(x,y+42,string(char2)+\" \"+global.rivalname); else draw_text(x,y+42,global.rivalname);",
        "if((54).VIEWINDEX && char<10)draw_text(x,y+42,string(char)+\" \"+global.rivalname); else if((54).VIEWINDEX && char=10)draw_text(x,y+42,string(char2)+\" \"+global.rivalname); else ex(7028,global.rivalname,x,y+42,c_white,fa_center,1);",
    )
    patched = _replace(
        patched,
        7018,
        "draw_set_valign(fa_bottom); draw_sprite_ext(sprite_index,image_index,x,y,image_xscale,image_yscale,0,image_blend,image_alpha); ex(6901,x,y-18,str,c_white,0,1); draw_set_valign(fa_top);",
        "draw_set_valign(fa_bottom); draw_sprite_ext(sprite_index,image_index,x,y,image_xscale,image_yscale,0,image_blend,image_alpha); ex(7028,str,x,y-18,c_white,fa_center,1); draw_set_valign(fa_top);",
    )
    patched = _replace_all(
        patched,
        7013,
        'draw_text(view_xview+44,view_yview+12,NAME+" "+ex(9935,ex(9918,160),string(global.indexnivel[global.actual1])));',
        'ex(7028,NAME,view_xview+44,view_yview+12,c_white,fa_left,1); ex(7028,ex(9935,ex(9918,160),string(global.indexnivel[global.actual1])),view_xview+121,view_yview+12,c_white,fa_right,1);',
    )
    patched = _replace_all(
        patched,
        7013,
        'draw_text(view_xview+44,view_yview+30,ex(8488,global.objpoke1[global.actual1]));',
        'ex(7028,ex(8488,global.objpoke1[global.actual1]),view_xview+44,view_yview+30,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        7013,
        'draw_text(view_xview+531,view_yview+12,NAME+" "+ex(9935,ex(9918,160),string(global.nivel2[global.actual2])));',
        'ex(7028,NAME,view_xview+455,view_yview+12,c_white,fa_left,1); ex(7028,ex(9935,ex(9918,160),string(global.nivel2[global.actual2])),view_xview+531,view_yview+12,c_white,fa_right,1);',
    )
    patched = _replace_all(
        patched,
        7013,
        'draw_text(view_xview+531,view_yview+30,ex(8488,global.objpoke2[global.actual2]));',
        'ex(7028,ex(8488,global.objpoke2[global.actual2]),view_xview+531,view_yview+30,c_white,fa_right,1);',
    )
    patched = _replace_all(
        patched,
        7013,
        "draw_text(view_xview+107,view_yview+9-desp,NAME);",
        "ex(7028,NAME,view_xview+107,view_yview+9-desp,c_black,fa_left,1);",
    )
    patched = _replace_all(
        patched,
        7013,
        'draw_text(view_xview+215,view_yview+9-desp,ex(9935,ex(9918,160),string(global.indexnivel[global.actual1])));',
        'ex(7028,ex(9935,ex(9918,160),string(global.indexnivel[global.actual1])),view_xview+215,view_yview+9-desp,c_black,fa_right,1);',
    )
    patched = _replace_all(
        patched,
        7013,
        'if(global.shownumberPS=1)draw_text_color(view_xview+168,view_yview+18,ex(9936,txt_num_ps,string(global.PS_1[global.actual1]), string(global.XTRA_PS_1[global.actual1])),COLOR,COLOR,COLOR,COLOR,1);',
        'if(global.shownumberPS=1)ex(7028,ex(9936,txt_num_ps,string(global.PS_1[global.actual1]), string(global.XTRA_PS_1[global.actual1])),view_xview+168,view_yview+18,COLOR,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        7013,
        'if(global.shownumberPS=2)draw_text_color(view_xview+168,view_yview+18,ex(9936,txt_num_pp,string(global.PP_1[global.actual1]), string(global.MAX_PP_1[global.actual1])),COLOR,COLOR,COLOR,COLOR,1);',
        'if(global.shownumberPS=2)ex(7028,ex(9936,txt_num_pp,string(global.PP_1[global.actual1]), string(global.MAX_PP_1[global.actual1])),view_xview+168,view_yview+18,COLOR,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        7013,
        'if(global.shownumberPS=3)draw_text_color(view_xview+168,view_yview+18,ex(9936,txt_num_ps,string(global.PS_1[global.actual1]), string(global.XTRA_PS_1[global.actual1]))+" "+ex(9936,txt_num_pp,string(global.PP_1[global.actual1]), string(global.MAX_PP_1[global.actual1])),COLOR,COLOR,COLOR,COLOR,1);',
        'if(global.shownumberPS=3)ex(7028,ex(9936,txt_num_ps,string(global.PS_1[global.actual1]), string(global.XTRA_PS_1[global.actual1]))+" "+ex(9936,txt_num_pp,string(global.PP_1[global.actual1]), string(global.MAX_PP_1[global.actual1])),view_xview+168,view_yview+18,COLOR,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        7013,
        "draw_text(view_xview+331,view_yview+9-desp,NAME);",
        "ex(7028,NAME,view_xview+331,view_yview+9-desp,c_black,fa_left,1);",
    )
    patched = _replace_all(
        patched,
        7013,
        'draw_text(view_xview+439,view_yview+9-desp,ex(9935,ex(9918,160),string(global.nivel2[global.actual2])));',
        'ex(7028,ex(9935,ex(9918,160),string(global.nivel2[global.actual2])),view_xview+439,view_yview+9-desp,c_black,fa_right,1);',
    )
    patched = _replace_all(
        patched,
        7013,
        'if(global.shownumberPS=1)draw_text_color(view_xview+392,view_yview+18,ex(9936,txt_num_ps,string(global.PS_2[global.actual2]), string(global.XTRA_PS_2)),COLOR,COLOR,COLOR,COLOR,1);',
        'if(global.shownumberPS=1)ex(7028,ex(9936,txt_num_ps,string(global.PS_2[global.actual2]), string(global.XTRA_PS_2)),view_xview+392,view_yview+18,COLOR,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        7013,
        'if(global.shownumberPS=2)draw_text_color(view_xview+392,view_yview+18,ex(9936,txt_num_pp,string(global.PP_2[global.actual2]), string(global.MAX_PP_2)),COLOR,COLOR,COLOR,COLOR,1);',
        'if(global.shownumberPS=2)ex(7028,ex(9936,txt_num_pp,string(global.PP_2[global.actual2]), string(global.MAX_PP_2)),view_xview+392,view_yview+18,COLOR,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        7013,
        'if(global.shownumberPS=3)draw_text_color(view_xview+392,view_yview+18,ex(9936,txt_num_ps,string(global.PS_2[global.actual2]), string(global.XTRA_PS_2))+" "+ex(9936,txt_num_pp,string(global.PP_2[global.actual2]),string(global.MAX_PP_2[global.actual2])), COLOR,COLOR,COLOR,COLOR,1);',
        'if(global.shownumberPS=3)ex(7028,ex(9936,txt_num_ps,string(global.PS_2[global.actual2]), string(global.XTRA_PS_2))+" "+ex(9936,txt_num_pp,string(global.PP_2[global.actual2]),string(global.MAX_PP_2[global.actual2])),view_xview+392,view_yview+18,COLOR,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        7014,
        'draw_text(view_xview+44,view_yview+12,NAME+" "+ex(9935,ex(9918,160),string(global.indexnivel[global.actual1])));',
        'ex(7028,NAME,view_xview+44,view_yview+12,c_white,fa_left,1); ex(7028,ex(9935,ex(9918,160),string(global.indexnivel[global.actual1])),view_xview+121,view_yview+12,c_white,fa_right,1);',
    )
    patched = _replace_all(
        patched,
        7014,
        'draw_text(view_xview+44,view_yview+30,ex(8488,global.objpoke1[global.actual1]));',
        'ex(7028,ex(8488,global.objpoke1[global.actual1]),view_xview+44,view_yview+30,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        7014,
        'draw_text(view_xview+369,view_yview+12,NAME+" "+ex(9935,ex(9918,160),string(global.nivel2[global.actual2])));',
        'ex(7028,NAME,view_xview+293,view_yview+12,c_white,fa_left,1); ex(7028,ex(9935,ex(9918,160),string(global.nivel2[global.actual2])),view_xview+369,view_yview+12,c_white,fa_right,1);',
    )
    patched = _replace_all(
        patched,
        7014,
        'draw_text(view_xview+369,view_yview+30,ex(8488,global.objpoke2[global.actual2]));',
        'ex(7028,ex(8488,global.objpoke2[global.actual2]),view_xview+369,view_yview+30,c_white,fa_right,1);',
    )
    patched = _replace_all(
        patched,
        7014,
        "draw_text(view_xview+331,view_yview+9-desp,NAME);",
        "ex(7028,NAME,view_xview+331,view_yview+9-desp,c_black,fa_left,1);",
    )
    patched = _replace_all(
        patched,
        7014,
        'draw_text(view_xview+439,view_yview+9-desp,ex(9935,ex(9918,160),string(global.indexnivel[global.actual1])));',
        'ex(7028,ex(9935,ex(9918,160),string(global.indexnivel[global.actual1])),view_xview+439,view_yview+9-desp,c_black,fa_right,1);',
    )
    patched = _replace_all(
        patched,
        7014,
        'if(global.shownumberPS=1)draw_text_color(view_xview+392,view_yview+18,ex(9936,txt_num_ps,string(global.PS_1[global.actual1]), string(global.XTRA_PS_1[global.actual1])),COLOR,COLOR,COLOR,COLOR,1);',
        'if(global.shownumberPS=1)ex(7028,ex(9936,txt_num_ps,string(global.PS_1[global.actual1]), string(global.XTRA_PS_1[global.actual1])),view_xview+392,view_yview+18,COLOR,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        7014,
        'if(global.shownumberPS=2)draw_text_color(view_xview+392,view_yview+18,ex(9936,txt_num_pp,string(global.PP_1[global.actual1]), string(global.MAX_PP_1[global.actual1])),COLOR,COLOR,COLOR,COLOR,1);',
        'if(global.shownumberPS=2)ex(7028,ex(9936,txt_num_pp,string(global.PP_1[global.actual1]), string(global.MAX_PP_1[global.actual1])),view_xview+392,view_yview+18,COLOR,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        7014,
        'if(global.shownumberPS=3)draw_text_color(view_xview+392,view_yview+18,ex(9936,txt_num_ps,string(global.PS_1[global.actual1]), string(global.XTRA_PS_1[global.actual1]))+" "+ex(9936,txt_num_pp,string(global.PP_1[global.actual1]), string(global.MAX_PP_1[global.actual1])),COLOR,COLOR,COLOR,COLOR,1);',
        'if(global.shownumberPS=3)ex(7028,ex(9936,txt_num_ps,string(global.PS_1[global.actual1]), string(global.XTRA_PS_1[global.actual1]))+" "+ex(9936,txt_num_pp,string(global.PP_1[global.actual1]), string(global.MAX_PP_1[global.actual1])),view_xview+392,view_yview+18,COLOR,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        7014,
        "draw_text(view_xview+107,view_yview+9-desp,NAME);",
        "ex(7028,NAME,view_xview+107,view_yview+9-desp,c_black,fa_left,1);",
    )
    patched = _replace_all(
        patched,
        7014,
        'draw_text(view_xview+215,view_yview+9-desp,ex(9935,ex(9918,160),string(global.nivel2[global.actual2])));',
        'ex(7028,ex(9935,ex(9918,160),string(global.nivel2[global.actual2])),view_xview+215,view_yview+9-desp,c_black,fa_right,1);',
    )
    patched = _replace_all(
        patched,
        7014,
        'if(global.shownumberPS=1)draw_text_color(view_xview+168,view_yview+18,ex(9936,txt_num_ps,string(global.PS_2[global.actual2]), string(global.XTRA_PS_2)),COLOR,COLOR,COLOR,COLOR,1);',
        'if(global.shownumberPS=1)ex(7028,ex(9936,txt_num_ps,string(global.PS_2[global.actual2]), string(global.XTRA_PS_2)),view_xview+168,view_yview+18,COLOR,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        7014,
        'if(global.shownumberPS=2)draw_text_color(view_xview+168,view_yview+18,ex(9936,txt_num_pp,string(global.PP_2[global.actual2]), string(global.MAX_PP_2)),COLOR,COLOR,COLOR,COLOR,1);',
        'if(global.shownumberPS=2)ex(7028,ex(9936,txt_num_pp,string(global.PP_2[global.actual2]), string(global.MAX_PP_2)),view_xview+168,view_yview+18,COLOR,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        7014,
        'if(global.shownumberPS=3)draw_text_color(view_xview+168,view_yview+18,ex(9936,txt_num_ps,string(global.PS_2[global.actual2]), string(global.XTRA_PS_2))+" "+ex(9936,txt_num_pp,string(global.PP_2[global.actual2]),string(global.MAX_PP_2[global.actual2])), COLOR,COLOR,COLOR,COLOR,1);',
        'if(global.shownumberPS=3)ex(7028,ex(9936,txt_num_ps,string(global.PS_2[global.actual2]), string(global.XTRA_PS_2))+" "+ex(9936,txt_num_pp,string(global.PP_2[global.actual2]),string(global.MAX_PP_2[global.actual2])),view_xview+168,view_yview+18,COLOR,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        7013,
        'draw_text(view_xview+112,view_yview+80,str);',
        'rest=str; line_y=view_yview+80; while(true){ cut=string_pos("#",rest); if(cut>0){ line_text=string_copy(rest,1,cut-1); rest=string_delete(rest,1,cut); } else { line_text=rest; rest=""; } if(line_text!=""){ if(global.language="zh" && global.zh_text_key_map!=(-1) && !ds_map_exists(global.zh_text_key_map,line_text)){ var dash_pos, part1, part2, key1, key2, pair_key; dash_pos=string_pos(" - ",line_text); if(dash_pos>0){ part1=string_copy(line_text,1,dash_pos-1); part2=string_delete(line_text,1,dash_pos+2); if(part1!="" && part2!=""){ key1=""; key2=""; if(ds_map_exists(global.zh_text_key_map,part1))key1=ds_map_find_value(global.zh_text_key_map,part1); if(ds_map_exists(global.zh_text_key_map,part2))key2=ds_map_find_value(global.zh_text_key_map,part2); pair_key="zh__custom__pair_dash"; if(key1!="")pair_key+="__par1__"+key1; else pair_key+="__par1raw__"+part1; if(key2!="")pair_key+="__par2__"+key2; else pair_key+="__par2raw__"+part2; if(ds_map_exists(global.zh_text_key_map,line_text))ds_map_replace(global.zh_text_key_map,line_text,pair_key); else ds_map_add(global.zh_text_key_map,line_text,pair_key); }}} ex(7028,line_text,view_xview+112,line_y,c_white,fa_left,0.9); line_y+=11; } if(rest="")break; }',
    )
    patched = _replace_all(
        patched,
        7014,
        'draw_text(view_xview+464,view_yview+80,str);',
        'rest=str; line_y=view_yview+80; while(true){ cut=string_pos("#",rest); if(cut>0){ line_text=string_copy(rest,1,cut-1); rest=string_delete(rest,1,cut); } else { line_text=rest; rest=""; } if(line_text!=""){ if(global.language="zh" && global.zh_text_key_map!=(-1) && !ds_map_exists(global.zh_text_key_map,line_text)){ var dash_pos, part1, part2, key1, key2, pair_key; dash_pos=string_pos(" - ",line_text); if(dash_pos>0){ part1=string_copy(line_text,1,dash_pos-1); part2=string_delete(line_text,1,dash_pos+2); if(part1!="" && part2!=""){ key1=""; key2=""; if(ds_map_exists(global.zh_text_key_map,part1))key1=ds_map_find_value(global.zh_text_key_map,part1); if(ds_map_exists(global.zh_text_key_map,part2))key2=ds_map_find_value(global.zh_text_key_map,part2); pair_key="zh__custom__pair_dash"; if(key1!="")pair_key+="__par1__"+key1; else pair_key+="__par1raw__"+part1; if(key2!="")pair_key+="__par2__"+key2; else pair_key+="__par2raw__"+part2; if(ds_map_exists(global.zh_text_key_map,line_text))ds_map_replace(global.zh_text_key_map,line_text,pair_key); else ds_map_add(global.zh_text_key_map,line_text,pair_key); }}} ex(7028,line_text,view_xview+464,line_y,c_white,fa_right,0.9); line_y+=11; } if(rest="")break; }',
    )
    patched = _replace_all(
        patched,
        7077,
        'for(i=0;i<=3;i+=1){ ex(6901,281,30+i*16,txt_pp,0,(13160656),1);}',
        'draw_set_font((3)); for(i=0;i<=3;i+=1){ ex(6901,281,30+i*16,"PP",0,(13160656),1);}',
    )
    patched = _replace_all(
        patched,
        9425,
        'draw_text(24,79,ex(8474,CONTACTOS[VISTA]));',
        'ex(7028,ex(8474,CONTACTOS[VISTA]),24,79,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9425,
        'draw_text(169,79,ex(8474,CONTACTOS[VISTA+1]));',
        'ex(7028,ex(8474,CONTACTOS[VISTA+1]),169,79,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9425,
        'draw_text(24,91,ex(8474,CONTACTOS[VISTA+2]));',
        'ex(7028,ex(8474,CONTACTOS[VISTA+2]),24,91,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9425,
        'draw_text(169,91,ex(8474,CONTACTOS[VISTA+3]));',
        'ex(7028,ex(8474,CONTACTOS[VISTA+3]),169,91,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9425,
        'draw_text(24,103,ex(8474,CONTACTOS[VISTA+4]));',
        'ex(7028,ex(8474,CONTACTOS[VISTA+4]),24,103,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9425,
        'draw_text(169,103,ex(8474,CONTACTOS[VISTA+5]));',
        'ex(7028,ex(8474,CONTACTOS[VISTA+5]),169,103,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9425,
        'draw_text(24,115,ex(8474,CONTACTOS[VISTA+6]));',
        'ex(7028,ex(8474,CONTACTOS[VISTA+6]),24,115,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9425,
        'draw_text(169,115,ex(8474,CONTACTOS[VISTA+7]));',
        'ex(7028,ex(8474,CONTACTOS[VISTA+7]),169,115,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9425,
        'draw_text(160,82,NAME_TRAINER);',
        'ex(7028,NAME_TRAINER,160,82,c_yellow,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        9425,
        'draw_text(160,103,txt_llamada);',
        'ex(7028,txt_llamada,160,103,c_white,fa_center,1);',
    )
    patched = _replace(
        patched,
        9425,
        "if(ESTADO=5)draw_set_color(c_red); else draw_set_color(c_white); draw_set_font((2)); draw_text(58,20,TEXT);",
        "draw_set_font((2)); if(ESTADO=5)ex(7028,TEXT,58,20,c_red,fa_left,1); else ex(7028,TEXT,58,20,c_white,fa_left,1);",
    )
    patched = _replace_all(
        patched,
        9474,
        'draw_text(315,9,ex(8490,global.pkmn2[0]));',
        'ex(7028,ex(8490,global.pkmn2[0]),315,9,c_black,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9474,
        'draw_text(423,9,ex(9935,txt_nv,string(global.nivel2[0])));',
        'ex(7028,ex(9935,txt_nv,string(global.nivel2[0])),423,9,c_black,fa_right,1);',
    )

    patched = _replace(
        patched,
        6982,
        "draw_set_font((19)); draw_set_halign(fa_left); draw_set_color(c_white); draw_text(3,18,txt_help1); draw_text(48,18,txt_help2); draw_text(93,18,txt_help3); draw_text(138,18,txt_help4);",
        "draw_set_font((19)); draw_set_halign(fa_left); draw_set_color(c_white); ex(7028,txt_help1,3,18,c_white,fa_left,1); ex(7028,txt_help2,48,18,c_white,fa_left,1); ex(7028,txt_help3,93,18,c_white,fa_left,1); ex(7028,txt_help4,138,18,c_white,fa_left,1);",
    )
    patched = _replace(
        patched,
        6982,
        "draw_text_color(160,80,txt_desc,0,0,0,0,0.6);",
        "ex(7028,txt_desc,160,80,0,fa_center,0.6);",
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,275,160,ex(9935,txt_pag,string(pag)),c_white,0,1);',
        'ex(7028,ex(9935,txt_pag,string(pag)),275,160,c_white,fa_left,1);',
    )
    patched = _replace(
        patched,
        6982,
        'if(num_paginas>1){ ex(6901,275,160,ex(9935,txt_pag,string(EV)),c_white,0,1);}',
        'if(num_paginas>1){ ex(7028,ex(9935,txt_pag,string(EV)),275,160,c_white,fa_left,1);}',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,15,45,txt_load,c_white,c_black,1);',
        'ex(7028,txt_load,15,45,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,15,45,txt_noinfo,c_white,c_black,1);',
        'ex(7028,txt_noinfo,15,45,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,15,45+16*i,texto,c_white,c_black,1);',
        'ex(7028,texto,15,45+16*i,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,216,45+16*i,ex(9935,txt_pb,ex(7818,PB!="0",PB,"--")),c_white,c_black,1);',
        'ex(7028,ex(9935,txt_pb,ex(7818,PB!="0",PB,"--")),264,45+16*i,c_white,fa_right,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,262,45+16*i,ex(9935,txt_pp,PP),c_white,c_black,1);',
        'ex(7028,ex(9935,txt_pp,PP),313,45+16*i,c_white,fa_right,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'if(pag=1){ if(listaAtdxNv[posAtaque+i]>=200){ texto=ex(9935,ex(9928,1542),ex(8471,listaAtdx[posAtaque+i])); ex(7028,texto,15,45+16*i,c_white,fa_left,1); } else { draw_set_halign(fa_right); ex(6901,32,45+16*i,string(listaAtdxNv[posAtaque+i]),c_white,c_black,1); draw_set_halign(fa_left); ex(7028,ex(8471,listaAtdx[posAtaque+i]),45,45+16*i,c_white,fa_left,1); } ex(7161,ex(9946,listaAtdx[posAtaque+i]),137,46+16*i); draw_set_font((4));draw_set_halign(fa_left); draw_sprite((171),ex(8426,listaAtdx[posAtaque+i]),170,46+16*i); var PB, PP; PB=string(ex(9944,listaAtdx[posAtaque+i])); PP=string(ex(9945,listaAtdx[posAtaque+i])); ex(7028,ex(9935,txt_pb,ex(7818,PB!="0",PB,"--")),264,45+16*i,c_white,fa_right,1); ex(7028,ex(9935,txt_pp,PP),313,45+16*i,c_white,fa_right,1); }',
        'if(pag=1){ if(listaAtdxNv[posAtaque+i]>=200){ texto=ex(9935,ex(9928,1542),ex(8471,listaAtdx[posAtaque+i])); ex(7028,texto,15,45+16*i,c_white,fa_left,1); } else { draw_set_halign(fa_right); ex(6901,32,45+16*i,string(listaAtdxNv[posAtaque+i]),c_white,c_black,1); draw_set_halign(fa_left); ex(7028,ex(8471,listaAtdx[posAtaque+i]),45,45+16*i,c_white,fa_left,1); } ex(7161,ex(9946,listaAtdx[posAtaque+i]),137,46+16*i); draw_set_font((4));draw_set_halign(fa_left); draw_sprite((171),ex(8426,listaAtdx[posAtaque+i]),170,46+16*i); var PB, PP; PB=string(ex(9944,listaAtdx[posAtaque+i])); PP=string(ex(9945,listaAtdx[posAtaque+i])); ex(7028,ex(9935,txt_pb,ex(7818,PB!="0",PB,"--")),264,45+16*i,c_white,fa_right,1); ex(7028,ex(9935,txt_pp,PP),313,45+16*i,c_white,fa_right,1); }',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,9,22,ex(9935,txt_ataques1,name),c_yellow,0,1);',
        'ex(7028,ex(9935,txt_ataques1,name),9,22,c_yellow,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,9,22,ex(9935,txt_ataques2,name),c_yellow,0,1);',
        'ex(7028,ex(9935,txt_ataques2,name),9,22,c_yellow,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,9,22,ex(9935,txt_ataques3,name),c_yellow,0,1);',
        'ex(7028,ex(9935,txt_ataques3,name),9,22,c_yellow,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,9,22,ex(9935,txt_ataques4,name),c_yellow,0,1);',
        'ex(7028,ex(9935,txt_ataques4,name),9,22,c_yellow,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,9,22,ex(9935,txt_ataques5,name),c_yellow,0,1);',
        'ex(7028,ex(9935,txt_ataques5,name),9,22,c_yellow,fa_left,1);',
    )
    patched = _replace(
        patched,
        6982,
        'if(VIENDOSHINY=false)ex(6901,9,22,txt_evol1,c_yellow,0,1); else ex(6901,9,22,txt_evol2,c_yellow,0,1);',
        'if(VIENDOSHINY=false)ex(7028,txt_evol1,9,22,c_yellow,fa_left,1); else ex(7028,txt_evol2,9,22,c_yellow,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,9,22,ex(9935,txt_statsgen1,name),c_yellow,0,1);',
        'ex(7028,ex(9935,txt_statsgen1,name),9,22,c_yellow,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,49,52,ttlstats_sinPP,c_white,c_black,1);',
        'ex(7028,ttlstats_sinPP,49,52,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,140,52,stats_sinPP,c_white,c_black,1);',
        'ex(7028,stats_sinPP,140,52,c_white,fa_right,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,49,40,ttlstats,c_white,c_black,1);',
        'ex(7028,ttlstats,49,40,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,140,40,stats,c_white,c_black,1);',
        'ex(7028,stats,140,40,c_white,fa_right,1);',
    )
    patched = _replace(
        patched,
        6982,
        'ex(7028,ttlstats_sinPP,49,52,c_white,fa_left,1);     draw_set_halign(fa_right);     ex(7028,stats_sinPP,140,52,c_white,fa_right,1);     draw_set_halign(fa_left);',
        'ex(7028,ex(9928,803),49,52,c_white,fa_left,1); draw_set_halign(fa_right); ex(6901,140,52,string(stat_sinPP[0]),c_white,c_black,1); draw_set_halign(fa_left); ex(7028,ex(9928,804),49,67,c_white,fa_left,1); draw_set_halign(fa_right); ex(6901,140,67,string(stat_sinPP[1]),c_white,c_black,1); draw_set_halign(fa_left); ex(7028,ex(9928,805),49,82,c_white,fa_left,1); draw_set_halign(fa_right); ex(6901,140,82,string(stat_sinPP[2]),c_white,c_black,1); draw_set_halign(fa_left); ex(7028,ex(9928,806),49,97,c_white,fa_left,1); draw_set_halign(fa_right); ex(6901,140,97,string(stat_sinPP[3]),c_white,c_black,1); draw_set_halign(fa_left); ex(7028,ex(9928,807),49,112,c_white,fa_left,1); draw_set_halign(fa_right); ex(6901,140,112,string(stat_sinPP[4]),c_white,c_black,1); draw_set_halign(fa_left); ex(7028,ex(9928,808),49,127,c_white,fa_left,1); draw_set_halign(fa_right); ex(6901,140,127,string(stat_sinPP[5]),c_white,c_black,1); draw_set_halign(fa_left); ex(7028,ex(9942,"txt_battle",353),49,142,c_white,fa_left,1); draw_set_halign(fa_right); ex(6901,140,142,string(stat_sinPP[6]),c_white,c_black,1); draw_set_halign(fa_left);',
    )
    patched = _replace(
        patched,
        6982,
        'ex(7028,ttlstats,49,40,c_white,fa_left,1);     draw_set_halign(fa_right);     ex(7028,stats,140,40,c_white,fa_right,1);     draw_set_halign(fa_left);',
        'ex(7028,ex(9928,803),49,40,c_white,fa_left,1); draw_set_halign(fa_right); ex(6901,140,40,string(stat[0]),c_white,c_black,1); draw_set_halign(fa_left); ex(7028,ex(9928,815),49,55,c_white,fa_left,1); draw_set_halign(fa_right); ex(6901,140,55,string(stat[1]),c_white,c_black,1); draw_set_halign(fa_left); ex(7028,ex(9928,804),49,70,c_white,fa_left,1); draw_set_halign(fa_right); ex(6901,140,70,string(stat[2]),c_white,c_black,1); draw_set_halign(fa_left); ex(7028,ex(9928,805),49,85,c_white,fa_left,1); draw_set_halign(fa_right); ex(6901,140,85,string(stat[3]),c_white,c_black,1); draw_set_halign(fa_left); ex(7028,ex(9928,806),49,100,c_white,fa_left,1); draw_set_halign(fa_right); ex(6901,140,100,string(stat[4]),c_white,c_black,1); draw_set_halign(fa_left); ex(7028,ex(9928,807),49,115,c_white,fa_left,1); draw_set_halign(fa_right); ex(6901,140,115,string(stat[5]),c_white,c_black,1); draw_set_halign(fa_left); ex(7028,ex(9928,808),49,130,c_white,fa_left,1); draw_set_halign(fa_right); ex(6901,140,130,string(stat[6]),c_white,c_black,1); draw_set_halign(fa_left); ex(7028,ex(9942,"txt_battle",353),49,145,c_white,fa_left,1); draw_set_halign(fa_right); ex(6901,140,145,string(stat[7]),c_white,c_black,1); draw_set_halign(fa_left);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,9,22,ex(9935,txt_adicional1,name),c_yellow,0,1);',
        'ex(7028,ex(9935,txt_adicional1,name),9,22,c_yellow,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,9,22,ex(9935,txt_adicional2,name),c_yellow,0,1);',
        'ex(7028,ex(9935,txt_adicional2,name),9,22,c_yellow,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,9,22,ex(9935,ex(7818,VIENDOSHINY,txt_adicionalshiny3,txt_adicional3),name),c_yellow,0,1);',
        'ex(7028,ex(9935,ex(7818,VIENDOSHINY,txt_adicionalshiny3,txt_adicional3),name),9,22,c_yellow,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,9,22,ex(9935,txt_adicional4,name),c_yellow,0,1);',
        'ex(7028,ex(9935,txt_adicional4,name),9,22,c_yellow,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,117,42,ex(9935,txt_poke,EspecDex),4471868,(13160656),1);',
        'ex(7028,ex(9935,txt_poke,EspecDex),117,42,4471868,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,16,126,InfoDex,4471868,(13160656),1);',
        'ex(7028,InfoDex,16,122,4471868,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,129,60,txt_alt,0,12105912,1);',
        'ex(7028,txt_alt,129,60,0,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,165,60,AltoDex,4471868,(13160656),1);',
        'ex(7028,AltoDex,165,60,4471868,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,129,76,txt_peso,0,12105912,1);',
        'ex(7028,txt_peso,129,76,0,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,165,76,PesoDex,4471868,(13160656),1);',
        'ex(7028,PesoDex,165,76,4471868,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,56,70,ex(8490,son),c_white,c_black,1);',
        'ex(7028,ex(8490,son),56,70,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,59,60,txt_obj1,ex(5769,objeto1),c_black,1);',
        'ex(7028,txt_obj1,59,60,ex(5769,objeto1),fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,59,97,txt_obj2,ex(5769,objeto2),c_black,1);',
        'ex(7028,txt_obj2,59,97,ex(5769,objeto2),fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,59,134,txt_obj3,ex(5769,objeto3),c_black,1);',
        'ex(7028,txt_obj3,59,134,ex(5769,objeto3),fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,20,61,ex(8481,h1),COLOR,c_black,1);',
        'ex(7028,ex(8481,h1),20,61,COLOR,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,150,61,ex(8481,h2),COLOR,c_black,1);',
        'ex(7028,ex(8481,h2),150,61,COLOR,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,20,115,ex(8481,ho1),COLOR,c_black,1);',
        'ex(7028,ex(8481,ho1),20,115,COLOR,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,150,115,ex(8481,ho2),COLOR,c_black,1);',
        'ex(7028,ex(8481,ho2),150,115,COLOR,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,117,28,"Nº00"+string(global.pkdexAC)+" "+name,4471868,(13160656),1);',
        'ex(7028,"Nº00"+string(global.pkdexAC)+" "+name,117,28,4471868,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,117,28,"Nº0"+string(global.pkdexAC)+" "+name,4471868,(13160656),1);',
        'ex(7028,"Nº0"+string(global.pkdexAC)+" "+name,117,28,4471868,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,117,28,"Nº"+string(global.pkdexAC)+" "+name,4471868,(13160656),1);',
        'ex(7028,"Nº"+string(global.pkdexAC)+" "+name,117,28,4471868,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        6982,
        'ex(6901,117,28," > "+name,4471868,(13160656),1);',
        'ex(7028," > "+name,117,28,4471868,fa_left,1);',
    )
    patched = _replace(
        patched,
        7066,
        'draw_text_color(53,9,txt_obj,(6316128),(6316128),(6316128),(6316128),1); draw_text_color(52,8,txt_obj,c_white,c_white,c_white,c_white,1);',
        'ex(7028,txt_obj,52,8,c_white,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        7066,
        'draw_text_color(9,141,ex(5229,DESC,302,(3)),c_white,c_white,c_white,c_white,1);',
        'ex(7028,ex(5229,DESC,302,(3)),9,141,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        7066,
        'draw_text_color(134,10+16*j,ex(8488,global.ObItem[i]),COLOR,COLOR,COLOR,COLOR,1);',
        'ex(7028,ex(8488,global.ObItem[i]),134,10+16*j,COLOR,fa_left,1);',
    )
    patched = _replace(
        patched,
        9326,
        'draw_text_color(53,9,txt_clave,(6316128),(6316128),(6316128),(6316128),1); draw_text_color(52,8,txt_clave,c_white,c_white,c_white,c_white,1);',
        'ex(7028,txt_clave,52,8,c_white,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        9326,
        'draw_text_color(9,141,ex(5229,DESC,302,(3)),c_white,c_white,c_white,c_white,1);',
        'ex(7028,ex(5229,DESC,302,(3)),9,141,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9326,
        'draw_text_color(134,10+16*j,ex(8488,global.ObClave[i]),COLOR,COLOR,COLOR,COLOR,1);',
        'ex(7028,ex(8488,global.ObClave[i]),134,10+16*j,COLOR,fa_left,1);',
    )
    patched = _replace(
        patched,
        9327,
        'draw_text_color(53,9,txt_mtmo,(6316128),(6316128),(6316128),(6316128),1); draw_text_color(52,8,txt_mtmo,c_white,c_white,c_white,c_white,1);',
        'ex(7028,txt_mtmo,52,8,c_white,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        9327,
        'if(OB>0)draw_text_color(64,141,ex(5229,DESC,185,(3)),c_white,c_white,c_white,c_white,1); else draw_text_color(9,141,ex(5229,DESC,185,(3)),c_white,c_white,c_white,c_white,1);',
        'if(OB>0)ex(7028,ex(5229,DESC,185,(3)),64,141,c_white,fa_left,1); else ex(7028,ex(5229,DESC,185,(3)),9,141,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9327,
        'draw_text_color(265,141,ex(9935,txt_pb,string(PB)),c_white,c_white,c_white,c_white,1); draw_text_color(266,157,ex(9935,txt_pp,string(PP)),c_white,c_white,c_white,c_white,1);',
        'ex(7028,ex(9935,txt_pb,string(PB)),265,141,c_white,fa_left,1); ex(7028,ex(9935,txt_pp,string(PP)),266,157,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9327,
        'draw_text_color(134,10+16*j,ex(8488,global.ObMT[i]),COLOR,COLOR,COLOR,COLOR,ALPHA);',
        'ex(7028,ex(8488,global.ObMT[i]),134,10+16*j,COLOR,fa_left,ALPHA);',
    )
    patched = _replace(
        patched,
        9328,
        'draw_text_color(53,9,txt_ball,(6316128),(6316128),(6316128),(6316128),1); draw_text_color(52,8,txt_ball,c_white,c_white,c_white,c_white,1);',
        'ex(7028,txt_ball,52,8,c_white,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        9328,
        'draw_text_color(9,141,ex(5229,ex(9936,txt_descball,DESC,txt_ball_safari),302,(3)),c_white,c_white,c_white,c_white,1);',
        '{ex(7028,ex(5229,DESC,302,(3)),9,141,c_white,fa_left,1); ex(7028,ex(9935,txt_usa,txt_ball_safari),9,157,c_white,fa_left,1);}',
    )
    patched = _replace_all(
        patched,
        9328,
        'draw_text_color(9,141,ex(5229,ex(9936,txt_descball,DESC,txt_ball_battle),222,(3)),c_white,c_white,c_white,c_white,1);',
        '{ex(7028,ex(5229,DESC,222,(3)),9,141,c_white,fa_left,1); ex(7028,ex(9935,txt_usa,txt_ball_battle),9,157,c_white,fa_left,1);}',
    )
    patched = _replace_all(
        patched,
        9328,
        'draw_text_color(9,141,ex(5229,ex(9935,txt_asignaBall,DESC),222,(3)),c_white,c_white,c_white,c_white,1);',
        'ex(7028,ex(5229,ex(9935,txt_asignaBall,DESC),222,(3)),9,141,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9328,
        'draw_text_color(9,141,ex(5229,DESC,302,(3)),c_white,c_white,c_white,c_white,1);',
        'ex(7028,ex(5229,DESC,302,(3)),9,141,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9328,
        'draw_text_color(134,10+16*j,ex(8488,global.ObBall[i]),COLOR,COLOR,COLOR,COLOR,1);',
        'ex(7028,ex(8488,global.ObBall[i]),134,10+16*j,COLOR,fa_left,1);',
    )
    patched = _replace(
        patched,
        9329,
        'draw_text_color(53,9,txt_baya,(6316128),(6316128),(6316128),(6316128),1); draw_text_color(52,8,txt_baya,c_white,c_white,c_white,c_white,1);',
        'ex(7028,txt_baya,52,8,c_white,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        9329,
        'if(global.baya_asign!=global.SELBaya)draw_text_color(9,141,txt_asigna,c_white,c_white,c_white,c_white,1); else draw_text_color(9,141,ex(9935,txt_usa,txt_tecla_safari),c_white,c_white,c_white,c_white,1);',
        'if(global.baya_asign!=global.SELBaya)ex(7028,txt_asigna,9,141,c_white,fa_left,1); else ex(7028,ex(9935,txt_usa,txt_tecla_safari),9,141,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9329,
        'else draw_text_color(9,141,ex(5229,DESC,302,(3)),c_white,c_white,c_white,c_white,1);',
        'else ex(7028,ex(5229,DESC,302,(3)),9,141,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9329,
        'if(ex(7603,global.ObBaya[i])<=9)draw_text_color(134,10+16*j,"Nº0"+string(ex(7603,global.ObBaya[i]))+" "+ex(8488,global.ObBaya[i]),COLOR,COLOR,COLOR,COLOR,1); else  draw_text_color(134,10+16*j,"Nº"+string(ex(7603,global.ObBaya[i]))+" "+ex(8488,global.ObBaya[i]),COLOR,COLOR,COLOR,COLOR,1);',
        'if(ex(7603,global.ObBaya[i])<=9){ draw_set_halign(fa_left); ex(6901,134,10+16*j,"Nº0"+string(ex(7603,global.ObBaya[i])),COLOR,COLOR,1); ex(7028,ex(8488,global.ObBaya[i]),170,10+16*j,COLOR,fa_left,1);} else { draw_set_halign(fa_left); ex(6901,134,10+16*j,"Nº"+string(ex(7603,global.ObBaya[i])),COLOR,COLOR,1); ex(7028,ex(8488,global.ObBaya[i]),170,10+16*j,COLOR,fa_left,1);}',
    )
    patched = _replace_all(
        patched,
        9330,
        'draw_text_color(9,141,ex(5229,DESC,302,(3)),c_white,c_white,c_white,c_white,1);',
        'ex(7028,ex(5229,DESC,302,(3)),9,141,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9330,
        'draw_text_color(53,9,txt_botiquin,(6316128),(6316128),(6316128),(6316128),1); draw_text_color(52,8,txt_botiquin,c_white,c_white,c_white,c_white,1);',
        'ex(7028,txt_botiquin,52,8,c_white,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        9330,
        'draw_text_color(53,9,txt_mejoras,(6316128),(6316128),(6316128),(6316128),1); draw_text_color(52,8,txt_mejoras,c_white,c_white,c_white,c_white,1);',
        'ex(7028,txt_mejoras,52,8,c_white,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        9330,
        'draw_text_color(53,9,txt_utilidades,(6316128),(6316128),(6316128),(6316128),1); draw_text_color(52,8,txt_utilidades,c_white,c_white,c_white,c_white,1);',
        'ex(7028,txt_utilidades,52,8,c_white,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        9330,
        'draw_text_color(53,9,txt_evolucion,(6316128),(6316128),(6316128),(6316128),1); draw_text_color(52,8,txt_evolucion,c_white,c_white,c_white,c_white,1);',
        'ex(7028,txt_evolucion,52,8,c_white,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        9330,
        'draw_text_color(53,9,txt_estrategia,(6316128),(6316128),(6316128),(6316128),1); draw_text_color(52,8,txt_estrategia,c_white,c_white,c_white,c_white,1);',
        'ex(7028,txt_estrategia,52,8,c_white,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        9330,
        'draw_text_color(53,9,txt_valioso,(6316128),(6316128),(6316128),(6316128),1); draw_text_color(52,8,txt_valioso,c_white,c_white,c_white,c_white,1);',
        'ex(7028,txt_valioso,52,8,c_white,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        9330,
        'draw_text_color(53,9,txt_megapiedras,(6316128),(6316128),(6316128),(6316128),1); draw_text_color(52,8,txt_megapiedras,c_white,c_white,c_white,c_white,1);',
        'ex(7028,txt_megapiedras,52,8,c_white,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        9330,
        'draw_text_color(53,9,txt_cristalesZ,(6316128),(6316128),(6316128),(6316128),1); draw_text_color(52,8,txt_cristalesZ,c_white,c_white,c_white,c_white,1);',
        'ex(7028,txt_cristalesZ,52,8,c_white,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        9330,
        'draw_text_color(134,10+16*j,ex(8488,global.ObItem[ElemBotiquin[i]]),COLOR,COLOR,COLOR,COLOR,1);',
        'ex(7028,ex(8488,global.ObItem[ElemBotiquin[i]]),134,10+16*j,COLOR,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9330,
        'draw_text_color(134,10+16*j,ex(8488,global.ObItem[ElemMejoras[i]]),COLOR,COLOR,COLOR,COLOR,1);',
        'ex(7028,ex(8488,global.ObItem[ElemMejoras[i]]),134,10+16*j,COLOR,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9330,
        'draw_text_color(134,10+16*j,ex(8488,global.ObItem[ElemUtilidades[i]]),COLOR,COLOR,COLOR,COLOR,1);',
        'ex(7028,ex(8488,global.ObItem[ElemUtilidades[i]]),134,10+16*j,COLOR,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9330,
        'draw_text_color(134,10+16*j,ex(8488,global.ObItem[ElemEvolucion[i]]),COLOR,COLOR,COLOR,COLOR,1);',
        'ex(7028,ex(8488,global.ObItem[ElemEvolucion[i]]),134,10+16*j,COLOR,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9330,
        'draw_text_color(134,10+16*j,ex(8488,global.ObItem[ElemEstrategia[i]]),COLOR,COLOR,COLOR,COLOR,1);',
        'ex(7028,ex(8488,global.ObItem[ElemEstrategia[i]]),134,10+16*j,COLOR,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9330,
        'draw_text_color(134,10+16*j,ex(8488,global.ObItem[ElemValioso[i]]),COLOR,COLOR,COLOR,COLOR,1);',
        'ex(7028,ex(8488,global.ObItem[ElemValioso[i]]),134,10+16*j,COLOR,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9330,
        'draw_text_color(134,10+16*j,ex(8488,global.ObItem[ElemMegapiedras[i]]),COLOR,COLOR,COLOR,COLOR,1);',
        'ex(7028,ex(8488,global.ObItem[ElemMegapiedras[i]]),134,10+16*j,COLOR,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9330,
        'draw_text_color(134,10+16*j,ex(8488,global.ObItem[ElemCristalesZ[i]]),COLOR,COLOR,COLOR,COLOR,1);',
        'ex(7028,ex(8488,global.ObItem[ElemCristalesZ[i]]),134,10+16*j,COLOR,fa_left,1);',
    )
    patched = _replace(
        patched,
        9331,
        'draw_text_color(53,9,txt_frente,(6316128),(6316128),(6316128),(6316128),1); draw_text_color(52,8,txt_frente,c_white,c_white,c_white,c_white,1);',
        'ex(7028,txt_frente,52,8,c_white,fa_center,1);',
    )
    patched = _replace_all(
        patched,
        9331,
        'draw_text_color(9,141,ex(5229,DESC,302,(3)),c_white,c_white,c_white,c_white,1);',
        'ex(7028,ex(5229,DESC,302,(3)),9,141,c_white,fa_left,1);',
    )
    patched = _replace_all(
        patched,
        9331,
        'draw_text_color(134,10+16*j,ex(8488,(1099).ObItem[i]),COLOR,COLOR,COLOR,COLOR,1);',
        'ex(7028,ex(8488,(1099).ObItem[i]),134,10+16*j,COLOR,fa_left,1);',
    )

    patched = _apply_startup_and_save_isolation_patches(patched)

    return patched


def _apply_startup_and_save_isolation_patches(raw: bytes) -> bytes:
    return patch_script_batch(
        raw,
        source_updates={10054: STARTUP_VALIDATION_BYPASS_SOURCE},
        replace_updates={
            script_index: [(SAVE_ISOLATION_OLD_PREFIX, SAVE_ISOLATION_NEW_PREFIX)]
            for script_index in SAVE_ISOLATION_SCRIPT_IDS
        },
        ignore_missing_replacements=True,
    )


def patch_uifix_incremental_runtime(raw: bytes) -> bytes:
    patched = raw

    patched = _apply_startup_and_save_isolation_patches(patched)
    patched = patch_script_source(patched, 7038, DRAW_INICIO_CONTROL_SOURCE)
    patched = patch_script_source(patched, 5211, ADD_TEXT_TO_BUFFER_SOURCE)
    patched = patch_script_source(patched, 7089, DRAW_PANEL_INFORMATIVO_SOURCE)
    patched = _replace_all(
        patched,
        7013,
        'draw_text(view_xview+112,view_yview+80,str);',
        'rest=str; line_y=view_yview+80; while(true){ cut=string_pos("#",rest); if(cut>0){ line_text=string_copy(rest,1,cut-1); rest=string_delete(rest,1,cut); } else { line_text=rest; rest=""; } if(line_text!=""){ if(global.language="zh" && global.zh_text_key_map!=(-1) && !ds_map_exists(global.zh_text_key_map,line_text)){ var dash_pos, part1, part2, key1, key2, pair_key; dash_pos=string_pos(" - ",line_text); if(dash_pos>0){ part1=string_copy(line_text,1,dash_pos-1); part2=string_delete(line_text,1,dash_pos+2); if(part1!="" && part2!=""){ key1=""; key2=""; if(ds_map_exists(global.zh_text_key_map,part1))key1=ds_map_find_value(global.zh_text_key_map,part1); if(ds_map_exists(global.zh_text_key_map,part2))key2=ds_map_find_value(global.zh_text_key_map,part2); pair_key="zh__custom__pair_dash"; if(key1!="")pair_key+="__par1__"+key1; else pair_key+="__par1raw__"+part1; if(key2!="")pair_key+="__par2__"+key2; else pair_key+="__par2raw__"+part2; if(ds_map_exists(global.zh_text_key_map,line_text))ds_map_replace(global.zh_text_key_map,line_text,pair_key); else ds_map_add(global.zh_text_key_map,line_text,pair_key); }}} ex(7028,line_text,view_xview+112,line_y,c_white,fa_left,0.9); line_y+=11; } if(rest="")break; }',
    )
    patched = _replace_all(
        patched,
        7014,
        'draw_text(view_xview+464,view_yview+80,str);',
        'rest=str; line_y=view_yview+80; while(true){ cut=string_pos("#",rest); if(cut>0){ line_text=string_copy(rest,1,cut-1); rest=string_delete(rest,1,cut); } else { line_text=rest; rest=""; } if(line_text!=""){ if(global.language="zh" && global.zh_text_key_map!=(-1) && !ds_map_exists(global.zh_text_key_map,line_text)){ var dash_pos, part1, part2, key1, key2, pair_key; dash_pos=string_pos(" - ",line_text); if(dash_pos>0){ part1=string_copy(line_text,1,dash_pos-1); part2=string_delete(line_text,1,dash_pos+2); if(part1!="" && part2!=""){ key1=""; key2=""; if(ds_map_exists(global.zh_text_key_map,part1))key1=ds_map_find_value(global.zh_text_key_map,part1); if(ds_map_exists(global.zh_text_key_map,part2))key2=ds_map_find_value(global.zh_text_key_map,part2); pair_key="zh__custom__pair_dash"; if(key1!="")pair_key+="__par1__"+key1; else pair_key+="__par1raw__"+part1; if(key2!="")pair_key+="__par2__"+key2; else pair_key+="__par2raw__"+part2; if(ds_map_exists(global.zh_text_key_map,line_text))ds_map_replace(global.zh_text_key_map,line_text,pair_key); else ds_map_add(global.zh_text_key_map,line_text,pair_key); }}} ex(7028,line_text,view_xview+464,line_y,c_white,fa_right,0.9); line_y+=11; } if(rest="")break; }',
    )
    patched = _replace_all(
        patched,
        7077,
        'for(i=0;i<=3;i+=1){ ex(6901,281,30+i*16,txt_pp,0,(13160656),1);}',
        'draw_set_font((3)); for(i=0;i<=3;i+=1){ ex(6901,281,30+i*16,"PP",0,(13160656),1);}',
    )

    return patched


def build_dialog_bitmap_test_runner(source_exe: Path, output_exe: Path) -> Path:
    output_exe.write_bytes(patch_dialog_bitmap_runtime(source_exe.read_bytes()))
    return output_exe


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_exe", type=Path)
    parser.add_argument("output_exe", type=Path)
    args = parser.parse_args()
    build_dialog_bitmap_test_runner(args.source_exe, args.output_exe)
    print(args.output_exe)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
