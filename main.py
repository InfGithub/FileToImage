import numpy as np
from cryption import encryption, decryption

password = b"async"
plaintext = b"Hello World"
salt_buffer = np.empty(32, dtype=np.uint8)

original = np.frombuffer(plaintext, dtype=np.uint8).copy()
buffer = original.copy()

encryption(password, buffer, salt_buffer)
decryption(password, buffer, salt_buffer)

if np.array_equal(original, buffer):
    print("通过")
else:
    print("失败")