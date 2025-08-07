# Everything started at here!
import math, tkinter as tk, os, base64, time
from tkinter import ttk, filedialog
from PIL import Image, ImageFile, ImageTk
from threading import Thread
from io import BytesIO

image_data = b"""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABp0lEQVR4AaTS3StDYRwH8O85O9pm7RhLCgsJmdcLiSTlwgUp4sIVl1IuXGn/
gbgiUm7dKVGSpLykCLlALOR9p8V2hm3nLLadc7C22smzWXkunvff53ml8c/0J1BSXt+RbI2kgLW8VjGkYbWsuNKbCEkIlNQ1KWP9dZjqskIjfbCHszUKCUkI9LVYE
GS0kGRguq0GgpcixYMI2GxDmXqtBsdX95i3P2DF84yeCUfqwPr6/sNnSIK5qBpdDRXIEd4xPpCdOiBQbOPp3gl0Whp3ciY23DT8JgNR+HWEZmuFUmXJuuDTLTjaWs
PC4gKuOQ6Lq09u0hZUwPBg92RnbwsCB9sQ/D64GAtyKQUSpcGZXSTFqy9xZm55ZHTXnnZsLoU5rxjORwdOz0UEgwryTam+ws5O2OB3wbF5iMAtj5/HD/kCeJXzW0l
bUB0hNoF7eYEnKx0CK+OJDkLOMKG9gLbFxuNLIsDmFkKSwnA5nZTOmAFGb8TSpastPjBWJwKMyEPkriNzxGe/kdVT0DHfXzLSo86IAM97qJAsRW/NLXA3VxTveYu2
1cAXAAAA///KMmNRAAAABklEQVQDANeqkiHWEMo+AAAAAElFTkSuQmCC""".replace(b"\n", b"")

VERSION: str = "0.9"
COMPATMODE: bool = False
compat_versions: list[str] = ["0.8"]
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None
split: str = "<<<INF>>>"
null_color: tuple = (30, 42, 227, 79)

def get_sqrt(value: int):
    return math.ceil(math.sqrt(value))

def encode(path: str, save_path: str, password: list[int]):
    update_loading(0.00, f"运行进度：正在读取文件......")
    start_time: float = time.time()

    with open(path, mode="rb") as f:
        file = f.read()
        file = (path.split("\\")[-1] + split + VERSION + split + str(len(file))+ split).encode("utf-8") + file + split.encode("utf-8")

    value: int = get_sqrt(len(file)/4)
    img = Image.new('RGBA', [value, value], color=None)
    pixel = img.load()

    if sum(password) == 0:
        for tx in range(0, value):
            for ty in range(0, value):
                intvar = (ty*value+tx)*4
                try:
                    pixel[tx, ty] = tuple([i for i in [file[intvar+id] for id in range(0, 4)]])
                except:
                    pixel[tx, ty] = null_color
            var=(tx+1) / value
            update_loading(var, f"运行进度：{round(var*100, 2)}%")

    else:
        for tx in range(0, value):
            for ty in range(0, value):
                intvar = (ty*value+tx)*4
                try:
                    pixel[tx, ty] = tuple([i if i<256 else i-256 for i in [file[intvar+id]+password[id] for id in range(0, 4)]])
                except:
                    pixel[tx, ty] = null_color
            var=(tx+1) / value
            update_loading(var, f"运行进度：{round(var*100, 2)}%")

    update_loading(1.00, f"运行进度：正在保存文件......")
    
    img.save(os.path.join(save_path, os.path.splitext(os.path.basename(path))[0] + ".png"))
    update_loading(1.00, f"运行进度：编码完成，用时{round(time.time()-start_time, 2)}s.")

def decode(path: str, save_path: str, password: list[int]):
    update_loading(0.00, f"运行进度：正在读取文件......")
    start_time: float = time.time()

    img = Image.open(path)
    pixel = img.load()
    file = list()

    if sum(password) == 0:
        for ty in range(0, img.size[0]):
            for tx in range(0, img.size[1]):
                for i, byte in enumerate(pixel[tx, ty]):
                    file.append(byte)
            var = (ty+1) / img.size[0]
            update_loading(var, f"运行进度：{round(var*100, 2)}%")

    else:
        for ty in range(0, img.size[0]):
            for tx in range(0, img.size[1]):
                for i, byte in enumerate(pixel[tx, ty]):
                    ba = byte-password[i]
                    file.append(ba+256 if ba<0 else ba)
            var = (ty+1) / img.size[0]
            update_loading(var, f"运行进度：{round(var*100, 2)}%")

    file = bytes(file)
    info = file.split(split.encode("utf-8"))

    try:
        def error_info(info):
            update_loading(0.00, f"程序版本异常 ⚠ 需求版本：{info[1]}")
        try:
            if (info[1] == VERSION.encode("utf-8")) or COMPATMODE or info[1] in [i.encode("utf-8") for i in compat_versions]:
                update_loading(1.00, f"运行进度：正在保存文件......")
                with open(os.path.join(save_path, info[0].decode("utf-8")), mode="wb") as f:
                    f.write(split.encode("utf-8").join(info[3:])[0: int(info[2].decode("utf-8"))])
                update_loading(1.00, f"运行进度：解码完成，用时{round(time.time()-start_time, 2)}s.")
            else:
                error_info(info)
        except:
            error_info(info)
    except:
        update_loading(0.00, f"密钥异常 ⚠ 请填写正确密钥")

def update_loading(value, text: str):
    loading['value'] = value
    loading_text.config(text=text)
    root.update_idletasks()

if __name__=="__main__":
    root = tk.Tk()
    root.geometry("250x210+648+648")
    root.title("FileToImage")
    file_path = None
    path = os.path.dirname(os.path.abspath(__file__))
    powerful = pow(2, 32)-1

    def split_string(s):
        part_len = len(s) // 4
        return [int(s[i:i+part_len], 2) for i in range(0, len(s), part_len)]

    def file_path_get():
        global file_path
        file_path = os.path.normpath(filedialog.askopenfilename())

    def path_get():
        global path
        path = os.path.normpath(filedialog.askdirectory()) + os.sep

    def password_get():
        pw = pw_entry.get()
        try:
            pw = abs(int(pw))
            if pw>powerful:
                pw = powerful
        except:
            pw = 0
        return split_string(bin(pw)[2:].zfill(32))


    tk.Label(root, text=f"File to Image    作者：INF    版本：{VERSION}").place(x=10, y=5)
    tk.Button(root, text="选择文件", command=file_path_get).place(x=10, y=40)
    tk.Button(root, text="选择路径", command=path_get).place(x=10, y=80)
    tk.Button(root, text="编码", command=lambda: Thread(target=encode, args=(file_path, path, password_get())).start()).place(x=80, y=40)
    tk.Button(root, text="解码", command=lambda: Thread(target=decode, args=(file_path, path, password_get())).start()).place(x=80, y=80)

    loading_text = tk.Label(root, text=f"运行进度：{0.00}%")
    loading_text.place(x=10, y=120)
    loading = ttk.Progressbar(root, length=230)
    loading.place(x=10, y=140)
    loading["maximum"] = 1
    loading["value"] = 0

    tk.Label(root, text=f"密钥（取值范围：0~4,294,967,295）").place(x=10, y=165)

    pw_entry = tk.Entry(root, width=32)
    pw_entry.place(x=10, y=185)

    with BytesIO(base64.b64decode(image_data)) as file:
        hacker_img = ImageTk.PhotoImage(Image.open(file))

    root.iconphoto(True, hacker_img)

    root.mainloop()