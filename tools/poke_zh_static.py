from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, Pattern
import argparse
import json
import re
import unicodedata
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw, ImageFont

try:
    from tools.poke_text_pack import decode_display_text, decode_lines
except ModuleNotFoundError:
    from poke_text_pack import decode_display_text, decode_lines

try:
    from tools.poke_zh_render import DEFAULT_FONT_SIZE, resolve_font_path
    from tools.poke_zh_render import make_line_key, render_bitmap_text
    from tools.poke_zh_render import render_manifest as render_manifest_bitmaps
except ModuleNotFoundError:
    from poke_zh_render import DEFAULT_FONT_SIZE, make_line_key, render_bitmap_text, resolve_font_path
    from poke_zh_render import render_manifest as render_manifest_bitmaps


PLACEHOLDER_RE = re.compile(r"\$[A-Za-z0-9]+\$")
TEMPLATE_TOKEN_RE = re.compile(r"(\$par1\$|\$par2\$|\$par3\$|#)")
MEGA_STONE_REMAINDERS = {
    "ite",
    "nite",
    "inite",
    "te",
}
GOOGLE_SPLIT_TOKEN = "ZZHSPLITC0DEX12345ZZ"
GOOGLE_TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q="
POKEAPI_USER_AGENT = "Mozilla/5.0 Codex/1.0"
POKEAPI_LIMITS = {
    "pokemon-species": 2000,
    "move": 2000,
    "ability": 500,
    "item": 2000,
}
PACK_WRAP_WIDTHS: dict[str, int | None] = {
    "txt_pkmn": None,
    "txt_attack": None,
    "txt_abilities": None,
    "txt_obj": None,
    "txt_places": None,
    "txt_adjective": None,
    "txt_battle": 290,
    "txt_attack_desc": 290,
    "txt_abilities_desc": 290,
    "txt_obj_desc": 290,
    "txt_obj_secret_base": 290,
    "txt_menu": 290,
    "txt_dialog": 290,
    "txt_character": 290,
    "txt_creditos": 290,
    "txt_exam": 290,
    "txt_keyboard": 290,
    "txt_map": 290,
    "txt_medals": 290,
    "txt_quests": 290,
    "txt_cartel": 290,
    "dex_espec": None,
    "dex_info": 290,
}
EXTRA_PACK_NAMES = ("dex_espec", "dex_info")
COMPACT_NUMERIC_FONT_SIZE = 12
RAW_KEY_LABELS = (
    tuple(chr(code) for code in range(ord("A"), ord("Z") + 1))
    + tuple(str(number) for number in range(10))
    + tuple(f"F{number}" for number in range(1, 13))
)
KEY_NAME_LINE_NUMBERS = tuple(range(1545, 1609))
KEY_TEMPLATE_LINES = {
    683: "{par1}翻页",
    684: "{par1}叫声",
    685: "{par1}退出",
    686: "{par1}帮助",
    702: "可查看闪光形态（{par1}）",
    703: "普通形态（{par1}）",
    832: "按{par1}分配这个树果。",
    833: "按{par1}使用。",
}
RAW_NUMBER_TEMPLATE_SPECS = (
    ("txt_menu", 699, tuple(str(number) for number in range(1, 21)), "第{par1}页", None),
    ("txt_menu", 549, tuple(str(number) for number in range(0, 301)) + ("--",), "威:{par1}", COMPACT_NUMERIC_FONT_SIZE),
    ("txt_menu", 550, tuple(str(number) for number in range(0, 301)) + ("--",), "PP:{par1}", COMPACT_NUMERIC_FONT_SIZE),
)
PACK_TEMPLATE_SPECS = (
    ("txt_menu", 698, "dex_espec", "{par1}宝可梦"),
    ("txt_menu", 215, "txt_pkmn", "{par1}的数据已更新。"),
    ("txt_menu", 705, "txt_pkmn", "{par1}的基础数据"),
    ("txt_menu", 707, "txt_pkmn", "{par1}的升级招式"),
    ("txt_menu", 1542, "txt_attack", "进化：{par1}"),
    ("txt_menu", 795, "txt_pkmn", "离开 - {par1}"),
    ("txt_menu", 821, "txt_pkmn", "资料 - {par1}"),
    ("txt_dialog", 2639, "txt_pkmn", "你获得了{par1}。"),
    ("txt_dialog", 2639, "txt_obj", "你获得了{par1}。"),
    ("txt_dialog", 4501, "txt_obj", "你找到了{par1}。"),
    ("txt_dialog", 6834, "txt_pkmn", "这只宝可梦是{par1}。"),
    ("txt_dialog", 6837, "txt_pkmn", "你获得了{par1}。"),
    ("txt_dialog", 6837, "txt_obj", "你获得了{par1}。"),
)
PACK_PAGE_TEMPLATE_SPECS = (
    (
        "txt_dialog",
        6838,
        "txt_pkmn",
        (
            "{par1}……",
            "不错的选择！",
        ),
    ),
)
LABEL_PAIR_TEMPLATE_SPECS = (
    (
        "txt_dialog",
        1499,
        "你好，训练家。#按{par1}可以查看宝可梦资料。#按{par2}可以把它从精灵球里放出来。",
    ),
    (
        "txt_dialog",
        1513,
        "对战开始时，首位宝可梦会上场。#按{par1}选择首位宝可梦，选中后按{par2}确认。",
    ),
)
LABEL_PAGE_TEMPLATE_SPECS = (
    (
        "txt_dialog",
        2561,
        (
            "你好，训练家！我们一直在等你。",
            "昨天我给了你训练家手册，希望你已经认真看过了。",
            "按{par1}就能查看它。",
        ),
    ),
)
LABEL_PAIR_PAGE_TEMPLATE_SPECS = (
    (
        "txt_dialog",
        6841,
        (
            "随身带上一些总是很重要。",
            "有了它们，你就能捕捉野生宝可梦。",
            "对战中，按{par1}就能把它们投出去。",
            "抓到宝可梦后，按{par2}就能在图鉴里查看信息。",
        ),
    ),
)
RAW_LABEL_TEMPLATE_SPECS = (
    ("txt_obj_desc", 170, "地图。#按{par1}使用。"),
)
NICKNAME_GENDER_LINE_NUMBERS = (224, 226)
BALL_PROMPT_DESC_LINES = tuple(range(178, 271))
PAGE_TEMPLATE_SPECS = (
    ("txt_dialog", 6841, 3, "par1", "对战时，按{label}投出它们。"),
    ("txt_dialog", 6841, 4, "par2", "如果你捕捉到宝可梦，按{label}打开图鉴查看信息。"),
)
DYNAMIC_BITMAP_TEXTS = [
    (f"zh__txt_dialog__5__slot__{slot}", f"已分配槽位 {slot}#按 Z 继续。")
    for slot in range(1, 100)
]
CUSTOM_LAYOUT_SPECS = (
    (
        "zh__custom__pair_dash",
        "w0|par1|seg1|par2",
        (
            ("seg__1", " - "),
        ),
    ),
)
SOURCE_OVERRIDES = {
    "New game": "新游戏",
    "ZH LOAD": "读取存档",
    "Exit game": "退出游戏",
    "Exit game?#All unsaved data will be lost.": "退出游戏？#所有未保存的数据将丢失。",
    "Restart game?#All unsaved data will be lost.": "重新开始游戏？#所有未保存的数据将丢失。",
    "Load file?#All unsaved data will be lost.": "读取存档？#所有未保存的数据将丢失。",
    "No Save File found!": "未找到存档文件！",
    "Hello, $prota$!": "你好，训练家！",
    "For example, these Pokémon are $par1$, $par2$ and $par3$.": "例如，这些宝可梦是伊布、皮卡丘和利欧路。",
    "Hello, $prota$!@How are you with the Pokédex?@Pokémon Seen... $par1$.@Pokémon Caught... $par2$.": "你好，训练家！#你的图鉴进展如何？#已见到的宝可梦。#已捕获的宝可梦。",
    "$par1$'s mom": "$par1$的妈妈",
    "Yes (&Z)": "是（Z）",
    "No (&X)": "否（X）",
    "OK (&Z)": "确定（Z）",
    "Select game screen scaling mode...": "选择游戏画面缩放模式...",
    "Max scale": "最大缩放",
    "Adjust to screen": "适应屏幕",
    "Scale 1x1": "缩放 1x1",
    "Scale 2x2": "缩放 2x2",
    "Turn off Game Sounds?": "关闭游戏音效？",
    "Turn on Game Sounds?": "开启游戏音效？",
    "Turn off Game Music?": "关闭游戏音乐？",
    "Turn on Game Music?": "开启游戏音乐？",
    "Not available.": "不可用。",
    "INFO.": "信息",
    "AREA": "地区",
    "EVOL.": "进化",
    "MOV.": "招式",
    "STATS": "能力",
    "ADD.": "附加",
    "Pokémon Info.": "宝可梦资料",
    "Pokémon Abil.": "宝可梦特性",
    "Battle Moves": "战斗招式",
    "Mouse": "鼠",
    "Key Items": "重要道具",
    "Level": "等级",
    "Lv $par1$": "等级$par1$",
    "A map. Press $par1$ to use it.": "地图。#按$par1$使用。",
    "A cellphone. Press $par1$ to use it.": "手机。#按$par1$使用。",
    "A rod used for fishing Pokémon. Press $par1$ to use it.": "用于钓宝可梦的钓竿。#按$par1$使用。",
    "A better rod used for fishing Pokémon. Press $par1$ to use it.": "更好的钓竿，可用来钓宝可梦。#按$par1$使用。",
    "The best rod used for fishing Pokémon. Press $par1$ to use it.": "最好的钓竿，可用来钓宝可梦。#按$par1$使用。",
    "Ride it to go even faster than with your Running Shoes. Press $par1$ to use it.": "骑上它会比跑鞋更快。#按$par1$使用。",
    "It lets you listen to the Star Region's music. Press $par1$ to use it.": "它能播放星区的音乐。#按$par1$使用。",
    "A flute that awakens sleeping Pokémon. Press $par1$ to use it during a battle.": "能唤醒睡眠宝可梦的笛子。#对战中按$par1$使用。",
    "Restores PP in battle. Press $par1$ to assign.": "对战中恢复PP。#按$par1$分配。",
    "Boosts Attack in battle. Press $par1$ to assign.": "对战中提升攻击。#按$par1$分配。",
    "Boosts Defense in battle. Press $par1$ to assign.": "对战中提升防御。#按$par1$分配。",
    "Remember, you can use the Phone by pressing $par1$!": "记住，按$par1$就能使用手机！",
    "$par1$ used $par2$.": "$par1$使用了$par2$。",
    "$par1$ has hit $par2$.": "$par1$击中了$par2$。",
    "Do you want to throw $par1$ to $par2$?#You have $par3$ units left.": "要对$par2$投出$par1$吗？#你还剩$par3$个。",
    "Do you want to throw $par1$ to $par2$?#You have one unit left.": "要对$par2$投出$par1$吗？#你还剩1个。",
    "#$par1$ Pokémon's number: $par2$.": "#$par1$的宝可梦数量：$par2$。",
    "#Health percentage: $par1$%": "#体力百分比：$par1$%",
    "#Pokémon with status condition: $par1$": "#处于异常状态的宝可梦：$par1$",
    "#Opponent Pokémon's number: $par1$": "#对手的宝可梦数量：$par1$",
    "Press $par1$ to assign this berry.": "按$par1$分配这个树果。",
    "Press $par1$ to use it.": "按$par1$使用。",
    "BP: $par1$": "威:$par1$",
    "PP: $par1$": "PP:$par1$",
    "Evol: $par1$": "进化：$par1$",
    " (Male)": "（雄性）",
    " (Female)": "（雌性）",
    "Type A": "属性1",
    "Type B": "属性2",
    "Stats": "能力",
    "ATTACK": "攻击",
    "DEFENSE": "防御",
    "SP. AT.": "特攻",
    "SP. DEF.": "特防",
    "SPEED": "速度",
    "Experience": "经验",
    "Exp. Points": "经验值",
    "Next Lv": "下一级",
    "Exp.": "经验",
    "Stats detail": "能力详情",
    "Instruction Values": "努力值",
    "Natural Talents Values": "个体值",
    "HP:#PP:#Attack:#Defense:#Special At.:#Special Def.:#Speed:#Total:": "HP:#PP:#攻击:#防御:#特攻:#特防:#速度:#总量:",
    "HP:#Attack:#Defense:#Special At.:#Special Def.:#Speed:#Total:": "HP:#攻击:#防御:#特攻:#特防:#速度:#总量:",
    "Health points (HP):#Attack:#Defense:#Spec. Atk.:#Spec. Def.:#Speed:": "HP值:#攻击:#防御:#特攻:#特防:#速度:",
    "Time: ": "时间：",
    "Physical": "物理",
    "Special": "特殊",
    "Status": "变化",
    "None": "无",
    "Normal": "一般",
    "Fire": "火",
    "Water": "水",
    "Grass": "草",
    "Electric": "电",
    "Rock": "岩石",
    "Fighting": "格斗",
    "Ground": "地面",
    "Psychic": "超能力",
    "Poison": "毒",
    "Bug": "虫",
    "Ice": "冰",
    "Dark": "恶",
    "Steel": "钢",
    "Flying": "飞行",
    "Ghost": "幽灵",
    "Dragon": "龙",
    "Fairy": "妖精",
    "Random": "随机",
    "HP": "HP",
    "PP": "PP",
    "Pokémon Center": "宝可梦中心",
    "Pokémon Shop": "宝可梦商店",
    "Pokémon Contest": "宝可梦华丽大赛",
    "Pokémon Tower": "宝可梦塔",
    "Pokémon League": "宝可梦联盟",
    "Home": "家",
    "Oak Lab": "大木研究所",
    "Rowan Lab": "山梨研究所",
}
BASE_GLOSSARY = [
    ("Pokémon", "宝可梦"),
    ("Pokemon", "宝可梦"),
    ("Pokédex", "宝可梦图鉴"),
    ("Pokedex", "宝可梦图鉴"),
    ("the trainer", "训练家"),
    ("the rival", "对手"),
    ("trainer", "训练家"),
    ("rival", "对手"),
    ("Kanto", "关都"),
    ("Johto", "城都"),
    ("Hoenn", "丰缘"),
    ("Sinnoh", "神奥"),
    ("Unova", "合众"),
    ("Kalos", "卡洛斯"),
    ("Alola", "阿罗拉"),
    ("Galar", "伽勒尔"),
    ("Paldea", "帕底亚"),
    ("Hisui", "洗翠"),
    ("Mega-Ring", "超级环"),
    ("Mega", "超级"),
    ("Gigamax", "超极巨化"),
    ("HP", "HP"),
    ("PP", "PP"),
    ("BP", "BP"),
]
NAME_PLACEHOLDER_REPLACEMENTS = {
    "$prota$": "the trainer",
    "$rival$": "the rival",
}
PARAM_PLACEHOLDER_TOKENS = {
    "$par1$": "ZZHPAR1TOKENZZ",
    "$par2$": "ZZHPAR2TOKENZZ",
    "$par3$": "ZZHPAR3TOKENZZ",
}
PARAM_PLACEHOLDER_NAMES = {
    "$par1$": "par1",
    "$par2$": "par2",
    "$par3$": "par3",
}


def is_static_renderable(text: str) -> bool:
    return bool(text.strip()) and _static_translation_source(text) is not None


def _static_translation_source(text: str) -> str | None:
    if not text.strip():
        return None
    if PLACEHOLDER_RE.search(text) is None:
        return text
    if text in SOURCE_OVERRIDES:
        return text

    placeholders = set(PLACEHOLDER_RE.findall(text))
    if placeholders <= set(NAME_PLACEHOLDER_REPLACEMENTS):
        normalized = text
        for token, replacement in NAME_PLACEHOLDER_REPLACEMENTS.items():
            normalized = normalized.replace(token, replacement)
        return re.sub(r"\s{2,}", " ", normalized).strip()
    return None


def _template_translation_source(text: str) -> str | None:
    if not text.strip():
        return None
    placeholders = set(PLACEHOLDER_RE.findall(text))
    if not placeholders or not placeholders <= set(PARAM_PLACEHOLDER_TOKENS):
        return None
    normalized = text
    for placeholder, token in PARAM_PLACEHOLDER_TOKENS.items():
        normalized = normalized.replace(placeholder, token)
    return normalized


def _restore_template_placeholders(text: str) -> str:
    restored = text
    for placeholder, token in PARAM_PLACEHOLDER_TOKENS.items():
        restored = restored.replace(token, placeholder)
    return restored


def make_page_key(folder: str, filename: str, line_number: int, page_number: int) -> str:
    return f"{make_line_key(folder, filename, line_number)}__page__{page_number}"


def _term_pattern(term: str) -> str:
    escaped = re.escape(term)
    prefix = r"(?<![A-Za-z0-9])" if term[:1].isalnum() else ""
    suffix = r"(?![A-Za-z0-9])" if term[-1:].isalnum() else ""
    return f"{prefix}{escaped}{suffix}"


def build_term_regex(glossary: list[tuple[str, str]]) -> Pattern[str]:
    ordered_terms = sorted({source for source, _ in glossary if source}, key=len, reverse=True)
    return re.compile("|".join(_term_pattern(term) for term in ordered_terms))


def mask_known_terms(
    text: str,
    glossary: list[tuple[str, str]],
    term_regex: Pattern[str],
) -> tuple[str, dict[str, str]]:
    replacements_by_source = dict(glossary)
    replacements: dict[str, str] = {}

    def replace(match: re.Match[str]) -> str:
        token = f"ZZHTERM{len(replacements):04d}ZZ"
        replacements[token] = replacements_by_source[match.group(0)]
        return token

    return term_regex.sub(replace, text), replacements


def unmask_known_terms(text: str, replacements: dict[str, str]) -> str:
    restored = text
    for token, value in replacements.items():
        restored = restored.replace(token, value)
    return restored


def _normalize_lookup_key(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    return "".join(character for character in ascii_only.lower() if character.isalnum())


def _measure_width(text: str, font: ImageFont.FreeTypeFont) -> int:
    probe = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    draw = ImageDraw.Draw(probe)
    bbox = draw.textbbox((0, 0), text or " ", font=font)
    return bbox[2] - bbox[0]


def wrap_text_to_width(
    text: str,
    max_width: int,
    *,
    font_path: Path | None = None,
    font_size: int = DEFAULT_FONT_SIZE,
) -> str:
    if max_width <= 0:
        return text

    font = ImageFont.truetype(str(resolve_font_path(font_path)), font_size)
    wrapped_lines: list[str] = []
    for raw_line in text.split("#"):
        if not raw_line:
            wrapped_lines.append("")
            continue
        current = ""
        for character in raw_line:
            candidate = current + character
            if current and _measure_width(candidate, font) > max_width:
                wrapped_lines.append(current)
                current = character
            else:
                current = candidate
        wrapped_lines.append(current)
    return "#".join(wrapped_lines)


def translate_pokemon_name(name: str, species_map: dict[str, str]) -> str | None:
    if name in species_map:
        return species_map[name]

    if name.startswith("Mega "):
        remainder = name[5:]
        suffix = ""
        if remainder.endswith(" X") or remainder.endswith(" Y"):
            suffix = remainder[-1]
            remainder = remainder[:-2]
        translated_base = species_map.get(remainder)
        if translated_base is None:
            return None
        return f"超级{translated_base}{suffix}"

    if name.endswith(" Gigamax"):
        base_name = name[: -len(" Gigamax")]
        translated_base = species_map.get(base_name)
        if translated_base is None:
            return None
        return f"{translated_base} 超极巨化"

    return None


def translate_item_name(
    name: str,
    item_map: dict[str, str],
    species_map: dict[str, str],
) -> str | None:
    exact = item_map.get(name)
    if exact is not None:
        return exact

    suffix_letter = ""
    base_name = name
    suffix_match = re.match(r"^(.*?)(?:\s+([A-Z]))?$", name)
    if suffix_match is not None and suffix_match.group(2) in {"X", "Y", "Z"}:
        base_name = suffix_match.group(1)
        suffix_letter = suffix_match.group(2) or ""

    normalized_item = _normalize_lookup_key(base_name)
    best_match: tuple[int, str] | None = None
    for species_name, translated_species_name in species_map.items():
        normalized_species = _normalize_lookup_key(species_name)
        if not normalized_item.startswith(normalized_species):
            continue
        remainder = normalized_item[len(normalized_species) :]
        if remainder not in MEGA_STONE_REMAINDERS:
            continue
        score = len(normalized_species)
        if best_match is None or score > best_match[0]:
            best_match = (score, translated_species_name)

    if best_match is None:
        return None

    return f"{best_match[1]}进化石{suffix_letter}"


def translate_place_name(name: str) -> str | None:
    route_match = re.fullmatch(r"Route (\d+)", name)
    if route_match is not None:
        return f"{route_match.group(1)}号道路"

    floor_map = {
        "(Upper Floor)": "（上层）",
        "(Middle Floor)": "（中层）",
        "(Lower Floor)": "（下层）",
    }
    if name in floor_map:
        return floor_map[name]

    return SOURCE_OVERRIDES.get(name)


def build_static_manifest_entries(
    folder: str,
    filename: str,
    lines: list[str],
    translate_line: Callable[[str], str],
    *,
    max_width: int | None = None,
    font_path: Path | None = None,
    font_size: int = DEFAULT_FONT_SIZE,
) -> list[dict[str, str | int]]:
    entries: list[dict[str, str | int]] = []
    for index, line in enumerate(lines, start=1):
        if not is_static_renderable(line):
            continue
        translated = translate_line(line)
        if not translated.strip():
            continue
        if max_width is not None:
            translated = wrap_text_to_width(
                translated,
                max_width,
                font_path=font_path,
                font_size=font_size,
            )
        entries.append(
            {
                "folder": folder,
                "filename": filename,
                "line": index,
                "text": translated,
            }
        )
    return entries


def build_page_manifest_entries(
    folder: str,
    filename: str,
    lines: list[str],
    translate_line: Callable[[str], str],
    *,
    max_width: int | None = None,
    font_path: Path | None = None,
    font_size: int = DEFAULT_FONT_SIZE,
) -> list[dict[str, str | int]]:
    entries: list[dict[str, str | int]] = []
    for index, line in enumerate(lines, start=1):
        pages = line.split("@")
        if len(pages) <= 1:
            continue
        for page_number, page_text in enumerate(pages, start=1):
            translation_source = _static_translation_source(page_text)
            if translation_source is None:
                continue
            translated = translate_line(page_text)
            if not translated.strip():
                continue
            if max_width is not None:
                translated = wrap_text_to_width(
                    translated,
                    max_width,
                    font_path=font_path,
                    font_size=font_size,
                )
            entries.append(
                {
                    "folder": folder,
                    "filename": filename,
                    "line": index,
                    "key": make_page_key(folder, filename, index, page_number),
                    "text": translated,
                }
            )
    return entries


def _load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def _decode_pack(path: Path) -> list[str]:
    return [decode_display_text(line) for line in decode_lines(path.read_bytes())]


def _fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": POKEAPI_USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def _fetch_pokeapi_resource_name_map(resource: str, cache_path: Path) -> dict[str, str]:
    cached = _load_json(cache_path, None)
    if cached:
        return cached

    listing = _fetch_json(f"https://pokeapi.co/api/v2/{resource}?limit={POKEAPI_LIMITS[resource]}")
    mapping: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(_fetch_json, entry["url"]): entry["url"] for entry in listing["results"]}
        for future in as_completed(futures):
            payload = future.result()
            names = payload.get("names", [])
            english = next((item["name"] for item in names if item["language"]["name"] == "en"), None)
            chinese = next((item["name"] for item in names if item["language"]["name"] == "zh-hans"), None)
            if english and chinese:
                mapping[english] = chinese

    sorted_mapping = dict(sorted(mapping.items()))
    _write_json(cache_path, sorted_mapping)
    return sorted_mapping


def _translate_google_payload(payload: str) -> str:
    url = GOOGLE_TRANSLATE_URL + urllib.parse.quote(payload)
    request = urllib.request.Request(url, headers={"User-Agent": POKEAPI_USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
    return "".join(chunk[0] for chunk in data[0])


def _normalize_translation(text: str) -> str:
    normalized = text.replace("@", "#")
    normalized = normalized.replace("神奇宝贝", "宝可梦")
    normalized = normalized.replace("口袋妖怪", "宝可梦")
    normalized = normalized.replace("精灵宝可梦", "宝可梦")
    normalized = normalized.replace("动作", "招式")
    normalized = normalized.replace("宝可梦图鉴图鉴", "宝可梦图鉴")
    normalized = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", normalized)
    normalized = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[#，。！？：；）])", "", normalized)
    normalized = re.sub(r"(?<=[（#])\s+(?=[\u4e00-\u9fff])", "", normalized)
    return normalized


def _translate_google_batch(
    texts: list[str],
    glossary: list[tuple[str, str]],
    term_regex: Pattern[str],
) -> list[str]:
    masked_texts: list[str] = []
    replacement_maps: list[dict[str, str]] = []
    for text in texts:
        masked, replacements = mask_known_terms(text, glossary, term_regex)
        masked_texts.append(masked)
        replacement_maps.append(replacements)

    payload = f"\n{GOOGLE_SPLIT_TOKEN}\n".join(masked_texts)
    translated_payload = _translate_google_payload(payload)
    raw_parts = translated_payload.split(GOOGLE_SPLIT_TOKEN)
    parts = [part.strip("\r\n") for part in raw_parts]
    if len(parts) != len(texts):
        raise ValueError(f"split mismatch: expected {len(texts)} parts, got {len(parts)}")

    restored: list[str] = []
    for part, replacements in zip(parts, replacement_maps):
        restored.append(_normalize_translation(unmask_known_terms(part, replacements)))
    return restored


def _iter_translation_batches(texts: list[str], *, max_items: int = 40, max_chars: int = 2400) -> list[list[str]]:
    batches: list[list[str]] = []
    current: list[str] = []
    current_chars = 0
    token_chars = len(GOOGLE_SPLIT_TOKEN) + 2

    for text in texts:
        addition = len(text) + (token_chars if current else 0)
        if current and (len(current) >= max_items or current_chars + addition > max_chars):
            batches.append(current)
            current = [text]
            current_chars = len(text)
            continue
        current.append(text)
        current_chars += addition

    if current:
        batches.append(current)
    return batches


def _translate_texts_with_cache(
    texts: list[str],
    cache_path: Path,
    glossary: list[tuple[str, str]],
) -> dict[str, str]:
    cache = _load_json(cache_path, {})
    unique_texts = list(dict.fromkeys(texts))
    pending = [text for text in unique_texts if text not in cache]
    term_regex = build_term_regex(glossary)

    for batch in _iter_translation_batches(pending):
        try:
            translated_batch = _translate_google_batch(batch, glossary, term_regex)
        except Exception:
            translated_batch = []
            for text in batch:
                translated_batch.extend(_translate_google_batch([text], glossary, term_regex))
        for source_text, translated_text in zip(batch, translated_batch):
            cache[source_text] = translated_text
        _write_json(cache_path, cache)

    return {text: cache[text] for text in texts}


def _build_glossary(
    species_map: dict[str, str],
    move_map: dict[str, str],
    ability_map: dict[str, str],
    item_map: dict[str, str],
) -> list[tuple[str, str]]:
    glossary = list(BASE_GLOSSARY)
    glossary.extend((source, target) for source, target in SOURCE_OVERRIDES.items() if len(source) > 2)
    glossary.extend(species_map.items())
    glossary.extend(move_map.items())
    glossary.extend(ability_map.items())
    glossary.extend(item_map.items())
    return glossary


def _translate_name_pack_line(
    filename: str,
    text: str,
    species_map: dict[str, str],
    move_map: dict[str, str],
    ability_map: dict[str, str],
    item_map: dict[str, str],
) -> str | None:
    if text in SOURCE_OVERRIDES:
        return SOURCE_OVERRIDES[text]
    if filename == "txt_pkmn":
        return translate_pokemon_name(text, species_map) or species_map.get(text)
    if filename == "txt_attack":
        return move_map.get(text)
    if filename == "txt_abilities":
        return ability_map.get(text)
    if filename == "txt_obj":
        return translate_item_name(text, item_map, species_map) or item_map.get(text)
    if filename == "txt_places":
        return translate_place_name(text)
    return None


def _dynamic_key_entry(
    folder: str,
    filename: str,
    line: int,
    key: str,
    text: str,
    *,
    font_size: int | None = None,
) -> dict[str, str | int]:
    entry: dict[str, str | int] = {
        "folder": folder,
        "filename": filename,
        "line": line,
        "key": key,
        "text": text,
    }
    if font_size is not None:
        entry["font_size"] = font_size
    return entry


def build_dynamic_layout_assets(
    folder: str,
    source_pack_lines: dict[str, list[str]],
    translate_template: Callable[[str, str], str | None],
) -> tuple[list[dict[str, str | int]], dict[str, str]]:
    entries: list[dict[str, str | int]] = []
    layouts: dict[str, str] = {}

    for filename, lines in source_pack_lines.items():
        wrap_width = PACK_WRAP_WIDTHS.get(filename, 290) or 0
        for line_number, line in enumerate(lines, start=1):
            pages = line.split("@")
            for page_number, page_text in enumerate(pages, start=1):
                if _template_translation_source(page_text) is None:
                    continue
                translated = translate_template(filename, page_text)
                if not translated:
                    continue
                parts = [part for part in TEMPLATE_TOKEN_RE.split(translated) if part]
                if not any(part in PARAM_PLACEHOLDER_NAMES for part in parts):
                    continue

                base_key = (
                    make_page_key(folder, filename, line_number, page_number)
                    if len(pages) > 1
                    else make_line_key(folder, filename, line_number)
                )
                layout_tokens = [f"w{wrap_width}"]
                segment_index = 0

                for part in parts:
                    if part == "#":
                        layout_tokens.append("br")
                        continue
                    if part in PARAM_PLACEHOLDER_NAMES:
                        layout_tokens.append(PARAM_PLACEHOLDER_NAMES[part])
                        continue
                    if not part:
                        continue
                    segment_index += 1
                    segment_key = f"{base_key}__seg__{segment_index}"
                    entries.append(_dynamic_key_entry(folder, filename, line_number, segment_key, part))
                    layout_tokens.append(f"seg{segment_index}")

                layouts[base_key] = "|".join(layout_tokens)

    for base_key, layout, segments in CUSTOM_LAYOUT_SPECS:
        layouts[base_key] = layout
        for segment_name, segment_text in segments:
            entries.append(
                _dynamic_key_entry(
                    folder,
                    "txt_battle",
                    0,
                    f"{base_key}__{segment_name}",
                    segment_text,
                )
            )

    return entries, layouts


def write_dynamic_layout_files(layouts: dict[str, str], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for key, layout in layouts.items():
        (output_dir / f"{key}__layout.txt").write_text(layout, encoding="ascii")


def _build_label_sources(translated_pack_lines: dict[str, list[str]]) -> list[tuple[str, str]]:
    menu_lines = translated_pack_lines.get("txt_menu", [])
    label_sources: list[tuple[str, str]] = [(raw_label, raw_label) for raw_label in RAW_KEY_LABELS]

    for line_number in KEY_NAME_LINE_NUMBERS:
        if 0 < line_number <= len(menu_lines):
            label = menu_lines[line_number - 1].strip()
            if label:
                label_sources.append((label, make_line_key("zh", "txt_menu", line_number)))
    return label_sources


def _build_key_label_entries(translated_pack_lines: dict[str, list[str]]) -> list[dict[str, str | int]]:
    entries: list[dict[str, str | int]] = []
    label_sources = _build_label_sources(translated_pack_lines)

    for line_number, template in KEY_TEMPLATE_LINES.items():
        base_key = make_line_key("zh", "txt_menu", line_number)
        for label, label_key in label_sources:
            if label_key == label:
                key = f"{base_key}__par1raw__{label}"
            else:
                key = f"{base_key}__par1__{label_key}"
            entries.append(_dynamic_key_entry("zh", "txt_menu", line_number, key, template.format(par1=label)))

    for filename, line_number, values, template, entry_font_size in RAW_NUMBER_TEMPLATE_SPECS:
        for value in values:
            entries.append(
                _dynamic_key_entry(
                    "zh",
                    filename,
                    line_number,
                    f"{make_line_key('zh', filename, line_number)}__par1raw__{value}",
                    template.format(par1=value),
                    font_size=entry_font_size,
                )
            )

    for filename, line_number, template in RAW_LABEL_TEMPLATE_SPECS:
        base_key = make_line_key("zh", filename, line_number)
        for label, label_key in label_sources:
            if label_key == label:
                key = f"{base_key}__par1raw__{label}"
            else:
                key = f"{base_key}__par1__{label_key}"
            entries.append(_dynamic_key_entry("zh", filename, line_number, key, template.format(par1=label)))

    return entries


def _build_ball_prompt_entries(
    translated_pack_lines: dict[str, list[str]],
    *,
    font_path: Path | None = None,
    font_size: int = DEFAULT_FONT_SIZE,
) -> list[dict[str, str | int]]:
    entries: list[dict[str, str | int]] = []
    label_sources = _build_label_sources(translated_pack_lines)
    desc_lines = translated_pack_lines.get("txt_obj_desc", [])
    use_base_key = make_line_key("zh", "txt_menu", 831)
    assign_base_key = make_line_key("zh", "txt_menu", 1178)

    for line_number in BALL_PROMPT_DESC_LINES:
        if not (0 < line_number <= len(desc_lines)):
            continue
        desc_text = desc_lines[line_number - 1].strip()
        if not desc_text:
            continue
        desc_key = make_line_key("zh", "txt_obj_desc", line_number)
        for label, label_key in label_sources:
            if label_key == label:
                param2_suffix = f"__par2raw__{label}"
            else:
                param2_suffix = f"__par2__{label_key}"
            use_text = wrap_text_to_width(
                f"{desc_text}#按{label}使用。",
                302,
                font_path=font_path,
                font_size=font_size,
            )
            assign_text = wrap_text_to_width(
                f"{desc_text}#按{label}分配这个道具。",
                222,
                font_path=font_path,
                font_size=font_size,
            )
            entries.append(
                _dynamic_key_entry(
                    "zh",
                    "txt_menu",
                    831,
                    f"{use_base_key}__par1__{desc_key}{param2_suffix}",
                    use_text,
                )
            )
            entries.append(
                _dynamic_key_entry(
                    "zh",
                    "txt_menu",
                    1178,
                    f"{assign_base_key}{param2_suffix}__par1__{desc_key}",
                    assign_text,
                )
            )

    return entries


def _build_pack_template_entries(translated_pack_lines: dict[str, list[str]]) -> list[dict[str, str | int]]:
    entries: list[dict[str, str | int]] = []
    for filename, line_number, param_pack, template in PACK_TEMPLATE_SPECS:
        base_key = make_line_key("zh", filename, line_number)
        source_lines = translated_pack_lines.get(param_pack, [])
        for param_line, param_text in enumerate(source_lines, start=1):
            if not param_text.strip():
                continue
            entries.append(
                _dynamic_key_entry(
                    "zh",
                    filename,
                    line_number,
                    f"{base_key}__par1__{make_line_key('zh', param_pack, param_line)}",
                    template.format(par1=param_text),
                )
            )
    return entries


def _build_pack_page_template_entries(translated_pack_lines: dict[str, list[str]]) -> list[dict[str, str | int]]:
    entries: list[dict[str, str | int]] = []
    for filename, line_number, param_pack, page_templates in PACK_PAGE_TEMPLATE_SPECS:
        base_key = make_line_key("zh", filename, line_number)
        source_lines = translated_pack_lines.get(param_pack, [])
        for param_line, param_text in enumerate(source_lines, start=1):
            if not param_text.strip():
                continue
            key_base = f"{base_key}__par1__{make_line_key('zh', param_pack, param_line)}"
            for page_number, template in enumerate(page_templates, start=1):
                entries.append(
                    _dynamic_key_entry(
                        "zh",
                        filename,
                        line_number,
                        f"{key_base}__page__{page_number}",
                        template.format(par1=param_text),
                    )
                )
    return entries


def _param_suffix(param_name: str, label: str, label_key: str) -> str:
    if label_key == label:
        return f"__{param_name}raw__{label}"
    return f"__{param_name}__{label_key}"


def _build_label_pair_template_entries(translated_pack_lines: dict[str, list[str]]) -> list[dict[str, str | int]]:
    entries: list[dict[str, str | int]] = []
    label_sources = _build_label_sources(translated_pack_lines)
    for filename, line_number, template in LABEL_PAIR_TEMPLATE_SPECS:
        base_key = make_line_key("zh", filename, line_number)
        for par1_label, par1_key in label_sources:
            par1_suffix = _param_suffix("par1", par1_label, par1_key)
            for par2_label, par2_key in label_sources:
                key = f"{base_key}{par1_suffix}{_param_suffix('par2', par2_label, par2_key)}"
                entries.append(
                    _dynamic_key_entry(
                        "zh",
                        filename,
                        line_number,
                        key,
                        template.format(par1=par1_label, par2=par2_label),
                    )
                )
    return entries


def _build_label_page_template_entries(translated_pack_lines: dict[str, list[str]]) -> list[dict[str, str | int]]:
    entries: list[dict[str, str | int]] = []
    label_sources = _build_label_sources(translated_pack_lines)
    for filename, line_number, page_templates in LABEL_PAGE_TEMPLATE_SPECS:
        base_key = make_line_key("zh", filename, line_number)
        for par1_label, par1_key in label_sources:
            key_base = f"{base_key}{_param_suffix('par1', par1_label, par1_key)}"
            for page_number, template in enumerate(page_templates, start=1):
                entries.append(
                    _dynamic_key_entry(
                        "zh",
                        filename,
                        line_number,
                        f"{key_base}__page__{page_number}",
                        template.format(par1=par1_label),
                    )
                )
    return entries


def _build_label_pair_page_template_entries(translated_pack_lines: dict[str, list[str]]) -> list[dict[str, str | int]]:
    entries: list[dict[str, str | int]] = []
    label_sources = _build_label_sources(translated_pack_lines)
    for filename, line_number, page_templates in LABEL_PAIR_PAGE_TEMPLATE_SPECS:
        base_key = make_line_key("zh", filename, line_number)
        for par1_label, par1_key in label_sources:
            par1_suffix = _param_suffix("par1", par1_label, par1_key)
            for par2_label, par2_key in label_sources:
                key_base = f"{base_key}{par1_suffix}{_param_suffix('par2', par2_label, par2_key)}"
                for page_number, template in enumerate(page_templates, start=1):
                    entries.append(
                        _dynamic_key_entry(
                            "zh",
                            filename,
                            line_number,
                            f"{key_base}__page__{page_number}",
                            template.format(par1=par1_label, par2=par2_label),
                        )
                    )
    return entries


def _build_nickname_prompt_entries(translated_pack_lines: dict[str, list[str]]) -> list[dict[str, str | int]]:
    entries: list[dict[str, str | int]] = []
    base_key = make_line_key("zh", "txt_menu", 220)
    pokemon_lines = translated_pack_lines.get("txt_pkmn", [])
    menu_lines = translated_pack_lines.get("txt_menu", [])
    gender_sources: list[tuple[str, str]] = []
    for line_number in NICKNAME_GENDER_LINE_NUMBERS:
        if 0 < line_number <= len(menu_lines):
            gender_text = menu_lines[line_number - 1].strip()
            if gender_text:
                gender_sources.append((gender_text, make_line_key("zh", "txt_menu", line_number)))

    for pokemon_line, pokemon_name in enumerate(pokemon_lines, start=1):
        if not pokemon_name.strip():
            continue
        pokemon_key = make_line_key("zh", "txt_pkmn", pokemon_line)
        for gender_text, gender_key in gender_sources:
            key = f"{base_key}__par1__{pokemon_key}__par2__{gender_key}"
            entries.append(
                _dynamic_key_entry(
                    "zh",
                    "txt_menu",
                    220,
                    key,
                    f"要给{pokemon_name}{gender_text}取昵称吗？",
                )
            )
    return entries


def _build_page_template_entries(translated_pack_lines: dict[str, list[str]]) -> list[dict[str, str | int]]:
    entries: list[dict[str, str | int]] = []
    label_sources = _build_label_sources(translated_pack_lines)

    for filename, line_number, page_number, param_name, template in PAGE_TEMPLATE_SPECS:
        base_key = f"{make_line_key('zh', filename, line_number)}__page__{page_number}"
        for label, label_key in label_sources:
            if label_key == label:
                key = f"{base_key}__{param_name}raw__{label}"
            else:
                key = f"{base_key}__{param_name}__{label_key}"
            entries.append(_dynamic_key_entry("zh", filename, line_number, key, template.format(label=label)))

    return entries


def _split_dex_info_pages(text: str) -> list[str]:
    if text.count("#") < 3:
        return [text]

    split_pos = -1
    line_breaks = 0
    for index, char in enumerate(text):
        if char == "#":
            line_breaks += 1
            if line_breaks == 3:
                split_pos = index
                break

    if split_pos == -1:
        return [text]

    first_page = text[:split_pos]
    second_page = text[split_pos + 1 :]
    return [page for page in (first_page, second_page) if page]


def _build_dex_info_page_entries(
    translated_pack_lines: dict[str, list[str]],
    *,
    font_path: Path | None = None,
    font_size: int = DEFAULT_FONT_SIZE,
) -> list[dict[str, str | int]]:
    entries: list[dict[str, str | int]] = []
    wrap_width = PACK_WRAP_WIDTHS["dex_info"]
    for line_number, text in enumerate(translated_pack_lines.get("dex_info", []), start=1):
        if not text.strip():
            continue
        wrapped_text = wrap_text_to_width(text, wrap_width, font_path=font_path, font_size=font_size) if wrap_width else text
        for page_number, page_text in enumerate(_split_dex_info_pages(wrapped_text), start=1):
            entries.append(
                _dynamic_key_entry(
                    "zh",
                    "dex_info",
                    line_number,
                    f"{make_line_key('zh', 'dex_info', line_number)}__page__{page_number}",
                    page_text,
                )
            )
    return entries


def build_dynamic_manifest_entries(
    translated_pack_lines: dict[str, list[str]],
    *,
    font_path: Path | None = None,
    font_size: int = DEFAULT_FONT_SIZE,
) -> list[dict[str, str | int]]:
    entries = [
        _dynamic_key_entry(
            "zh",
            "txt_dialog",
            5,
            f"zh__txt_dialog__5__slot__{slot}",
            f"已分配槽位 {slot}#按 Z 继续。",
        )
        for slot in range(1, 100)
    ]
    entries.extend(_build_key_label_entries(translated_pack_lines))
    entries.extend(_build_ball_prompt_entries(translated_pack_lines, font_path=font_path, font_size=font_size))
    entries.extend(_build_dex_info_page_entries(translated_pack_lines, font_path=font_path, font_size=font_size))
    entries.extend(_build_pack_template_entries(translated_pack_lines))
    entries.extend(_build_pack_page_template_entries(translated_pack_lines))
    entries.extend(_build_label_pair_template_entries(translated_pack_lines))
    entries.extend(_build_label_page_template_entries(translated_pack_lines))
    entries.extend(_build_label_pair_page_template_entries(translated_pack_lines))
    entries.extend(_build_nickname_prompt_entries(translated_pack_lines))
    entries.extend(_build_page_template_entries(translated_pack_lines))
    return entries


def build_render_manifest(
    root: Path,
    manifest_path: Path,
    cache_dir: Path,
    *,
    layout_dir: Path | None = None,
    font_path: Path | None = None,
    font_size: int = DEFAULT_FONT_SIZE,
) -> list[dict[str, str | int]]:
    text_root = root / "data" / "text" / "en"
    layout_dir = layout_dir or (root / "data" / "text" / "zh" / "render")
    pokeapi_cache_dir = cache_dir / "pokeapi"
    google_cache_path = cache_dir / "google_static_cache.json"

    species_map = _fetch_pokeapi_resource_name_map("pokemon-species", pokeapi_cache_dir / "pokemon-species.zh-hans.json")
    move_map = _fetch_pokeapi_resource_name_map("move", pokeapi_cache_dir / "move.zh-hans.json")
    ability_map = _fetch_pokeapi_resource_name_map("ability", pokeapi_cache_dir / "ability.zh-hans.json")
    item_map = _fetch_pokeapi_resource_name_map("item", pokeapi_cache_dir / "item.zh-hans.json")

    glossary = _build_glossary(species_map, move_map, ability_map, item_map)
    packs = sorted(
        [path for path in text_root.glob("txt_*.dll")]
        + [text_root / f"{pack_name}.dll" for pack_name in EXTRA_PACK_NAMES if (text_root / f"{pack_name}.dll").exists()],
        key=lambda path: path.stem,
    )

    generic_texts: list[str] = []
    decoded_pack_lines: dict[str, list[str]] = {}
    for pack_path in packs:
        filename = pack_path.stem
        lines = _decode_pack(pack_path)
        decoded_pack_lines[filename] = lines
        for line in lines:
            pages = line.split("@")
            if len(pages) > 1:
                for page_text in pages:
                    page_translation_source = _static_translation_source(page_text)
                    if page_translation_source is None:
                        continue
                    translated = _translate_name_pack_line(filename, page_text, species_map, move_map, ability_map, item_map)
                    if translated is None and page_text not in SOURCE_OVERRIDES:
                        generic_texts.append(page_translation_source)
                    template_translation_source = _template_translation_source(page_text)
                    if template_translation_source is not None and page_text not in SOURCE_OVERRIDES:
                        generic_texts.append(template_translation_source)
            translation_source = _static_translation_source(line)
            if translation_source is None:
                template_translation_source = _template_translation_source(line)
                if template_translation_source is not None and line not in SOURCE_OVERRIDES:
                    generic_texts.append(template_translation_source)
                continue
            translated = _translate_name_pack_line(filename, line, species_map, move_map, ability_map, item_map)
            if translated is None and line not in SOURCE_OVERRIDES:
                generic_texts.append(translation_source)
            template_translation_source = _template_translation_source(line)
            if template_translation_source is not None and line not in SOURCE_OVERRIDES:
                generic_texts.append(template_translation_source)

    google_lookup = _translate_texts_with_cache(generic_texts, google_cache_path, glossary)

    manifest_entries: list[dict[str, str | int]] = []
    translated_pack_lines: dict[str, list[str]] = {}

    def translate_template_line(filename: str, text: str) -> str | None:
        if text in SOURCE_OVERRIDES:
            return SOURCE_OVERRIDES[text]
        template_source = _template_translation_source(text)
        if template_source is None:
            return None
        translated = google_lookup.get(template_source)
        if translated is None:
            return None
        return _restore_template_placeholders(translated)

    for filename, lines in decoded_pack_lines.items():
        wrap_width = PACK_WRAP_WIDTHS.get(filename, 290)

        def translate_line(text: str) -> str:
            if text in SOURCE_OVERRIDES:
                return SOURCE_OVERRIDES[text]
            translated = _translate_name_pack_line(filename, text, species_map, move_map, ability_map, item_map)
            if translated is not None:
                return translated
            translation_source = _static_translation_source(text)
            if translation_source is None:
                return ""
            return google_lookup[translation_source]

        translated_pack_lines[filename] = [
            translate_line(line) if _static_translation_source(line) is not None else ""
            for line in lines
        ]
        manifest_entries.extend(
            build_static_manifest_entries(
                "zh",
                filename,
                lines,
                translate_line,
                max_width=wrap_width,
                font_path=font_path,
                font_size=font_size,
            )
        )
        manifest_entries.extend(
            build_page_manifest_entries(
                "zh",
                filename,
                lines,
                translate_line,
                max_width=wrap_width,
                font_path=font_path,
                font_size=font_size,
            )
        )

    manifest_entries.extend(
        build_dynamic_manifest_entries(
            translated_pack_lines,
            font_path=font_path,
            font_size=font_size,
        )
    )
    layout_entries, layouts = build_dynamic_layout_assets("zh", decoded_pack_lines, translate_template_line)
    manifest_entries.extend(layout_entries)
    manifest_entries.sort(key=lambda entry: (entry["filename"], int(entry["line"]), str(entry.get("key", ""))))
    _write_json(manifest_path, manifest_entries)
    write_dynamic_layout_files(layouts, layout_dir)
    return manifest_entries


def render_manifest_parallel(
    manifest_path: Path,
    output_dir: Path,
    *,
    font_path: Path | None = None,
    font_size: int = DEFAULT_FONT_SIZE,
    workers: int = 8,
) -> None:
    entries = _load_json(manifest_path, [])

    def render_entry(entry: dict[str, str | int]) -> None:
        key = entry.get("key") or make_line_key(str(entry["folder"]), str(entry["filename"]), int(entry["line"]))
        render_bitmap_text(
            str(entry["text"]),
            output_dir / f"{key}.png",
            font_path=font_path,
            font_size=int(entry.get("font_size", font_size)),
        )

    with ThreadPoolExecutor(max_workers=max(workers, 1)) as executor:
        list(executor.map(render_entry, entries))

    for key, text in DYNAMIC_BITMAP_TEXTS:
        render_bitmap_text(
            text,
            output_dir / f"{key}.png",
            font_path=font_path,
            font_size=font_size,
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--render-dir", type=Path)
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--font-path", type=Path)
    parser.add_argument("--font-size", type=int, default=DEFAULT_FONT_SIZE)
    parser.add_argument("--manifest-only", action="store_true")
    parser.add_argument("--render-only", action="store_true")
    parser.add_argument("--render-workers", type=int, default=8)
    args = parser.parse_args()

    root = args.root
    manifest_path = args.manifest or (root / "data" / "text" / "zh" / "render_manifest.json")
    render_dir = args.render_dir or (root / "data" / "text" / "zh" / "render")
    cache_dir = args.cache_dir or (root / "artifacts" / "zh_static_cache")

    manifest_entries: list[dict[str, str | int]] = []
    if not args.render_only:
        manifest_entries = build_render_manifest(
            root,
            manifest_path,
            cache_dir,
            layout_dir=render_dir,
            font_path=args.font_path,
            font_size=args.font_size,
        )
    if not args.manifest_only:
        render_manifest_parallel(
            manifest_path,
            render_dir,
            font_path=args.font_path,
            font_size=args.font_size,
            workers=args.render_workers,
        )
    if not manifest_entries:
        manifest_entries = _load_json(manifest_path, [])
    print(f"entries={len(manifest_entries)} manifest={manifest_path} render_dir={render_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
