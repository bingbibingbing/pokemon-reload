from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
import argparse
import struct
import zlib


GMK_MAGIC = 1234321
GM80_DATA_OFFSET = 0x1E8480
SWAP_TABLE_SIZE = 256


@dataclass(frozen=True)
class FontResource:
    index: int
    name: str
    font_name: str
    size: int
    bold: bool
    italic: bool
    range_begin: int
    range_end: int


@dataclass(frozen=True)
class ScriptResource:
    index: int
    name: str
    source: str


@dataclass(frozen=True)
class ObjectAction:
    lib_id: int
    act_id: int
    kind: int
    may_be_relative: bool
    question: bool
    applies_to_something: bool
    action_type: int
    function_name: str
    function_code: str
    arguments_used: int
    argument_kind: tuple[int, ...]
    applies_to_object: int
    is_relative: bool
    argument_value: tuple[str, ...]
    not_flag: bool


@dataclass(frozen=True)
class ObjectEvent:
    event_type: int
    event_kind: int
    actions: tuple[ObjectAction, ...]


@dataclass(frozen=True)
class ObjectResource:
    index: int
    name: str
    sprite_index: int
    solid: bool
    visible: bool
    depth: int
    persistent: bool
    parent_index: int
    mask_index: int
    events: tuple[ObjectEvent, ...]


@dataclass(frozen=True)
class RoomInstance:
    x: int
    y: int
    obj_index: int
    instance_id: int
    creation_code: str


@dataclass(frozen=True)
class RoomResource:
    index: int
    name: str
    caption: str
    width: int
    height: int
    speed: int
    persistent: bool
    bg_color: int
    bg_color_draw: bool
    creation_code: str
    instances: tuple[RoomInstance, ...]


@dataclass(frozen=True)
class EncryptedGameBlob:
    length_offset: int
    data_offset: int
    encrypted_data: bytes
    decrypted_data: bytes
    forward_table: tuple[int, ...]


@dataclass(frozen=True)
class GameResources:
    exe_path: Path
    runner_version: int
    fonts: list[FontResource | None]
    scripts: dict[int, ScriptResource]
    script_count: int
    objects: dict[int, ObjectResource]
    object_count: int
    rooms: dict[int, RoomResource]
    room_count: int

    def get_script(self, index: int) -> ScriptResource:
        return self.scripts[index]

    def get_object(self, index: int) -> ObjectResource:
        return self.objects[index]

    def get_room(self, index: int) -> RoomResource:
        return self.rooms[index]


class _Stream:
    def __init__(self, data: bytes) -> None:
        self._data = data
        self.pos = 0

    def setpos(self, offset: int) -> None:
        self.pos = offset

    def skip_bytes(self, size: int) -> None:
        self.pos += size

    def skip_dwords(self, count: int) -> None:
        self.pos += 4 * count

    def read(self, size: int) -> bytes:
        end = self.pos + size
        if end > len(self._data):
            raise EOFError(f"read past end at pos={self.pos} size={size} len={len(self._data)}")
        chunk = self._data[self.pos:end]
        self.pos = end
        return chunk

    def read_dword(self) -> int:
        return struct.unpack("<I", self.read(4))[0]

    def read_sdword(self) -> int:
        return struct.unpack("<i", self.read(4))[0]

    def read_bool(self) -> bool:
        return self.read_dword() >= 1

    def read_string_bytes(self) -> bytes:
        return self.read(self.read_dword())

    def read_string(self) -> str:
        return self.read_string_bytes().decode("latin1", errors="replace")

    def deserialize(self, decompress: bool) -> _Stream:
        blob = self.read(self.read_dword())
        if decompress:
            blob = zlib.decompress(blob)
        return _Stream(blob)


def _skip_settings(stream: _Stream) -> None:
    stream.skip_dwords(1)
    stream.deserialize(True)


def _skip_wrapper(stream: _Stream) -> None:
    stream.skip_bytes(stream.read_dword())
    stream.skip_bytes(stream.read_dword())


def decrypt_game_blob(encrypted_data: bytes, forward_table: tuple[int, ...] | bytes) -> bytes:
    forward = list(forward_table)
    reverse = [0] * SWAP_TABLE_SIZE
    for index, value in enumerate(forward):
        reverse[value] = index

    data = bytearray(encrypted_data)

    for index in range(len(data) - 1, 0, -1):
        data[index] = (reverse[data[index]] - data[index - 1] - index) & 0xFF

    for index in range(len(data) - 1, -1, -1):
        swap_index = index - forward[index & 0xFF]
        if swap_index < 0:
            swap_index = 0
        data[index], data[swap_index] = data[swap_index], data[index]

    return bytes(data)


def encrypt_game_blob(decrypted_data: bytes, forward_table: tuple[int, ...] | bytes) -> bytes:
    forward = list(forward_table)
    data = bytearray(decrypted_data)

    for index in range(len(data)):
        swap_index = index - forward[index & 0xFF]
        if swap_index < 0:
            swap_index = 0
        data[index], data[swap_index] = data[swap_index], data[index]

    for index in range(1, len(data)):
        data[index] = forward[(data[index] + data[index - 1] + index) & 0xFF]

    return bytes(data)


def extract_encrypted_game_blob(raw: bytes) -> EncryptedGameBlob:
    if struct.unpack_from("<I", raw, GM80_DATA_OFFSET)[0] != GMK_MAGIC:
        raise ValueError("input is not a supported GM8.0 runner build")

    stream = _Stream(raw)
    stream.setpos(GM80_DATA_OFFSET + 4)
    stream.skip_dwords(2)
    _skip_settings(stream)
    _skip_wrapper(stream)

    d1 = stream.read_dword()
    d2 = stream.read_dword()
    stream.skip_dwords(d1)
    forward = tuple(stream.read(SWAP_TABLE_SIZE))
    stream.skip_dwords(d2)

    length_offset = stream.pos
    encrypted_size = stream.read_dword()
    data_offset = stream.pos
    encrypted_data = stream.read(encrypted_size)

    return EncryptedGameBlob(
        length_offset=length_offset,
        data_offset=data_offset,
        encrypted_data=encrypted_data,
        decrypted_data=decrypt_game_blob(encrypted_data, forward),
        forward_table=forward,
    )


def _skip_extensions(stream: _Stream) -> None:
    stream.skip_dwords(1)
    count = stream.read_dword()
    for _ in range(count):
        stream.skip_dwords(1)
        stream.read_string()
        stream.skip_bytes(stream.read_dword())

        block_count = stream.read_dword()
        for _ in range(block_count):
            stream.skip_dwords(1)
            stream.skip_bytes(stream.read_dword())
            stream.skip_dwords(1)
            stream.skip_bytes(stream.read_dword())
            stream.skip_bytes(stream.read_dword())

            compiled_count = stream.read_dword()
            for _ in range(compiled_count):
                stream.skip_dwords(1)
                stream.skip_bytes(stream.read_dword())
                stream.skip_bytes(stream.read_dword())
                stream.skip_dwords(3)
                stream.skip_dwords(17)
                stream.skip_dwords(1)

            function_count = stream.read_dword()
            for _ in range(function_count):
                stream.skip_dwords(1)
                stream.skip_bytes(stream.read_dword())
                stream.skip_bytes(stream.read_dword())

        stream.skip_bytes(stream.read_dword())


def _skip_serialized_section(stream: _Stream) -> int:
    stream.skip_dwords(1)
    count = stream.read_dword()
    for _ in range(count):
        stream.skip_bytes(stream.read_dword())
    return count


def _skip_constants(stream: _Stream) -> int:
    stream.skip_dwords(1)
    count = stream.read_dword()
    for _ in range(count):
        stream.read_string_bytes()
        stream.read_string_bytes()
    return count


def _read_fonts(stream: _Stream) -> list[FontResource | None]:
    stream.skip_dwords(1)
    count = stream.read_dword()
    fonts: list[FontResource | None] = []

    for index in range(count):
        resource = stream.deserialize(True)
        if not resource.read_bool():
            fonts.append(None)
            continue

        name = resource.read_string()
        resource.skip_dwords(1)
        font_name = resource.read_string()
        size = resource.read_dword()
        bold = resource.read_bool()
        italic = resource.read_bool()
        range_begin = resource.read_dword()
        range_end = resource.read_dword()

        fonts.append(
            FontResource(
                index=index,
                name=name,
                font_name=font_name,
                size=size,
                bold=bold,
                italic=italic,
                range_begin=range_begin,
                range_end=range_end,
            )
        )

    return fonts


def _iter_scripts(stream: _Stream) -> tuple[int, Iterator[ScriptResource]]:
    stream.skip_dwords(1)
    count = stream.read_dword()

    def _generator() -> Iterator[ScriptResource]:
        for index in range(count):
            resource = stream.deserialize(True)
            if not resource.read_bool():
                continue
            name = resource.read_string()
            resource.skip_dwords(1)
            source = resource.read_string()
            yield ScriptResource(index=index, name=name, source=source)

    return count, _generator()


def _read_object_action(stream: _Stream) -> ObjectAction:
    stream.skip_dwords(1)
    lib_id = stream.read_dword()
    act_id = stream.read_dword()
    kind = stream.read_dword()
    may_be_relative = stream.read_bool()
    question = stream.read_bool()
    applies_to_something = stream.read_bool()
    action_type = stream.read_dword()
    function_name = stream.read_string()
    function_code = stream.read_string()
    arguments_used = stream.read_dword()
    stream.skip_dwords(1)
    argument_kind = tuple(stream.read_dword() for _ in range(8))
    applies_to_object = stream.read_sdword()
    is_relative = stream.read_bool()
    stream.skip_dwords(1)
    argument_value = tuple(stream.read_string() for _ in range(8))
    not_flag = stream.read_bool()

    return ObjectAction(
        lib_id=lib_id,
        act_id=act_id,
        kind=kind,
        may_be_relative=may_be_relative,
        question=question,
        applies_to_something=applies_to_something,
        action_type=action_type,
        function_name=function_name,
        function_code=function_code,
        arguments_used=arguments_used,
        argument_kind=argument_kind,
        applies_to_object=applies_to_object,
        is_relative=is_relative,
        argument_value=argument_value,
        not_flag=not_flag,
    )


def _iter_objects(stream: _Stream) -> tuple[int, Iterator[ObjectResource]]:
    stream.skip_dwords(1)
    count = stream.read_dword()

    def _generator() -> Iterator[ObjectResource]:
        for index in range(count):
            resource = stream.deserialize(True)
            if not resource.read_bool():
                continue

            name = resource.read_string()
            resource.skip_dwords(1)
            sprite_index = resource.read_sdword()
            solid = resource.read_bool()
            visible = resource.read_bool()
            depth = resource.read_sdword()
            persistent = resource.read_bool()
            parent_index = resource.read_sdword()
            mask_index = resource.read_sdword()

            events: list[ObjectEvent] = []
            event_type_count = resource.read_dword() + 1
            for event_type in range(event_type_count):
                while True:
                    event_kind = resource.read_sdword()
                    if event_kind == -1:
                        break

                    resource.skip_dwords(1)
                    action_count = resource.read_dword()
                    actions = tuple(_read_object_action(resource) for _ in range(action_count))
                    events.append(
                        ObjectEvent(
                            event_type=event_type,
                            event_kind=event_kind,
                            actions=actions,
                        )
                    )

            yield ObjectResource(
                index=index,
                name=name,
                sprite_index=sprite_index,
                solid=solid,
                visible=visible,
                depth=depth,
                persistent=persistent,
                parent_index=parent_index,
                mask_index=mask_index,
                events=tuple(events),
            )

    return count, _generator()


def _iter_rooms(stream: _Stream, runner_version: int) -> tuple[int, Iterator[RoomResource]]:
    stream.skip_dwords(1)
    count = stream.read_dword()

    def _generator() -> Iterator[RoomResource]:
        for index in range(count):
            resource = stream.deserialize(True)
            if not resource.read_bool():
                continue

            name = resource.read_string()
            resource.skip_dwords(1)
            caption = resource.read_string()
            width = resource.read_dword()
            height = resource.read_dword()
            speed = resource.read_dword()
            persistent = resource.read_bool()
            bg_color = resource.read_dword()
            bg_color_draw = resource.read_bool()
            creation_code = resource.read_string()

            if runner_version == 800:
                snap_size = 16
            else:
                snap_size = 32
            _ = snap_size

            background_count = resource.read_dword()
            for _ in range(background_count):
                resource.read_bool()
                resource.read_bool()
                resource.read_sdword()
                resource.read_sdword()
                resource.read_sdword()
                resource.read_bool()
                resource.read_bool()
                resource.read_sdword()
                resource.read_sdword()
                resource.read_bool()

            resource.read_bool()
            view_count = resource.read_dword()
            for _ in range(view_count):
                resource.read_bool()
                resource.skip_dwords(13)

            instances: list[RoomInstance] = []
            instance_count = resource.read_dword()
            for _ in range(instance_count):
                instances.append(
                    RoomInstance(
                        x=resource.read_sdword(),
                        y=resource.read_sdword(),
                        obj_index=resource.read_sdword(),
                        instance_id=resource.read_sdword(),
                        creation_code=resource.read_string(),
                    )
                )

            tile_count = resource.read_dword()
            for _ in range(tile_count):
                resource.skip_dwords(9)

            yield RoomResource(
                index=index,
                name=name,
                caption=caption,
                width=width,
                height=height,
                speed=speed,
                persistent=persistent,
                bg_color=bg_color,
                bg_color_draw=bg_color_draw,
                creation_code=creation_code,
                instances=tuple(instances),
            )

    return count, _generator()


@dataclass(frozen=True)
class _ScriptSection:
    section_start: int
    entries_offset: int
    section_end: int
    entries: list[bytes]


def _read_script_section(decrypted_data: bytes) -> _ScriptSection:
    stream = _Stream(decrypted_data)
    pre_count = stream.read_dword()
    stream.skip_dwords(pre_count + 1)
    stream.read_dword()
    for _ in range(4):
        stream.read_dword()

    _skip_extensions(stream)
    _skip_serialized_section(stream)
    _skip_constants(stream)
    _skip_serialized_section(stream)
    _skip_serialized_section(stream)
    _skip_serialized_section(stream)
    _skip_serialized_section(stream)

    section_start = stream.pos
    stream.skip_dwords(1)
    count = stream.read_dword()
    entries_offset = stream.pos
    entries: list[bytes] = []

    for _ in range(count):
        entries.append(stream.read(stream.read_dword()))

    return _ScriptSection(
        section_start=section_start,
        entries_offset=entries_offset,
        section_end=stream.pos,
        entries=entries,
    )


def _patch_compressed_script_source_replace(
    compressed_resource: bytes,
    old: str,
    new: str,
) -> bytes:
    resource_data = zlib.decompress(compressed_resource)
    resource = _Stream(resource_data)

    if not resource.read_bool():
        raise ValueError("target script slot is empty")

    resource.read_string()
    resource.skip_dwords(1)
    source_length_offset = resource.pos
    source_length = resource.read_dword()
    source_offset = resource.pos
    source_bytes = resource.read(source_length)
    source = source_bytes.decode("latin1", errors="strict")

    if old not in source:
        raise ValueError(f"substring not found in script source: {old!r}")

    patched_source = source.replace(old, new, 1)
    patched_bytes = patched_source.encode("latin1", errors="strict")
    patched_resource = (
        resource_data[:source_length_offset]
        + struct.pack("<I", len(patched_bytes))
        + patched_bytes
        + resource_data[source_offset + source_length :]
    )
    return zlib.compress(patched_resource)


def _patch_compressed_script_source(
    compressed_resource: bytes,
    new_source: str,
) -> bytes:
    resource_data = zlib.decompress(compressed_resource)
    resource = _Stream(resource_data)

    if not resource.read_bool():
        raise ValueError("target script slot is empty")

    resource.read_string()
    resource.skip_dwords(1)
    source_length_offset = resource.pos
    source_length = resource.read_dword()
    source_offset = resource.pos
    new_source_bytes = new_source.encode("latin1", errors="strict")

    patched_resource = (
        resource_data[:source_length_offset]
        + struct.pack("<I", len(new_source_bytes))
        + new_source_bytes
        + resource_data[source_offset + source_length :]
    )
    return zlib.compress(patched_resource)


def _patch_script_entry(
    raw: bytes,
    script_index: int,
    patch_entry: callable,
) -> bytes:
    blob = extract_encrypted_game_blob(raw)
    section = _read_script_section(blob.decrypted_data)

    if script_index < 0 or script_index >= len(section.entries):
        raise IndexError(f"script index out of range: {script_index}")

    rebuilt_entries: list[bytes] = []
    for index, entry in enumerate(section.entries):
        if index == script_index:
            entry = patch_entry(entry)
        rebuilt_entries.append(struct.pack("<I", len(entry)) + entry)

    patched_decrypted = (
        blob.decrypted_data[: section.entries_offset]
        + b"".join(rebuilt_entries)
        + blob.decrypted_data[section.section_end :]
    )
    patched_encrypted = encrypt_game_blob(patched_decrypted, blob.forward_table)

    return (
        raw[: blob.length_offset]
        + struct.pack("<I", len(patched_encrypted))
        + patched_encrypted
        + raw[blob.data_offset + len(blob.encrypted_data) :]
    )


def patch_script_source(raw: bytes, script_index: int, new_source: str) -> bytes:
    return _patch_script_entry(
        raw,
        script_index,
        lambda entry: _patch_compressed_script_source(entry, new_source),
    )


def patch_script_source_replace(raw: bytes, script_index: int, old: str, new: str) -> bytes:
    return _patch_script_entry(
        raw,
        script_index,
        lambda entry: _patch_compressed_script_source_replace(entry, old, new),
    )


def load_game(exe_path: Path) -> GameResources:
    raw = exe_path.read_bytes()
    if struct.unpack_from("<I", raw, GM80_DATA_OFFSET)[0] != GMK_MAGIC:
        raise ValueError(f"{exe_path} is not a supported GM8.0 runner build")

    runner_version = struct.unpack_from("<I", raw, GM80_DATA_OFFSET + 4)[0]
    game_data = _Stream(extract_encrypted_game_blob(raw).decrypted_data)
    pre_count = game_data.read_dword()
    game_data.skip_dwords(pre_count + 1)
    game_data.read_dword()
    for _ in range(4):
        game_data.read_dword()

    _skip_extensions(game_data)
    _skip_serialized_section(game_data)
    _skip_constants(game_data)
    _skip_serialized_section(game_data)
    _skip_serialized_section(game_data)
    _skip_serialized_section(game_data)
    _skip_serialized_section(game_data)

    script_count, script_iter = _iter_scripts(game_data)
    scripts = {script.index: script for script in script_iter}
    fonts = _read_fonts(game_data)
    _skip_serialized_section(game_data)
    object_count, object_iter = _iter_objects(game_data)
    objects = {resource.index: resource for resource in object_iter}
    room_count, room_iter = _iter_rooms(game_data, runner_version)
    rooms = {resource.index: resource for resource in room_iter}

    return GameResources(
        exe_path=exe_path,
        runner_version=runner_version,
        fonts=fonts,
        scripts=scripts,
        script_count=script_count,
        objects=objects,
        object_count=object_count,
        rooms=rooms,
        room_count=room_count,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("exe", type=Path)
    parser.add_argument("--script-index", type=int)
    parser.add_argument("--script-name")
    parser.add_argument("--list-fonts", action="store_true")
    args = parser.parse_args()

    game = load_game(args.exe)
    print(f"runner_version={game.runner_version} script_count={game.script_count} font_slots={len(game.fonts)}")

    if args.list_fonts:
        for font in game.fonts:
            print(font)

    if args.script_index is not None:
        print(game.get_script(args.script_index).source)

    if args.script_name:
        for script in game.scripts.values():
            if script.name == args.script_name:
                print(script.source)
                break
        else:
            raise SystemExit(f"script not found: {args.script_name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
