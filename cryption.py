import numpy as np
from os import urandom
from hashlib import shake_256, sha256

def cryption(
    password: bytes,
    buffer: np.ndarray,
    salt_buffer: np.ndarray
) -> None:
    base_sponge = shake_256()
    base_sponge.update(password)
    base_sponge.update(salt_buffer)

    for index in range(0, buffer.size, 1_048_576):
        end: int = min(index + 1_048_576, buffer.size)
        chunk_sponge = base_sponge.copy()
        chunk_sponge.update(index.to_bytes(length=8))
        buffer[index:end] ^= np.frombuffer(chunk_sponge.digest(end - index), dtype=np.uint8)

def encryption(
    password: bytes,
    buffer: np.ndarray,
    salt_buffer: np.ndarray,
    mac_buffer: np.ndarray
) -> None:
    salt: bytes = urandom(32)
    salt_buffer[:] = memoryview(salt)

    cryption(password, buffer, salt_buffer)

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
) -> None:
    mac = sha256()
    mac.update(password)
    mac.update(buffer)
    mac.update(salt_buffer)

    if not np.array_equal(mac_buffer, np.frombuffer(mac.digest(), dtype=np.uint8)):
        raise ValueError("Warning - Data has been tampered with")

    cryption(password, buffer, salt_buffer)