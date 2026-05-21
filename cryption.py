import numpy as np
from os import urandom
from hashlib import shake_256, sha256

def encryption(
    password: bytes,
    buffer: np.ndarray,
    salt_buffer: np.ndarray,
    mac_buffer: np.ndarray
):
    salt: bytes = urandom(32)
    salt_buffer[:] = memoryview(salt)

    for index in range(0, buffer.size, 1_048_576):
        end: int = min(index + 1_048_576, buffer.size)
        chunk_keystream = shake_256()
        chunk_keystream.update(password)
        chunk_keystream.update(salt_buffer)
        chunk_keystream.update(index.to_bytes(length=8))
        key_stream: np.ndarray = np.frombuffer(chunk_keystream.digest(end - index), dtype=np.uint8)
        buffer[index:end] = np.bitwise_xor(buffer[index:end], key_stream)

    mac = sha256()
    mac.update(password)
    mac.update(buffer)
    mac.update(salt_buffer)
    mac_buffer[:] = memoryview(mac.digest())


def decryption(
    password: bytes,
    buffer: np.ndarray,
    salt_buffer: np.ndarray,
    mac_buffer: np.ndarray
):
    mac = sha256()
    mac.update(password)
    mac.update(buffer)
    mac.update(salt_buffer)

    if not np.array_equal(mac_buffer, np.frombuffer(mac.digest(), dtype=np.uint8)):
        raise ValueError("Warning - Data has been tampered with")

    for index in range(0, buffer.size, 1_048_576):
        end: int = min(index + 1_048_576, buffer.size)
        chunk_keystream = shake_256()
        chunk_keystream.update(password)
        chunk_keystream.update(salt_buffer)
        chunk_keystream.update(index.to_bytes(length=8))
        key_stream: np.ndarray = np.frombuffer(chunk_keystream.digest(end - index), dtype=np.uint8)
        buffer[index:end] = np.bitwise_xor(buffer[index:end], key_stream)