import tkinter as tk
from tkinter.ttk import Combobox
from tkinter.filedialog import askdirectory, askopenfilename

from PIL import Image
from PIL.ImageTk import PhotoImage

from io import BytesIO
from os import path
from base64 import b64decode
from threading import Thread

from data import icon_b64, workspace, CompressType, compress_types
from util import Tooltip
from core import encode, decode

class UI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("FileToImage")
        self.root.geometry("250x170")
        self.root.resizable(False, False)
        self.root.eval("tk::PlaceWindow . center")

        self.file_path: str = ""
        self.dir_path: str = workspace
        self.processing: bool = False
        self.compress: dict[CompressType, int] = {
            "raw": 2,
            "zlib": 6,
            "bz2": 6, 
            "lzma": 6
        }

        with BytesIO(b64decode(icon_b64)) as file:
            self.icon: PhotoImage = PhotoImage(Image.open(file))

        self.root.iconphoto(True, self.icon) # pyright: ignore[reportArgumentType]
        self.ui_init()
        self.show_password_check()

        self.set_loading_info("喵喵喵~")

    def set_file_path(self) -> None:
        result: str = path.normpath(askopenfilename())
        if result and result != ".":
            self.file_path = result
            self.set_loading_info(f"文件：{path.basename(self.file_path)}")
            self.set_tooltip_info(self.file_path)

    def set_dir_path(self) -> None:
        result: str = path.normpath(askdirectory())
        if result and result != ".":
            self.dir_path = result
            self.set_loading_info(f"目录：{self.dir_path}")

    def ui_init(self) -> None:
        tk.Label(self.root, text="Author：INF").place(x=10, y=5)
        self.file_button = tk.Button(self.root, text="文件", command=lambda: self.set_file_path())
        self.file_button.place(x=10, y=40)
        self.dir_button = tk.Button(self.root, text="目录", command=lambda: self.set_dir_path())
        self.dir_button.place(x=10, y=80)

        self.encode_button = tk.Button(self.root, text="编码", command=lambda: Thread(
            target=self.p_encode, args=(), daemon=True).start())
        self.encode_button.place(x=50, y=40)
        self.decode_button = tk.Button(self.root, text="解码", command=lambda: Thread(
            target=self.p_decode, args=(), daemon=True).start())
        self.decode_button.place(x=50, y=80)

        self.loading_text = tk.Label(self.root)
        self.loading_text.place(x=10, y=115)
        self.loading_text_tooltip: Tooltip = Tooltip(self.loading_text, hover_text="", delay=300)

        tk.Label(self.root, text=f"密钥：").place(x=10, y=140)
        self.password_entry = tk.Entry(self.root, width=18, font="Consolas")
        self.password_entry.place(x=48, y=142)

        self.show_password = tk.BooleanVar(value=True)
        tk.Checkbutton(self.root, variable=self.show_password,
            command=self.show_password_check, state="active").place(x=220, y=140)

        self.compress_type_combobox = Combobox(
            self.root, state="readonly", width=6,
            values=compress_types, # pyright: ignore[reportArgumentType]
        )
        self.compress_type_combobox.current(0)
        self.compress_type_combobox.place(x=110, y=42)
        self.compress_type_combobox.bind("<<ComboboxSelected>>", self.compress_type_selected)

        self.compress_level_combobox = Combobox(
            self.root, state="readonly", width=2,
            values=list(map(str, range(10))),
        )

        self.compress_level_combobox.current(2)
        self.compress_level_combobox.place(x=180, y=42)
        self.compress_level_combobox.bind("<<ComboboxSelected>>", self.compress_level_selected)

    def run(self) -> None:
        self.root.mainloop()

    def show_password_check(self) -> None:
        self.password_entry.config(show="*" if self.show_password.get() else "")

    def set_loading_info(self, text: str) -> None:
        self.root.after(0, lambda: self._update_loading_text(text))

    def _update_loading_text(self, text: str) -> None:
        if len(text) >= 30:
            text = text[:27] + "..."
        self.loading_text.config(text=text)

    def set_tooltip_info(self, text: str) -> None:
        self.root.after(0, lambda: self._update_tooltip_text(text))

    def _update_tooltip_text(self, text: str) -> None:
        self.loading_text_tooltip.config(hover_text=text)

    def get_password(self) -> str:
        return self.password_entry.get()

    def p_encode(self) -> None:
        if self.processing:
            return
        
        self.processing = True
        self.root.after(0, lambda: self._lock_buttons())
        try:
            encode(ui=self) # TODO
        except Exception as err:
            self.set_loading_info(f"异常：{err}")
        finally:
            self.processing = False
            self.root.after(0, lambda: self._unlock_buttons())

    def p_decode(self) -> None:
        if self.processing:
            return
        
        self.processing = True
        self.root.after(0, lambda: self._lock_buttons())
        try:
            decode(ui=self) # TODO
        except Exception as err:
            self.set_loading_info(f"异常：{err}")
        finally:
            self.processing = False
            self.root.after(0, lambda: self._unlock_buttons())

    def _lock_buttons(self) -> None:
        self.encode_button.config(state="disabled")
        self.decode_button.config(state="disabled")
        self.file_button.config(state="disabled")
        self.dir_button.config(state="disabled")

    def _unlock_buttons(self) -> None:
        self.encode_button.config(state="normal")
        self.decode_button.config(state="normal")
        self.file_button.config(state="normal")
        self.dir_button.config(state="normal")

    def get_compress_settings(self) -> tuple[CompressType, int]:
        compress_type: CompressType = self.compress_type_combobox.get() # pyright: ignore[reportAssignmentType]
        return compress_type, self.compress[compress_type]

    def compress_type_selected(self, event):
        compress_type: str = self.compress_type_combobox.get()
        self.compress_level_combobox.set(self.compress[compress_type]) # pyright: ignore[reportArgumentType]

    def compress_level_selected(self, event):
        compress_type: str = self.compress_type_combobox.get()
        self.compress[compress_type] = int(self.compress_level_combobox.get()) # pyright: ignore[reportArgumentType]

if __name__ == "__main__":
    ui = UI()
    ui.run()