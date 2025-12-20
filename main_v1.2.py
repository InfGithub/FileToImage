import tkinter as tk, numpy as np
from io import BytesIO
from os import path, urandom
from PIL import Image, ImageTk, ImageFile
from math import ceil, sqrt
from base64 import b64decode
from typing import Optional
from hashlib import md5 as md5_checksum, sha256
from threading import Thread
from tkinter.filedialog import askdirectory, askopenfilename

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None

def get_version_text(version: tuple[int, int]) -> str:
    return ".".join([item.__str__() for item in version])

def get_version_tuple(version: str) -> tuple[int, int]:
    return tuple([int(item) for item in version.split(".")])

def get_sqrt(value: float) -> int:
    return ceil(sqrt(value))

class Tooltip:
    def __init__(self, widget: tk.Widget, hover_text: str = "", delay: int = 100) -> None:
        self.widget, self.hover_text, self.delay = widget, hover_text, delay
        self.tip_window: Optional[tk.Toplevel] = None
        self.tip_id: Optional[str] = None

        widget.bind("<Enter>", self.schedule_tip)
        widget.bind("<Leave>", self.hide_tip)
        widget.bind("<ButtonPress>", self.hide_tip)

    def schedule_tip(self, event: tk.Event) -> None:
        if not self.hover_text:
            return
        self.tip_id = self.widget.after(self.delay, self.show_tip)

    def show_tip(self) -> None:
        if self.tip_window or not self.hover_text:
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")

        frame = tk.Frame(self.tip_window, relief="solid", borderwidth=1)
        frame.pack()
        
        tk.Label(frame, text=self.hover_text, justify="left", relief="flat", padx=4, pady=2).pack()
        
        self.adjust_position()
    
    def adjust_position(self) -> None:
        if not self.tip_window:
            return
        
        self.tip_window.update_idletasks()
        width = self.tip_window.winfo_width()
        height = self.tip_window.winfo_height()
        x, y = self.tip_window.winfo_x(), self.tip_window.winfo_y()
        
        screen_width = self.tip_window.winfo_screenwidth()
        screen_height = self.tip_window.winfo_screenheight()
        
        if x + width > screen_width:
            x = screen_width - width - 10
        if y + height > screen_height:
            y = screen_height - height - 10
        
        self.tip_window.wm_geometry(f"+{max(0, x)}+{max(0, y)}")
    
    def hide_tip(self, event: Optional[tk.Event] = None) -> None:
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None
        if self.tip_id:
            self.widget.after_cancel(self.tip_id)
            self.tip_id = None
    
    def config(self, hover_text: Optional[str] = None) -> None:
        if hover_text is not None:
            self.hover_text = hover_text
        self.hide_tip()

class UI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FileToImage")
        self.root.geometry("250x170+648+648")
        self.root.eval("tk::PlaceWindow . center")

        with BytesIO(b64decode(Config.icon_b64_data)) as file:
            self.icon = ImageTk.PhotoImage(Image.open(file))

        self.root.iconphoto(True, self.icon)

        self.ui_init()
        self.set_loading_info("喵喵喵~")
        self.show_password_check()


    def ui_init(self):
        tk.Label(self.root, text=f"Author：INF\tVersion：{get_version_text(Config.version)}").place(x=10, y=5)

        tk.Button(self.root, text="选择文件", command=get_file_path).place(x=10, y=40)
        tk.Button(self.root, text="选择目录", command=get_dir_path).place(x=10, y=80)
        tk.Button(self.root, text="编码", command=lambda: Thread(target=encode, args=(self,)).start()).place(x=80, y=40)
        tk.Button(self.root, text="解码", command=lambda: Thread(target=decode, args=(self,)).start()).place(x=80, y=80)

        self.loading_text = tk.Label(self.root)
        self.loading_text.place(x=10, y=115)
        self.tooltip = Tooltip(self.loading_text)

        tk.Label(self.root, text=f"密钥：").place(x=10, y=140)
        self.password_entry = tk.Entry(self.root, width=18, font="Consolas")
        self.password_entry.place(x=48, y=142)

        self.show_password = tk.BooleanVar(value=True)
        tk.Checkbutton(self.root, variable=self.show_password,
            command=self.show_password_check, state="active").place(x=220, y=140)

    def set_loading_info(self, text: str):
        if len(text) >= 30:
            text: str = f"{text[:30]}..."
        self.loading_text.config(text=text)

    def show_password_check(self):
        self.password_entry.config(show="*" if self.show_password.get() else "")

    def run(self):
        self.root.mainloop()

def get_dir_path():
    Config.dir_path = path.normpath(askdirectory())

def get_file_path():
    Config.file_path = path.normpath(askopenfilename())

def get_path_with_upper_drive(file_path: str):
    drive, tail = path.splitdrive(file_path)
    return drive.upper() + tail if drive else file_path

def encryption(password: bytes, data: np.ndarray, chunk_size: int = 1048576):

    salt = urandom(16)
    salt_array = np.frombuffer(salt, dtype=np.uint8)

    key = np.frombuffer(sha256(password + salt).digest(), dtype=np.uint8)
    result = [salt_array, data]

    for index in range(0, data.size, chunk_size):
        end = min(index + chunk_size, data.size)
        key_stream = np.resize(key, end - index)
        data[index:end] = np.bitwise_xor(data[index:end], key_stream)

    return np.concatenate(result)

def decryption(password: bytes, data: np.ndarray, chunk_size: int = 1048576):
    salt, data = data[:16], data[16:]

    key = np.frombuffer(sha256(password + salt.tobytes()).digest(), dtype=np.uint8)
    for index in range(0, data.size, chunk_size):
        end = min(index + chunk_size, data.size)
        key_stream = np.resize(key, end - index)
        data[index:end] = np.bitwise_xor(data[index:end], key_stream)

    return data

def encode(ui: UI):
    ui.tooltip.config("")
    password: str = ui.password_entry.get()

    if not password.isascii():
        ui.set_loading_info("错误：密钥不得包含非ASCII字符。")
        return

    ui.set_loading_info("运行进度：正在读取文件。")

    if Config.file_path is None:
        ui.set_loading_info("错误：未指定文件。")
        return
    
    if not path.exists(Config.file_path):
        ui.set_loading_info(f"错误：{Config.file_path}不存在。")
        return

    if Config.dir_path is None:
        ui.set_loading_info("错误：未指定目录。")
        return
    
    if not path.exists(Config.dir_path):
        ui.set_loading_info(f"错误：{Config.dir_path}不存在。")
        return
    
    try:
        with open(Config.file_path, mode="rb") as f:
            data_rb: bytearray = bytearray(f.read())
    except Exception as e:
        ui.set_loading_info(f"文件错误：{e}")
        return

    try:
        ui.set_loading_info("运行进度：正在组织信息。")
        version_rb: bytes = get_version_text(Config.version).encode("utf-8")
        filename_rb: bytes = path.basename(Config.file_path).encode("utf-8")
        data_rb_length: int = len(data_rb)
        data_rb_length_rb: bytes = str(data_rb_length).encode("utf-8")
        md5_checksum_rb: bytes = md5_checksum(data_rb).hexdigest().encode("utf-8")
        separator: bytes = Config.spliter
        sep_length: int = len(separator)
        header_parts: list[bytes] = [version_rb, filename_rb, data_rb_length_rb, md5_checksum_rb]
        header_length: list[int] = [len(item) for item in header_parts]
        header_total: int = sum(header_length) + sep_length * 4
        total_length: int = header_total + data_rb_length + 16
        
        ui.set_loading_info("运行进度：正在编码信息。")
        side_length: int = get_sqrt((total_length + 3) // 4)
        target_size: int = side_length * side_length * 4 - 16
        data_rb[:0] = b"\x00" * header_total
        offset: int = 0
        for index, item in enumerate(header_parts):
            data_rb[offset:offset + header_length[index]] = item
            offset += header_length[index]
            data_rb[offset:offset + sep_length] = separator
            offset += sep_length
        data_rb.extend(b"\x00" * (target_size - data_rb_length))
        result_arr: np.ndarray = np.frombuffer(data_rb, dtype=np.uint8)[:target_size]
        
        ui.set_loading_info("运行进度：正在加密数据。")
        result_arr = encryption(
            password=password.encode("ascii"),
            data=result_arr, chunk_size=1048576
        )
        
        ui.set_loading_info("运行进度：正在映射图像。")
        result_image: Image.Image = Image.fromarray(
            result_arr.reshape(side_length, side_length, 4), mode="RGBA")
        
        ui.set_loading_info("运行进度：正在保存文件。")
        filename_without_ext: str = path.splitext(path.basename(Config.file_path))[0]
        save_file_path: str = path.join(Config.dir_path, f"{filename_without_ext}.png")
        result_image.save(
            save_file_path, format="PNG",
            compress_level=2, optimize=False,
            pnginfo=None, icc_profile=None
        )
        
        upper_file_path: str = get_path_with_upper_drive(save_file_path)
        ui.set_loading_info(f"编码完成。保存于{upper_file_path}。")
        ui.tooltip.config(upper_file_path)
        
    except MemoryError as e:
        ui.set_loading_info(f"内存不足：{e}")
    except Exception as e:
        ui.set_loading_info(f"编码错误：{e}")

def decode(ui: UI):
    ui.tooltip.config("")
    password: str = ui.password_entry.get()

    if not password.isascii():
        ui.set_loading_info("错误：密钥不得包含非ASCII字符。")
        return

    ui.set_loading_info("运行进度：正在读取文件。")

    if Config.file_path is None:
        ui.set_loading_info("错误：未指定文件。")
        return
    
    if not path.exists(Config.file_path):
        ui.set_loading_info(f"错误：{Config.file_path}不存在。")
        return

    if Config.dir_path is None:
        ui.set_loading_info("错误：未指定目录。")
        return
    
    if not path.exists(Config.dir_path):
        ui.set_loading_info(f"错误：{Config.dir_path}不存在。")
        return
    
    try:
        image: Image.Image = Image.open(Config.file_path)
    except Exception as e:
        ui.set_loading_info(f"文件错误：{e}")
        return

    try:
        ui.set_loading_info("运行进度：正在还原数据。")
        rgba_array: np.ndarray = np.array(image.convert("RGBA"), dtype=np.uint8)
        data_rb_flat_arr: np.ndarray = rgba_array.ravel()

        ui.set_loading_info("运行进度：正在解密数据。")
        data_rb_flat_arr = decryption(
            password=password.encode("ascii"),
            data=data_rb_flat_arr, chunk_size=1048576
        )

        data_rb_full: bytes = data_rb_flat_arr.tobytes()
        version_rb, filename_rb, data_rb_length_rb, md5_checksum_rb, *data_rb = data_rb_full.split(Config.spliter)
        data_rb: bytes = Config.spliter.join(data_rb)

        ui.set_loading_info("运行进度：正在解析数据。")
        version: tuple[int, int] = get_version_tuple(version_rb.decode("utf-8"))
        filename: str = filename_rb.decode("utf-8")
        data_rb_length: int = int(data_rb_length_rb.decode("utf-8"))
        data_md5_checksum_value: str = md5_checksum_rb.decode("utf-8")
        data_rb_unfull: bytes = data_rb[:data_rb_length]

        ui.set_loading_info("运行进度：正在验证数据。")
        md5_checksum_value: str = md5_checksum(data_rb_unfull).hexdigest()
        md5_checksum_right: bool = data_md5_checksum_value == md5_checksum_value

        if not md5_checksum_right:
            ui.set_loading_info("MD5值异常，图片数据可能已损坏。")
            return
        
        ui.set_loading_info("运行进度：正在保存文件。")
        save_file_path: str = path.join(Config.dir_path, filename)
        try:
            with open(save_file_path, mode="wb") as f:
                f.write(data_rb_unfull)
        except Exception as e:
            ui.set_loading_info(f"文件错误：{e}")
            return

        upper_file_path: str = get_path_with_upper_drive(save_file_path)
        ui.set_loading_info(f"解码完成。保存于{upper_file_path}。")
        ui.tooltip.config(upper_file_path)
    except Exception as e:
        ui.set_loading_info(f"编码错误：{e}")

class Config:
    version: tuple[int, int] = (1, 2)

    icon_b64_data: str = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAAACXBIWXMAAABHAAAARAAbKp\
bnAAADG0lEQVR4nAEQA+/8AOCoccyUXd+pf8mTaYyEgY+HhIq813qsx6LDyrrb4tmlf7+LZdCJV9GKWNKEVc1/UADhpW3QlF\
zDil7co3eSoqZ4iIyTnK+EjaB0iJOitsHO0LzGyLTr0q7t1LDn3cbo3scA6a+Do2k9nVdBoFpEh4aQkZCau5aH2bSlmZeanJ\
qdx6+pmoJ8zG1Lz3BOwI1xxZJ2AOqrgqVmPapYRLFfS4Fwdo59g9q4ofPRusvDwK6mo7KssnFrcchePt91VdVuR9VuRwDjon\
m2dUyRZWCQZF+vk4fCpprasIr3zafWzcrGvbqQnq15h5bHYETXcFTScE/WdFMA3JtzuHdPkmNdypuV49PIuamejoSHm5GUj4\
aLmZCVgJ20bImgil1efE9QhVBOe0ZEAOeVca9dOdVDNthGOZqPmYuAipSLknJpcIKLlqKrtpW0y36dtFlnhkNRcE9OZEtKYA\
DfmXmTTS2nLSa4PjeHgIm1rrfSz8rc2dTg5ua9w8PSs7qSc3qCeqNqYotXV3ViYoAA2JuCiUwzfygln0hFypaMtYF3ubizx8\
bBxsXEo6Khr1RTn0RDnmyPkmCDimeHmXaWANWUeqxrUYEpK4QsLrZMRZAmH5F0a+3Qx9vZ2pqYmZE9PpZCQ69zjrV5lK99or\
WDqADHk322gmykW1mTSkiSR0itYmOpoZ7p4d7W5urY6Oy6n5y6n5zVrKrYr63Woa3JlKAA14RzrltKy2VavlhNb1JOzbCs6/\
Tx2uPgrr3HipmjwqidxKqfvJmM2bap2q6tzaGgANKGdaVZSLhIPrBANm9DQsqendTo6cnd3svCw56Vlsallbybi8Sop7+jos\
yfoseanQC/j4Sre3DDjGjFjmqHgHatppzB2OKftsCnoaPJw8Xk29xqYWI3RFhVYnbNsq3hxsEAt5WOknBplmpFsoZh1ap/tY\
pfoLfIobjJpYeB2bu1pKKjRkRFYWluhIyRgV9gspCRAIx2b2tVTlJCQnNjY4ZwaWhSS0xjcWZ9i4uSn5CXpFJQVURCR2VlZ7\
a2uI19f1lJS0nSufWWhUvLAAAAAElFTkSuQmCC"

    dir_path: str = path.dirname(path.abspath(__file__))
    file_path: str = None
    spliter: bytes = "<<<INF>>>".encode("utf-8")

def main():
    app = UI()
    app.run()


if __name__ == "__main__":
    main()