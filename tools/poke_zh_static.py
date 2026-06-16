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
RAW_KEY_LABELS = (
    tuple(chr(code) for code in range(ord("A"), ord("Z") + 1))
    + tuple(str(number) for number in range(10))
    + tuple(f"F{number}" for number in range(1, 13))
)
KEY_NAME_LINE_NUMBERS = tuple(range(1545, 1609))
KEY_TEMPLATE_LINES = {
    683: "{par1} - 页面",
    684: "{par1} - 叫声",
    685: "{par1} - 退出",
    686: "{par1} - 帮助",
    702: "可查看闪光形态（{par1}）",
    703: "普通形态（{par1}）",
}
RAW_NUMBER_TEMPLATE_LINES = {
    699: "第{par1}页",
}
PACK_TEMPLATE_SPECS = (
    ("txt_menu", 698, "dex_espec", "{par1}宝可梦"),
    ("txt_menu", 705, "txt_pkmn", "{par1}的一般能力值。"),
    ("txt_menu", 707, "txt_pkmn", "{par1}升级可学会的招式。"),
    ("txt_dialog", 2639, "txt_pkmn", "你获得了{par1}。"),
    ("txt_dialog", 2639, "txt_obj", "你获得了{par1}。"),
)
DYNAMIC_BITMAP_TEXTS = [
    (f"zh__txt_dialog__5__slot__{slot}", f"已分配槽位 {slot}#按 Z 继续。")
    for slot in range(1, 100)
]
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


def _dynamic_key_entry(folder: str, filename: str, line: int, key: str, text: str) -> dict[str, str | int]:
    return {
        "folder": folder,
        "filename": filename,
        "line": line,
        "key": key,
        "text": text,
    }


def _build_key_label_entries(translated_pack_lines: dict[str, list[str]]) -> list[dict[str, str | int]]:
    entries: list[dict[str, str | int]] = []
    menu_lines = translated_pack_lines.get("txt_menu", [])
    label_sources: list[tuple[str, str]] = [(raw_label, raw_label) for raw_label in RAW_KEY_LABELS]

    for line_number in KEY_NAME_LINE_NUMBERS:
        if 0 < line_number <= len(menu_lines):
            label = menu_lines[line_number - 1].strip()
            if label:
                label_sources.append((label, make_line_key("zh", "txt_menu", line_number)))

    for line_number, template in KEY_TEMPLATE_LINES.items():
        base_key = make_line_key("zh", "txt_menu", line_number)
        for label, label_key in label_sources:
            if label_key == label:
                key = f"{base_key}__par1raw__{label}"
            else:
                key = f"{base_key}__par1__{label_key}"
            entries.append(_dynamic_key_entry("zh", "txt_menu", line_number, key, template.format(par1=label)))

    for line_number, template in RAW_NUMBER_TEMPLATE_LINES.items():
        for number in range(1, 21):
            entries.append(
                _dynamic_key_entry(
                    "zh",
                    "txt_menu",
                    line_number,
                    f"{make_line_key('zh', 'txt_menu', line_number)}__par1raw__{number}",
                    template.format(par1=number),
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


def build_dynamic_manifest_entries(translated_pack_lines: dict[str, list[str]]) -> list[dict[str, str | int]]:
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
    entries.extend(_build_pack_template_entries(translated_pack_lines))
    return entries


def build_render_manifest(
    root: Path,
    manifest_path: Path,
    cache_dir: Path,
    *,
    font_path: Path | None = None,
    font_size: int = DEFAULT_FONT_SIZE,
) -> list[dict[str, str | int]]:
    text_root = root / "data" / "text" / "en"
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
            translation_source = _static_translation_source(line)
            if translation_source is None:
                continue
            translated = _translate_name_pack_line(filename, line, species_map, move_map, ability_map, item_map)
            if translated is None and line not in SOURCE_OVERRIDES:
                generic_texts.append(translation_source)

    google_lookup = _translate_texts_with_cache(generic_texts, google_cache_path, glossary)

    manifest_entries: list[dict[str, str | int]] = []
    translated_pack_lines: dict[str, list[str]] = {}
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

    manifest_entries.extend(build_dynamic_manifest_entries(translated_pack_lines))
    manifest_entries.sort(key=lambda entry: (entry["filename"], int(entry["line"]), str(entry.get("key", ""))))
    _write_json(manifest_path, manifest_entries)
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
            font_size=font_size,
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
