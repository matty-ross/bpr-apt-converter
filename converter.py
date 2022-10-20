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
            pass
        elif frame_item_type == 2: # frame label
            pass
        elif frame_item_type == 3: # place object
            pass
        elif frame_item_type == 4: # remove object
            swap(fp, "<L")
        elif frame_item_type == 5: # background color
            swap(fp, "<L")
        elif frame_item_type == 6: # start sound
            assert False, "Should be unused"
        elif frame_item_type == 7: # start sound stream
            assert False, "Should be unused"
        elif frame_item_type == 8: # init action
            pass


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


def main() -> None:
    with open("data/testing.dat", "r+b") as fp:
        convert(fp)


if __name__ == "__main__":
    main()