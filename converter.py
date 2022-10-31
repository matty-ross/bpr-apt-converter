import struct
import os
from typing import BinaryIO


def swap(fp: BinaryIO, fmt: str) -> int:
    size = struct.calcsize(fmt)
    buff = fp.read(size)
    buff = buff[::-1]
    fp.seek(-size, os.SEEK_CUR)
    fp.write(buff)
    return struct.unpack(fmt, buff)[0]


def convert_action_records(fp: BinaryIO, apt_data_offset: int, action_records_offset: int) -> None:
    return # TODO: implement all action types
    fp.seek(apt_data_offset + action_records_offset, os.SEEK_SET)
    while True:
        action_type = swap(fp, "B")
        if action_type == 0:
            break
        elif action_type <= 0x76:
            continue
        elif action_type in [0x77, 0xB4, 0xB7, ]:
            assert False, "Unimplemented"
        elif action_type in [0x78, 0x79, 0x7A, 0x7B, 0x7C, 0x7D, 0x7E, 0x7F, 0x80, 0x82, 0x84, 0x85, 0x86, 0x89, 0x8A, 0x8D, 0x90, 0x91, 0x92, 0x93, 0x95, 0x97, 0x98, 0x9A, 0x9C, 0x9E, 0xA0, 0xA8, 0xA9, 0xAA, 0xAB, 0xAC, 0xAD, ]:
            continue
        elif action_type in [0x81, 0x87, 0x99, 0x9D, 0x9F, 0xB8, ]:
            swap(fp, "<L")
        elif action_type in [0x83, ]:
            assert False, "Unimplemented"
        elif action_type in [0x88, 0x96, ]:
            swap(fp, "<L")
            swap(fp, "<L")
            # TODO: follow the pointer
        elif action_type in [0x8B, ]:
            assert False, "Unimplemented"
        elif action_type in [0x8C, ]:
            assert False, "Unimplemented"
        elif action_type in [0x8E, ]:
            assert False, "Unimplemented"
        elif action_type in [0x8F, ]:
            assert False, "Unimplemented"
        elif action_type in [0x94, ]:
            assert False, "Unimplemented"
        elif action_type in [0x9B, ]:
            assert False, "Unimplemented"
        elif action_type in [0xA1, 0xA4, 0xA5, 0xA6, 0xA7, ]:
            assert False, "Unimplemented"
        elif action_type in [0xA2, 0xAE, 0xAF, 0xB0, 0xB1, 0xB2, 0xB3, 0xB5, ]:
            swap(fp, "B")
        elif action_type in [0xA3, 0xB6, ]:
            assert False, "Unimplemented"
        else:
            assert False, "Unknown action type"


def convert_frame(fp: BinaryIO, apt_data_offset: int, frame_offset: int) -> None:
    fp.seek(apt_data_offset + frame_offset, os.SEEK_SET)
    item_count = swap(fp, "<L")
    items_offset = swap(fp, "<L")
    for i in range(item_count):
        fp.seek(apt_data_offset + items_offset + i * 0x4, os.SEEK_SET)
        frame_item_offset = swap(fp, "<L")
        if frame_item_offset == 0:
            continue
        fp.seek(apt_data_offset + frame_item_offset)
        frame_item_type = swap(fp, "<L")

        if frame_item_type == 1: # action
            action_records_offset = swap(fp, "<L")
            convert_action_records(fp, apt_data_offset, action_records_offset)
        elif frame_item_type == 2: # frame label
            swap(fp, "<L")
            swap(fp, "<H")
            swap(fp, "<H")
            swap(fp, "<L")
        elif frame_item_type == 3: # place object
            flags = swap(fp, "<L")
            swap(fp, "<L")
            swap(fp, "<L")
            for _ in range(6):
                swap(fp, "<L")
            swap(fp, "<L")
            swap(fp, "<L")
            swap(fp, "<L")
            swap(fp, "<L")
            swap(fp, "<L")
            clip_actions_offset = swap(fp, "<L")
        elif frame_item_type == 4: # remove object
            swap(fp, "<L")
        elif frame_item_type == 5: # background color
            swap(fp, "<L")
        elif frame_item_type == 6: # start sound
            assert False, "Should be unused"
        elif frame_item_type == 7: # start sound stream
            assert False, "Should be unused"
        elif frame_item_type == 8: # init action
            swap(fp, "<L")
            action_records_offset = swap(fp, "<L")
            convert_action_records(fp, apt_data_offset, action_records_offset)
        else:
            assert False, "Unknown frame item type"


def convert_character(fp: BinaryIO, apt_data_offset: int, character_offset: int) -> None:
    fp.seek(apt_data_offset + character_offset, os.SEEK_SET)
    character_type = swap(fp, "<L")
    swap(fp, "<L")
    swap(fp, "<H")
    swap(fp, "<H")
    swap(fp, "<L")

    if character_type == 1: # shape
        swap(fp, "<L")
        swap(fp, "<L")
        swap(fp, "<L")
        swap(fp, "<L")
        swap(fp, "<L")
    elif character_type == 2: # text
        swap(fp, "<L")
        swap(fp, "<L")
        swap(fp, "<L")
        swap(fp, "<L")
        swap(fp, "<L")
        swap(fp, "<L")
        swap(fp, "<L")
        swap(fp, "<L")
        swap(fp, "<L")
        swap(fp, "<L")
        swap(fp, "<L")
        swap(fp, "<L")
        swap(fp, "<L")
    elif character_type == 3: # font
        swap(fp, "<L")
        swap(fp, "<L")
        assert swap(fp, "<L") == 0, "Should be unused"
    elif character_type == 4: # button
        assert False, "Should be unused"
    elif character_type == 5: # sprite
        frame_count = swap(fp, "<L")
        frames_offset = swap(fp, "<L")
        assert swap(fp, "<L") == 0, "Should be unused"
        for i in range(frame_count):
            convert_frame(fp, apt_data_offset, frames_offset + i * 0x8)
    elif character_type == 6: # sound
        assert False, "Should be unused"
    elif character_type == 7: # image
        swap(fp, "<L")
    elif character_type == 8: # morph
        assert False, "Should be unused"
    elif character_type == 9: # movie
        frame_count = swap(fp, "<L")
        frames_offset = swap(fp, "<L")
        assert swap(fp, "<L") == 0, "Should be unused"
        fp.seek(0x8, os.SEEK_CUR) # skip characters
        swap(fp, "<L")
        swap(fp, "<L")
        swap(fp, "<L")
        import_count = swap(fp, "<L")
        imports_offset = swap(fp, "<L")
        export_count = swap(fp, "<L")
        exports_offset = swap(fp, "<L")
        assert swap(fp, "<L") == 0, "Should be unused"
        fp.seek(apt_data_offset + imports_offset, os.SEEK_SET)
        for _ in range(import_count):
            swap(fp, "<L")
            swap(fp, "<L")
            swap(fp, "<L")
            assert swap(fp, "<L") == 0, "Should be unused"
        fp.seek(apt_data_offset + exports_offset, os.SEEK_SET)
        for _ in range(export_count):
            swap(fp, "<L")
            swap(fp, "<L")
        for i in range(frame_count):
            convert_frame(fp, apt_data_offset, frames_offset + i * 0x8)
    elif character_type == 10: # static text
        assert False, "Should be unused"
    elif character_type == 11: # none
        assert False, "Should be unused"
    elif character_type == 12: # video
        assert False, "Should be unused"
    else:
        assert False, "Unknown character type"


def convert_vertex(fp: BinaryIO, vertex_offset: int) -> None:
    fp.seek(vertex_offset)
    swap(fp, "<L")
    swap(fp, "<L")
    fp.seek(0x4, os.SEEK_CUR)
    swap(fp, "<L")
    swap(fp, "<L")


def convert_geometry_data(fp: BinaryIO, geometry_data_offset: int) -> None:
    fp.seek(geometry_data_offset)
    swap(fp, "<L")
    swap(fp, "<L")
    swap(fp, "<L")
    swap(fp, "<L")
    vertices_count = swap(fp, "<L")
    vertices_offset = swap(fp, "<L")
    for i in range(vertices_count):
        fp.seek(vertices_offset + i * 0x4, os.SEEK_SET)
        vertex_offset = swap(fp, "<L")
        convert_vertex(fp, vertex_offset)


def convert_geometry_record(fp: BinaryIO, geometry_record_offset: int) -> None:
    fp.seek(geometry_record_offset, os.SEEK_SET)
    swap(fp, "<L")
    geometry_data_count = swap(fp, "<L")
    geometry_data_offsets = swap(fp, "<L")
    for i in range(geometry_data_count):
        fp.seek(geometry_data_offsets + i * 0x4, os.SEEK_SET)
        geometry_data_offset = swap(fp, "<L")
        convert_geometry_data(fp, geometry_data_offset)


def convert(fp: BinaryIO) -> None:
    # header
    fp.seek(0x0, os.SEEK_SET)
    swap(fp, "<L")
    swap(fp, "<L")
    apt_data_offset = swap(fp, "<L")
    const_offset = swap(fp, "<L")
    geometry_offset = swap(fp, "<L")
    swap(fp, "<L")

    # apt constant file
    fp.seek(const_offset + 0x14, os.SEEK_SET)
    movie_offset = swap(fp, "<L")
    item_count = swap(fp, "<L")
    constants_offset = swap(fp, "<L")
    fp.seek(const_offset + constants_offset, os.SEEK_SET)
    for _ in range(item_count):
        swap(fp, "<L")
        swap(fp, "<L")

    # characters
    fp.seek(apt_data_offset + movie_offset + 0x1C, os.SEEK_SET)
    character_count = swap(fp, "<L")
    characters_offset = swap(fp, "<L")
    for i in range(character_count):
        fp.seek(apt_data_offset + characters_offset + i * 0x4, os.SEEK_SET)
        character_offset = swap(fp, "<L")
        if character_offset != 0:
            convert_character(fp, apt_data_offset, character_offset)

    # geometry
    fp.seek(geometry_offset, os.SEEK_SET)
    geometry_record_count = swap(fp, "<L")
    swap(fp, "<L")
    geometry_records_offset = swap(fp, "<L")
    for i in range(geometry_record_count):
        fp.seek(geometry_records_offset + i * 0x4, os.SEEK_SET)
        geometry_record_offset = swap(fp, "<L")
        convert_geometry_record(fp, geometry_record_offset)



def main() -> None:
    with open("data/testing.dat", "r+b") as fp:
        convert(fp)


if __name__ == "__main__":
    main()