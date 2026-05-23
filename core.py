from os import path
from math import isqrt
from typing import TYPE_CHECKING

from compress import (
    zlib_compress, zlib_decompress,
    bz2_compress, bz2_decompress,
    lzma_compress, lzma_decompress
)

from cryption import encryption, decryption
from data import compress_types

if TYPE_CHECKING:
    from ui import UI

def encode(ui: "UI") -> None:
    ui.set_tooltip_info("")
    password: str = ui.get_password()

    if not password.isascii():
        ui.set_loading_info("错误：密钥不得包含非ASCII字符。")
        return

    ui.set_loading_info("运行进度：正在读取文件。")

    if not ui.file_path:
        ui.set_loading_info("错误：未指定文件。")
        return
    
    if not path.exists(ui.file_path):
        ui.set_loading_info(f"错误：{ui.file_path}不存在。")
        return
    
    if not ui.dir_path:
        ui.set_loading_info("错误：未指定目录。")
        return
    
    if not path.exists(ui.dir_path):
        ui.set_loading_info(f"错误：{ui.dir_path}不存在。")
        return

    try:
        with open(ui.file_path, mode="rb") as f:
            b_file: bytearray = bytearray(f.read())
    except Exception as e:
        ui.set_loading_info(f"文件错误：{e}")
        return
    
    ui.set_loading_info("运行进度：正在压缩信息。")
    compress_type, compress_level = ui.get_compress_settings()
    if compress_type == "raw":
        b_compressed_file: bytearray = b_file
    elif compress_type == "zlib":
        b_compressed_file: bytearray = zlib_compress(b_file, level=compress_level)
    elif compress_type == "bz2":
        b_compressed_file: bytearray = bz2_compress(b_file, level=compress_level)
    elif compress_type == "lzma":
        b_compressed_file: bytearray = lzma_compress(b_file, level=compress_level)
    else:
        ui.set_loading_info("错误：不受支持的压缩方案。")
        return

    # ui.set_loading_info("运行进度：正在组织信息。")

    # format_stub_code: bytes = bytes((0, 0, 0, compress_types.index(compress_type))) # 4 byte
    # b_filename: bytes = path.basename(ui.file_path).encode("utf-8").rjust(256, b"\x00") # 256 byte

    # header: list[bytes] = [format_stub_code, b_filename]
    # header_length_for_item: list[int] = [len(item) for item in header]

    # ui.set_loading_info("运行进度：正在编码信息。")
    # offset: int = 0
    # for index, item in enumerate(header):
    #     b_compressed_file[offset:offset + header_length_for_item[index]] = item
    #     offset += header_length_for_item[index]
    # header_length: int = sum(header_length_for_item)
    # # isqrt((header_length + len(b_file) + 3) // 4) + 1

    # TODO: 乱七八糟的 旧版内存布局与新版不一样 需要重新考虑


def decode(ui: "UI") -> None:
    ...