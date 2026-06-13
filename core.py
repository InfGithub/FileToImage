from os import path
from math import isqrt
from unicodedata import normalize, category

import numpy as np
from PIL import Image

from compress import (
    zlib_compress, zlib_decompress,
    bz2_compress, bz2_decompress,
    lzma_compress, lzma_decompress
)

from cryption import encryption, decryption
from data import compress_types, version
from util import UI

def get_square_ge(n: int) -> int:
    m: int = isqrt(n)
    if m * m < n:
        m += 1
    return m

def get_upper_drive(file_path: str) -> str:
    drive, tail = path.splitdrive(file_path)
    return drive.upper() + tail if drive else file_path

def safe2utf8(data: bytes, max_len: int) -> bytes:
    if len(data) <= max_len:
        return data
    for i in range(max_len, -1, -1):
        if data[i] & 0xC0 != 0x80:
            return data[:i]
    return b""

def encode(ui: UI) -> None:
    ui.set_tooltip_info("")
    password: str = ui.get_password()

    if not password.isprintable():
        ui.set_loading_info("错误：密码包含不可打印字符。")
        return

    if any(category(char) in ("Cf",) for char in password):
        ui.set_loading_info("错误：密码包含不可见字符。")
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

    format_stub_code: bytes = bytes((*version, compress_types.index(compress_type))) # 4 byte
    b_compressed_file_length: bytes = compressed_file_length.to_bytes(length=8)
    b_filename: bytes = safe2utf8(
        path.basename(ui.file_path).encode("utf-8"),
        256
    ).ljust(256, b"\x00")  # 256 byte

    # code 4bb + salt + sha + len 8 + name 256b = 332
    # [code4][salt32][sha32][len8][name256][data]
    head_length: int = 4 + 32 + 32 + 8 + 256
    data_length: int = head_length + compressed_file_length
    side_length: int = get_square_ge((data_length + 3)  // 4)

    b_compressed_file[:0] = bytearray(head_length)
    data: bytearray = b_compressed_file
    data_length: int = len(data)

    data[0:4] = format_stub_code

    target_bytes: int = side_length * side_length * 4
    if data_length < target_bytes:
        data.extend(b"\x00" * (target_bytes - data_length))

    b_password: bytes = normalize("NFC", password).encode("utf-8")
    salt_buffer: np.ndarray = np.frombuffer(
        data,
        dtype=np.uint8,
        count=32,
        offset=4 # 4 + 32 = 36
    )
    sha_buffer: np.ndarray = np.frombuffer(
        data,
        dtype=np.uint8,
        count=32,
        offset=36 # 36 + 32 = 68
    )

    data[68:76] = b_compressed_file_length # 68 + 8 = 76
    data[76:332] = b_filename # 76 + 256 = 332

    buffer: np.ndarray = np.frombuffer(
        data,
        dtype=np.uint8,
        count=len(data) - 68,
        offset=68
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
        np.frombuffer(
            data, dtype=np.uint8
        ).reshape(
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

class Decoder:
    def decode(self, ui: UI) -> None:
        ui.set_tooltip_info("")
        password: str = ui.get_password()

        if not password.isprintable():
            ui.set_loading_info("错误：密码包含不可打印字符。")
            return

        if any(category(char) in ("Cf",) for char in password):
            ui.set_loading_info("错误：密码包含不可见字符。")
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
            image: Image.Image = Image.open(ui.file_path)
        except Exception as e:
            ui.set_loading_info(f"文件错误：{e}")
            return

        ui.set_loading_info("运行进度：正在还原数据。")
        data: np.ndarray = np.array(image.convert("RGBA"), dtype=np.uint8).ravel()
        format_stub_code: bytes = data.data[:4].tobytes() # 4 byte

        if format_stub_code[0:3] == b"\x00\x00\x00":
            return self._decode_x000000(ui, data)
        
        ui.set_loading_info(f"不受支持的版本：{format_stub_code.hex()}")

    def _decode_x000000(self, ui: UI, data: np.ndarray) -> None:
        ui.set_loading_info("运行进度：正在解密数据。")

        salt: np.ndarray = np.frombuffer(
            data,
            dtype=np.uint8,
            count=32,
            offset=4
        )
        mac: np.ndarray = np.frombuffer(
            data,
            dtype=np.uint8, 
            count=32,
            offset=36
        )
        buffer: np.ndarray = np.frombuffer(
            data,
            dtype=np.uint8,
            count=len(data) - 68,
            offset=68
        )

        b_password: bytes = normalize("NFC", ui.get_password()).encode("utf-8")
        try:
            decryption(b_password, buffer, salt, mac)
        except ValueError as e:
            ui.set_loading_info(f"{e}")
            ui.set_tooltip_info(f"{e}")
            return
        
        b_buffer: memoryview = buffer.data
        compressed_file_length: int = int.from_bytes(b_buffer[:8])
        filename: str = bytes(b_buffer[8:264]).decode("utf-8").rstrip("\x00")

        b_compressed_data: memoryview = b_buffer[264:264 + compressed_file_length]
        compress_type_index: int = data[3]  # format_stub_code[3]
        if compress_type_index == 0:
            file_data: bytearray = bytearray(b_compressed_data)
        elif compress_type_index == 1:
            file_data: bytearray = zlib_decompress(b_compressed_data)
        elif compress_type_index == 2:
            file_data: bytearray = bz2_decompress(b_compressed_data)
        elif compress_type_index == 3:
            file_data: bytearray = lzma_decompress(b_compressed_data)
        else:
            ui.set_loading_info("错误：不受支持的压缩方案。")
            return

        ui.set_loading_info("运行进度：正在保存文件。")
        save_file_path: str = path.join(ui.dir_path, filename) # type: ignore
        try:
            with open(save_file_path, mode="wb") as f:
                f.write(file_data)
        except Exception as e:
            ui.set_loading_info(f"文件错误：{e}")
            return
        upper_file_path: str = get_upper_drive(save_file_path)
        ui.set_loading_info(f"解码完成。保存于{upper_file_path}")
        ui.set_tooltip_info(upper_file_path)

def decode(ui: UI) -> None:
    decoder: Decoder = Decoder()
    decoder.decode(ui)