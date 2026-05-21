import numpy as np
from cryption import encryption, decryption  # 替换为你的模块名

# 测试1：基本加解密
print("测试1：基本加解密")
password = b"async"
plaintext = b"Hello, this is a test message!"
data = np.frombuffer(plaintext, dtype=np.uint8).copy()
salt_buf = np.empty(32, dtype=np.uint8)
mac_buf = np.empty(32, dtype=np.uint8)

original = data.copy()

encryption(password, data, salt_buf, mac_buf)
decryption(password, data, salt_buf, mac_buf)

if np.array_equal(original, data):
    print("✓ 通过")
else:
    print("✗ 失败")

# 测试2：空数据
print("\n测试2：空数据")
data = np.frombuffer(b"", dtype=np.uint8).copy()
salt_buf = np.empty(32, dtype=np.uint8)
mac_buf = np.empty(32, dtype=np.uint8)

encryption(password, data, salt_buf, mac_buf)
decryption(password, data, salt_buf, mac_buf)

if len(data) == 0:
    print("✓ 通过")
else:
    print("✗ 失败")

# 测试3：大数据（1MB+）
print("\n测试3：大数据（2MB）")
large_data = np.random.bytes(2_000_000)
data = np.frombuffer(large_data, dtype=np.uint8).copy()
salt_buf = np.empty(32, dtype=np.uint8)
mac_buf = np.empty(32, dtype=np.uint8)

original = data.copy()

encryption(password, data, salt_buf, mac_buf)
decryption(password, data, salt_buf, mac_buf)

if np.array_equal(original, data):
    print("✓ 通过")
else:
    print("✗ 失败")

# 测试4：篡改检测
print("\n测试4：篡改检测")
data = np.frombuffer(b"Test message", dtype=np.uint8).copy()
salt_buf = np.empty(32, dtype=np.uint8)
mac_buf = np.empty(32, dtype=np.uint8)

encryption(password, data, salt_buf, mac_buf)
data[10] ^= 0xFF  # 篡改密文

try:
    decryption(password, data, salt_buf, mac_buf)
    print("✗ 失败：未检测到篡改")
except ValueError as e:
    print(f"✓ 通过：{e}")

# 测试5：不同密码
print("\n测试5：不同密码")
data = np.frombuffer(b"Secret message", dtype=np.uint8).copy()
salt_buf = np.empty(32, dtype=np.uint8)
mac_buf = np.empty(32, dtype=np.uint8)
original = data.copy()

encryption(b"correct_password", data, salt_buf, mac_buf)

try:
    decryption(b"wrong_password", data, salt_buf, mac_buf)
    print("✗ 失败：错误密码解密成功")
except ValueError:
    print("✓ 通过：错误密码被拒绝")