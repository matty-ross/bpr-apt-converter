import os
import struct
from typing import BinaryIO


class AptFileConverter:


    def __init__(self, fp: BinaryIO):
        self.fp = fp
        self.apt_data_offset = None
        self.const_file_offset = None
        self.geometry_offset = None
        self.movie_offset = None

        AptFileConverter.CHARACTERS_FUNCTIONS = {
            1: AptFileConverter.convert_character_shape,
            2: AptFileConverter.convert_character_text,
            3: AptFileConverter.convert_character_font,
            5: AptFileConverter.convert_character_sprite,
            7: AptFileConverter.convert_character_image,
            9: AptFileConverter.convert_character_movie,
        }


    def convert(self) -> None:
        self.convert_header()
        self.convert_const_file()
        self.convert_character(self.movie_offset)
        self.convert_geometry()


    def convert_header(self) -> None:
        self.fp.seek(0x0, os.SEEK_SET)
        self.swap("<L")
        self.swap("<L")
        self.apt_data_offset = self.swap("<L")
        self.const_file_offset = self.swap("<L")
        self.geometry_offset = self.swap("<L")
        self.swap("<L")


    def convert_import(self, import_offset: int) -> None:
        self.fp.seek(self.apt_data_offset + import_offset, os.SEEK_SET)
        self.swap("<L")
        self.swap("<L")
        self.swap("<L")
        assert self.swap("<L") == 0, "Should be NULL."


    def convert_export(self, export_offset: int) -> None:
        self.fp.seek(self.apt_data_offset + export_offset, os.SEEK_SET)
        self.swap("<L")
        self.swap("<L")


    def convert_character(self, character_offset: int) -> None:
        if character_offset == 0:
            return
        
        self.fp.seek(self.apt_data_offset + character_offset, os.SEEK_SET)
        character_type = self.swap("<L")
        self.swap("<L")
        self.swap("<H")
        self.swap("<H")
        assert self.swap("<L") == 0, "Should be NULL."

        fn = AptFileConverter.CHARACTERS_FUNCTIONS.get(character_type)
        assert fn is not None, f"Character {character_type} should be unused."
        fn(self, character_offset + 0x10)

        
    def convert_character_shape(self, character_offset: int) -> None:
        self.fp.seek(self.apt_data_offset + character_offset, os.SEEK_SET)
        for _ in range(4):
            self.swap("<L")
        self.swap("<L")


    def convert_character_text(self, character_offset: int) -> None:
        self.fp.seek(self.apt_data_offset + character_offset, os.SEEK_SET)
        for _ in range(4):
            self.swap("<L")
        self.swap("<L")
        self.swap("<L")
        self.swap("<L")
        self.swap("<L")
        self.swap("<L")
        self.swap("<L")
        self.swap("<L")
        self.swap("<L")
        self.swap("<L")


    def convert_character_font(self, character_offset: int) -> None:
        self.fp.seek(self.apt_data_offset + character_offset, os.SEEK_SET)
        self.swap("<L")
        self.swap("<L")
        assert self.swap("<L") == 0, "Should be NULL."


    def convert_character_sprite(self, character_offset: int) -> None:
        self.fp.seek(self.apt_data_offset + character_offset, os.SEEK_SET)
        frames_count = self.swap("<L")
        frames_offset = self.swap("<L")
        assert self.swap("<L") == 0, "Should be NULL."


    def convert_character_image(self, character_offset: int) -> None:
        self.fp.seek(self.apt_data_offset + character_offset, os.SEEK_SET)
        self.swap("<L")


    def convert_character_movie(self, character_offset: int) -> None:
        self.fp.seek(self.apt_data_offset + character_offset, os.SEEK_SET)
        frames_count = self.swap("<L")
        frames_offset = self.swap("<L")
        assert self.swap("<L") == 0, "Should be NULL."
        characters_count = self.swap("<L")
        characters_offsets = self.swap("<L")
        self.swap("<L")
        self.swap("<L")
        self.swap("<L")
        imports_count = self.swap("<L")
        imports_offset = self.swap("<L")
        exports_count = self.swap("<L")
        exports_offset = self.swap("<L")
        self.swap("<L")

        for i in range(characters_count):
            self.fp.seek(self.apt_data_offset + characters_offsets + i * 0x4, os.SEEK_SET)
            character_offset = self.swap("<L")
            if character_offset != self.movie_offset: # skip movie to prevent endless recursion
                self.convert_character(character_offset)

        for i in range(imports_count):
            import_offset = imports_offset + i * 0x10
            self.convert_import(import_offset)

        for i in range(exports_count):
            export_offset = exports_offset + i * 0x8
            self.convert_export(export_offset)


    def convert_const_file(self) -> None:
        self.fp.seek(self.const_file_offset, os.SEEK_SET)
        self.fp.seek(0x14, os.SEEK_CUR)
        self.movie_offset = self.swap("<L")
        constants_count = self.swap("<L")
        constants_offset = self.swap("<L")
        
        for i in range(constants_count):
            constant_offset = constants_offset + i * 0x8
            self.convert_constant(constant_offset)


    def convert_constant(self, constant_offset: int) -> None:
        self.fp.seek(self.const_file_offset + constant_offset, os.SEEK_SET)
        self.swap("<L")
        self.swap("<L")

    
    def convert_geometry(self) -> None:
        self.fp.seek(self.geometry_offset, os.SEEK_SET)
        geometry_records_count = self.swap("<L")
        self.swap("<L")
        geometry_records_offsets = self.swap("<L")
        
        for i in range(geometry_records_count):
            self.fp.seek(geometry_records_offsets + i * 0x4, os.SEEK_SET)
            geometry_record_offset = self.swap("<L")
            self.convert_geometry_record(geometry_record_offset)


    def convert_geometry_record(self, geometry_record_offset: int) -> None:
        self.fp.seek(geometry_record_offset, os.SEEK_SET)
        self.swap("<L")
        geometry_data_count = self.swap("<L")
        geometry_data_offsets = self.swap("<L")
        
        for i in range(geometry_data_count):
            self.fp.seek(geometry_data_offsets + i * 0x4, os.SEEK_SET)
            geometry_data_offset = self.swap("<L")
            self.convert_geometry_data(geometry_data_offset)


    def convert_geometry_data(self, geometry_data_offset: int) -> None:
        self.fp.seek(geometry_data_offset, os.SEEK_SET)
        self.swap("<L")
        self.swap("<L")
        self.swap("<L")
        self.swap("<L")
        vertices_count = self.swap("<L")
        vertices_offsets = self.swap("<L")
        
        for i in range(vertices_count):
            self.fp.seek(vertices_offsets + i * 0x4, os.SEEK_SET)
            vertex_offset = self.swap("<L")
            self.convert_vertex(vertex_offset)


    def convert_vertex(self, vertex_offset: int) -> None:
        self.fp.seek(vertex_offset, os.SEEK_SET)
        self.swap("<L")
        self.swap("<L")
        self.fp.seek(0x4, os.SEEK_CUR)
        self.swap("<L")
        self.swap("<L")


    def swap(self, fmt: str) -> int:
        size = struct.calcsize(fmt)
        buff = self.fp.read(size)
        buff = buff[::-1]
        self.fp.seek(-size, os.SEEK_CUR)
        self.fp.write(buff)
        return struct.unpack(fmt, buff)[0]



def main():
    with open("data/testing.dat", "r+b") as fp:
        converter = AptFileConverter(fp)
        converter.convert()


if __name__ == "__main__":
    main()