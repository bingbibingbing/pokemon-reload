from __future__ import annotations

import argparse
from pathlib import Path


VALUES_ADJUSTMENT_MAP = {
    52: 32,
    84: 33,
    110: 34,
    126: 35,
    32: 36,
    44: 37,
    57: 38,
    39: 39,
    112: 40,
    96: 41,
    50: 42,
    98: 43,
    74: 44,
    120: 45,
    108: 46,
    80: 47,
    100: 48,
    75: 49,
    119: 50,
    102: 51,
    78: 52,
    104: 53,
    37: 54,
    101: 55,
    95: 56,
    81: 57,
    45: 58,
    97: 59,
    99: 60,
    60: 61,
    53: 62,
    35: 63,
    113: 64,
    64: 65,
    118: 66,
    76: 67,
    47: 68,
    62: 69,
    116: 70,
    85: 71,
    121: 72,
    59: 73,
    72: 74,
    106: 75,
    115: 76,
    103: 77,
    40: 78,
    86: 79,
    36: 80,
    109: 81,
    82: 82,
    43: 83,
    58: 84,
    107: 85,
    93: 86,
    68: 87,
    91: 88,
    69: 89,
    56: 90,
    88: 91,
    111: 92,
    46: 93,
    41: 94,
    66: 95,
    48: 96,
    125: 97,
    34: 98,
    51: 99,
    89: 100,
    117: 101,
    33: 102,
    73: 103,
    122: 104,
    54: 105,
    94: 106,
    70: 107,
    61: 108,
    105: 109,
    49: 110,
    87: 111,
    55: 112,
    123: 113,
    77: 114,
    71: 115,
    65: 116,
    92: 117,
    42: 118,
    90: 119,
    67: 120,
    38: 121,
    63: 122,
    79: 123,
    83: 124,
    124: 125,
    114: 126,
}

VALUES_ADJUSTMENT_INVERSE_MAP = {decoded: encoded for encoded, decoded in VALUES_ADJUSTMENT_MAP.items()}

SPECIAL_CHAR_MAP = {
    "&{n}": "ñ",
    "&{N}": "Ñ",
    "&{a}": "á",
    "&{e}": "é",
    "&{i}": "í",
    "&{o}": "ó",
    "&{u}": "ú",
    "&{A}": "Á",
    "&{E}": "É",
    "&{I}": "Í",
    "&{O}": "Ó",
    "&{U}": "Ú",
    "&{aa}": "à",
    "&{AA}": "À",
    "&{ee}": "è",
    "&{EE}": "È",
    "&{e2}": "ê",
    "&{E2}": "Ê",
    "&{uu}": "ü",
    "&{UU}": "Ü",
    "&{C}": "Ç",
    "&{c}": "ç",
    "&{?}": "¿",
    "&{!}": "¡",
    "&{E1}": "€",
    "&{o1}": "º",
    "&{a1}": "ª",
    "&{c1}": "’",
    "&{c2}": "´",
    "&{.}": "…",
    "&{i1}": "¬",
    "&{u2}": "¨",
    "&{ss}": "§",
}

SPECIAL_CHAR_INVERSE_MAP = {value: key for key, value in SPECIAL_CHAR_MAP.items()}


def decode_lines(blob: bytes) -> list[bytes]:
    if not blob:
        return []
    return blob.splitlines(keepends=True)


def encode_lines(lines: list[bytes]) -> bytes:
    return b"".join(lines)


def roundtrip_bytes(blob: bytes) -> bytes:
    return encode_lines(decode_lines(blob))


def replace_line_text(blob: bytes, line_index: int, replacement: bytes) -> bytes:
    lines = decode_lines(blob)
    current = lines[line_index]
    newline = b""
    if current.endswith(b"\r\n"):
        newline = b"\r\n"
    elif current.endswith(b"\n"):
        newline = b"\n"
    if newline:
        current = current[: -len(newline)]
    lines[line_index] = replacement + newline
    return encode_lines(lines)


def compare_line_lengths(left: bytes, right: bytes) -> list[tuple[int, int, int]]:
    left_lines = decode_lines(left)
    right_lines = decode_lines(right)
    rows: list[tuple[int, int, int]] = []
    for index, (left_line, right_line) in enumerate(zip(left_lines, right_lines)):
        rows.append(
            (
                index,
                len(left_line.rstrip(b"\r\n")),
                len(right_line.rstrip(b"\r\n")),
            )
        )
    return rows


def decode_display_text(raw_line: bytes) -> str:
    raw = raw_line.rstrip(b"\r\n")
    decoded = bytes(VALUES_ADJUSTMENT_MAP.get(byte, byte) for byte in raw)
    text = decoded.decode("latin1")
    for token, character in SPECIAL_CHAR_MAP.items():
        text = text.replace(token, character)
    return text


def encode_display_text(text: str, encoding: str = "latin1") -> bytes:
    encoded_text = text
    for character, token in SPECIAL_CHAR_INVERSE_MAP.items():
        encoded_text = encoded_text.replace(character, token)
    encoded_bytes = encoded_text.encode(encoding)
    return bytes(VALUES_ADJUSTMENT_INVERSE_MAP.get(byte, byte) for byte in encoded_bytes)


def build_token_alphabet(raw_tokens: list[str]) -> list[str]:
    return sorted(set(raw_tokens), key=len, reverse=True)


def tokenize_line(
    line: str,
    alphabet: list[str],
    allow_fallback_single_chars: bool = False,
) -> list[str]:
    tokens: list[str] = []
    index = 0
    while index < len(line):
        match = None
        for token in alphabet:
            if line.startswith(token, index):
                match = token
                break
        if match is None:
            if allow_fallback_single_chars:
                tokens.append(line[index])
                index += 1
                continue
            raise ValueError(f"Unrecognized token at index {index}: {line[index:index + 16]!r}")
        tokens.append(match)
        index += len(match)
    return tokens


def infer_char_mapping(
    encoded_lines: list[str],
    plaintext_lines: list[str],
    alphabet: list[str],
) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for encoded_line, plaintext_line in zip(encoded_lines, plaintext_lines):
        tokens = tokenize_line(encoded_line, alphabet)
        if len(tokens) != len(plaintext_line):
            continue
        for token, character in zip(tokens, plaintext_line):
            existing = mapping.get(token)
            if existing is not None and existing != character:
                raise ValueError(
                    f"Conflicting mapping for token {token!r}: {existing!r} vs {character!r}"
                )
            mapping[token] = character
    return mapping


def decode_line_with_mapping(
    line: str,
    mapping: dict[str, str],
    alphabet: list[str],
    unknown: str = "?",
) -> str:
    return "".join(mapping.get(token, unknown) for token in tokenize_line(line, alphabet))


def decode_line_with_composites(
    line: str,
    mapping: dict[str, str],
    alphabet: list[str],
    unknown: str = "?",
) -> str:
    accent_map = {
        "a": "á",
        "e": "é",
        "i": "í",
        "o": "ó",
        "u": "ú",
        "A": "Á",
        "E": "É",
        "I": "Í",
        "O": "Ó",
        "U": "Ú",
    }
    tokens = tokenize_line(line, alphabet)
    decoded: list[str] = []
    index = 0
    while index < len(tokens):
        if index + 3 < len(tokens) and tokens[index] == "9" and tokens[index + 1] == "O" and tokens[index + 3] == "|":
            base = mapping.get(tokens[index + 2])
            if base in accent_map:
                decoded.append(accent_map[base])
                index += 4
                continue
        decoded.append(mapping.get(tokens[index], unknown))
        index += 1
    return "".join(decoded)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--compare", type=Path)
    args = parser.parse_args()

    blob = args.path.read_bytes()
    rebuilt = roundtrip_bytes(blob)
    output_dir = Path("artifacts/roundtrip")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{args.path.name}.roundtrip").write_bytes(rebuilt)
    print(f"bytes={len(blob)} lines={len(decode_lines(blob))} exact={rebuilt == blob}")
    if args.compare:
        rows = compare_line_lengths(blob, args.compare.read_bytes())
        preview = rows[:5]
        print(f"compare_rows={len(rows)} preview={preview}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
