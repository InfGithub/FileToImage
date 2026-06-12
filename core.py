from os import path
from math import isqrt
from typing import TYPE_CHECKING

import numpy as np
from PIL import Image

from compress import (
    zlib_compress, zlib_decompress,
    bz2_compress, bz2_decompress,
    lzma_compress, lzma_decompress
)

from cryption import encryption, decryption
from data import compress_types

if TYPE_CHECKING:
    from ui import UI

def get_square_ge(n: int) -> int:
    m: int = isqrt(n)
    if m * m < n:
        m += 1
    return m * m

def get_upper_drive(file_path: str) -> str:
    drive, tail = path.splitdrive(file_path)
    return drive.upper() + tail if drive else file_path

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

    ui.set_loading_info("运行进度：正在组织信息。")
    compressed_file_length: int = len(b_compressed_file)

    format_stub_code: bytes = bytes((0, 0, 0, compress_types.index(compress_type))) # 4 byte
    b_compressed_file_length: bytes = compressed_file_length.to_bytes(length=8)
    b_filename: bytes = path.basename(ui.file_path).encode("ascii")[:256].rjust(256, b"\x00")  # 256 byte

    # code 4b + len 8b + name 256b + salt + sha = 332
    # [code4][len8][name256][salt32][sha32][data]
    head_length: int = 4 + 8 + 256 + 32 + 32
    data_length: int = head_length + compressed_file_length
    side_length: int = get_square_ge((data_length + 3)  // 4)

    b_compressed_file[:0] = bytearray(head_length)
    data: bytearray = b_compressed_file

    data[0:4] = format_stub_code
    data[4:12] = b_compressed_file_length # 4 + 8 = 12
    data[12:268] = b_filename # 12 + 256 = 268

    target_bytes: int = side_length * side_length * 4
    if len(data) < target_bytes:
        data.extend(b"\x00" * (target_bytes - len(data)))

    b_password: bytes = password.encode("ascii")
    salt_buffer: np.ndarray = np.frombuffer(
        data[268:300], # 268 + 32 = 300
        dtype=np.uint8
    )
    sha_buffer: np.ndarray = np.frombuffer(
        data[300:332], # 300 + 32 = 332
        dtype=np.uint8
    )
    buffer: np.ndarray = np.frombuffer(
        data[332:],
        dtype=np.uint8
    )

    ui.set_loading_info("运行进度：正在加密数据。")

    encryption(
        b_password,
        buffer,
        salt_buffer,
        sha_buffer
    )

    ui.set_loading_info("运行进度：正在映射图像。")
    result: Image.Image = Image.fromarray(
        np.frombuffer(data).reshape(
            side_length, side_length, 4
            ),
        mode="RGBA"
    )

    ui.set_loading_info("运行进度：正在保存文件。")
    filename_without_ext: str = path.splitext(path.basename(ui.file_path))[0]
    save_file_path: str = path.join(ui.dir_path, f"{filename_without_ext}.png")
    result.save(
        save_file_path,
        format="PNG",
        optimize=False,
        pnginfo=None,
        icc_profile=None,
        compress_level=compress_level if compress_type == "raw" else 2
    )
        
    upper_file_path: str = get_upper_drive(save_file_path)
    ui.set_loading_info(f"编码完成。保存于{upper_file_path}")
    ui.set_tooltip_info(upper_file_path)

def decode(ui: "UI") -> None:
    ...