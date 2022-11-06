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

        AptFileConverter.FRAME_ITEMS_FUNCTION = {
            1: AptFileConverter.convert_frame_item_action,
            2: AptFileConverter.convert_frame_item_frame_label,
            3: AptFileConverter.convert_frame_item_place_object,
            4: AptFileConverter.convert_frame_item_remove_object,
            5: AptFileConverter.convert_frame_item_background_color,
            8: AptFileConverter.convert_frame_item_init_action,
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

        for i in range(frames_count):
            frame_offset = frames_offset + i * 0x8
            self.convert_frame(frame_offset)


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

        for i in range(frames_count):
            frame_offset = frames_offset + i * 0x8
            self.convert_frame(frame_offset)

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


    def convert_frame(self, frame_offset: int) -> None:
        self.fp.seek(self.apt_data_offset + frame_offset, os.SEEK_SET)
        frame_items_count = self.swap("<L")
        frame_items_offsets = self.swap("<L")

        for i in range(frame_items_count):
            self.fp.seek(self.apt_data_offset + frame_items_offsets + i * 0x4, os.SEEK_SET)
            frame_item_offset = self.swap("<L")
            self.convert_frame_item(frame_item_offset)


    def convert_frame_item(self, frame_item_offset: int) -> None:
        if frame_item_offset == 0:
            return
        
        self.fp.seek(self.apt_data_offset + frame_item_offset, os.SEEK_SET)
        frame_item_type = self.swap("<L")

        fn = AptFileConverter.FRAME_ITEMS_FUNCTION.get(frame_item_type)
        assert fn is not None, f"Frame item {frame_item_type} should be unused."
        fn(self, frame_item_offset + 0x4)


    def convert_frame_item_action(self, frame_item_offset: int) -> None:
        self.fp.seek(self.apt_data_offset + frame_item_offset, os.SEEK_SET)
        actions_offset = self.swap("<L")
        
        self.convert_actions(actions_offset)


    def convert_frame_item_frame_label(self, frame_item_offset: int) -> None:
        self.fp.seek(self.apt_data_offset + frame_item_offset, os.SEEK_SET)
        self.swap("<L")
        self.swap("<H")
        self.swap("<H")
        self.swap("<L")


    def convert_frame_item_place_object(self, frame_item_offset: int) -> None:
        self.fp.seek(self.apt_data_offset + frame_item_offset, os.SEEK_SET)
        self.swap("<L")
        self.swap("<L")
        self.swap("<L")
        for _ in range(6):
            self.swap("<L")
        self.swap("<L")
        self.swap("<L")
        self.swap("<L")
        self.swap("<L")
        self.swap("<L")
        clip_actions_offset = self.swap("<L")
        
        self.convert_clip_actions(clip_actions_offset)


    def convert_clip_actions(self, clip_actions_offset: int) -> None:
        if clip_actions_offset == 0:
            return

        self.fp.seek(self.apt_data_offset + clip_actions_offset, os.SEEK_SET)
        clip_action_records_count = self.swap("<L")
        clip_action_records_offset = self.swap("<L")

        for i in range(clip_action_records_count):
            clip_action_record_offset = clip_action_records_offset + i * 0xC
            self.convert_clip_action_record(clip_action_record_offset)


    def convert_clip_action_record(self, clip_action_record_offset: int) -> None:
        self.fp.seek(self.apt_data_offset + clip_action_record_offset, os.SEEK_SET)
        self.swap("<L")
        self.swap("<L")
        actions_offset = self.swap("<L")

        self.convert_actions(actions_offset)


    def convert_frame_item_remove_object(self, frame_item_offset: int) -> None:
        self.fp.seek(self.apt_data_offset + frame_item_offset, os.SEEK_SET)
        self.swap("<L")


    def convert_frame_item_background_color(self, frame_item_offset: int) -> None:
        self.fp.seek(self.apt_data_offset + frame_item_offset, os.SEEK_SET)
        self.swap("<L")


    def convert_frame_item_init_action(self, frame_item_offset: int) -> None:
        self.fp.seek(self.apt_data_offset + frame_item_offset, os.SEEK_SET)
        self.swap("<L")
        actions_offset = self.swap("<L")
        
        self.convert_actions(actions_offset)


    def convert_actions(self, actions_offset: int) -> None:
        if actions_offset == 0:
            return

        # switch statement at 0x006B6730

        current_offset = self.apt_data_offset + actions_offset
        while True:
            self.fp.seek(current_offset, os.SEEK_SET)
            action = self.swap("B")
            if action == 0:
                break
            elif action in [0x77, 0xB4, 0xB7, ]: # 00
                # align 0x1
                # size 0x4
                self.swap("<L")
                current_offset = self.fp.tell()
            elif action in [0x81, 0x87, 0x99, 0x9D, 0x9F, 0xB8, ]: # 01
                # align 0x4
                # size 0x4
                self.align()
                self.swap("<L")
                current_offset = self.fp.tell()
            elif action in [0x83, ]: # 02
                # align 0x4
                # size 0x8
                self.align()
                self.swap("<L") # TODO: where does it point to?
                self.swap("<L") # TODO: where does it point to?
                current_offset = self.fp.tell()
            elif action in [0x88, 0x96, ]: # 03
                # align 0x4
                # size 0x8
                self.align()
                self.swap("<L")
                self.swap("<L") # TODO: follow the pointer
                current_offset = self.fp.tell()
                # TODO
            elif action in [0x8B, ]: # 04
                # align 0x4
                # size 0x4
                self.align()
                self.swap("<L") # TODO: where does it point to?
                current_offset = self.fp.tell()
            elif action in [0x8C, ]: # 05
                # align 0x4
                # size 0x4
                self.align()
                self.swap("<L")
                current_offset = self.fp.tell()
            elif action in [0x8E, ]: # 06
                # align 0x4
                # size 0x1C
                self.align()
                self.swap("<L") # TODO: follow the pointer
                self.swap("<L")
                self.swap("<H")
                self.swap("<H")
                self.swap("<L") # TODO: follow the pointer
                self.swap("<L")
                self.swap("<L")
                self.swap("<L")
                current_offset = self.fp.tell()
                # TODO
            elif action in [0x8F, ]: # 07
                # align 0x4
                # size 0x14
                self.align()
                self.skip(0x14) # TODO: temporary
                current_offset = self.fp.tell()
                # TODO
            elif action in [0x94, ]: # 08
                # align 0x4
                # size 0x4
                self.align()
                self.swap("<L") # TODO: where does it point to?
                current_offset = self.fp.tell()
            elif action in [0x9B, ]: # 09
                # align 0x4
                # size 0x18
                self.align()
                self.swap("<L") # TODO: follow the pointer
                self.swap("<L")
                self.swap("<L") # TODO: follow the pointer
                self.swap("<L")
                self.swap("<L")
                self.swap("<L")
                current_offset = self.fp.tell()
                # TODO
            elif action in [0xA1, 0xA4, 0xA5, 0xA6, 0xA7, ]: # 0A
                # align 0x4
                # size 0x4
                self.align()
                self.swap("<L")
                current_offset = self.fp.tell()
            elif action in [0xA2, 0xAE, 0xAF, 0xB0, 0xB1, 0xB2, 0xB3, 0xB5, ]: # 0B
                # align 0x1
                # size 0x1
                self.skip(0x1)
                current_offset = self.fp.tell()
            elif action in [0xA3, 0xB6, ]: # 0C
                # align 0x1
                # size 0x2
                self.swap("<H")
                current_offset = self.fp.tell()
            else: # 0D
                current_offset = self.fp.tell()
                continue


    def convert_const_file(self) -> None:
        self.fp.seek(self.const_file_offset, os.SEEK_SET)
        self.skip(0x14)
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
        self.skip(0x4)
        self.swap("<L")
        self.swap("<L")


    def swap(self, fmt: str) -> int:
        size = struct.calcsize(fmt)
        buff = self.fp.read(size)
        buff = buff[::-1]
        self.fp.seek(-size, os.SEEK_CUR)
        self.fp.write(buff)
        return struct.unpack(fmt, buff)[0]


    def skip(self, size: int) -> int:
        self.fp.seek(size, os.SEEK_CUR)


    def align(self) -> None:
        offset = self.fp.tell()
        offset += 0x3
        offset &= 0xFFFFFFFC
        self.fp.seek(offset, os.SEEK_SET)



def main():
    with open("data/testing.dat", "r+b") as fp:
        converter = AptFileConverter(fp)
        converter.convert()


if __name__ == "__main__":
    main()