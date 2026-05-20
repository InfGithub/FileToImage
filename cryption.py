import numpy as np
from os import urandom
from hashlib import shake_256, sha256

def encryption(
    password: bytes,
    buffer: np.ndarray,
    salt_buffer: np.ndarray,
    chunk_size: int = 1048576
):

    salt: bytes = urandom(32)
    salt_buffer[:] = memoryview(salt)
    password_hashed: bytes = sha256(password).digest()

    for index in range(0, buffer.size, chunk_size):
        end: int = min(index + chunk_size, buffer.size)
        chunk_context: bytes = password_hashed + salt + index.to_bytes(8, "big")
        chunk_keystream: bytes = shake_256(chunk_context).digest(end - index)
        key_stream: np.ndarray = np.frombuffer(chunk_keystream, dtype=np.uint8)
        buffer[index:end] = np.bitwise_xor(buffer[index:end], key_stream)


def decryption(
    password: bytes,
    buffer: np.ndarray,
    salt_buffer: np.ndarray,
    chunk_size: int = 1048576
):

    password_hashed: bytes = sha256(password).digest()
    context: bytes = password_hashed + salt_buffer.tobytes()

    for index in range(0, buffer.size, chunk_size):
        end: int = min(index + chunk_size, buffer.size)
        chunk_context: bytes = context + index.to_bytes(8, "big")
        chunk_keystream: bytes = shake_256(chunk_context).digest(end - index)
        key_stream: np.ndarray = np.frombuffer(chunk_keystream, dtype=np.uint8)
        buffer[index:end] = np.bitwise_xor(buffer[index:end], key_stream)