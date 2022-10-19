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


def convert_character(fp: BinaryIO, apt_data_offset: int, character_offset: int) -> None:
    fp.seek(apt_data_offset + character_offset, os.SEEK_SET)
    character_type = swap(fp, "<L")
    swap(fp, "<L")
    swap(fp, "<H")
    swap(fp, "<H")
    swap(fp, "<L")

    if character_type == 1:
        pass
    elif character_type == 2:
        pass
    elif character_type == 3:
        pass
    elif character_type == 4:
        pass
    elif character_type == 5:
        pass
    elif character_type == 6:
        pass
    elif character_type == 7:
        pass
    elif character_type == 8:
        pass
    elif character_type == 9:
        pass
    elif character_type == 10:
        pass
    elif character_type == 11:
        pass
    elif character_type == 12:
        pass


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