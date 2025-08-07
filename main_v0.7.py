# Everything started at here!
import math, tkinter as tk, os
from tkinter import ttk, filedialog
from PIL import Image, ImageFile
from threading import Thread
 
VERSION: str = "0.7"
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None
split: str = "<<<INF>>>"
null_color: tuple = (30, 42, 227, 79)

def get_sqrt(value: int):
    return math.ceil(math.sqrt(value))

def encode(path: str, save_path: str):
    update_loading(0.00, f"运行进度：正在读取文件......")

    with open(path, mode="rb") as f:
        file = f.read()
        file = (path.split("\\")[-1] + split + VERSION + split + str(len(file))+ split).encode("utf-8") + file + split.encode("utf-8")

    value: int = get_sqrt(len(file)/4)
    img = Image.new('RGBA', [value, value], color=None)
    pixel = img.load()

    for tx in range(0, value):
        for ty in range(0, value):
            intvar = (ty*value+tx)*4
            try:
                pixel[tx, ty] = (file[intvar], file[intvar+1], file[intvar+2], file[intvar+3])
            except:
                pixel[tx, ty] = null_color
        var=(tx+1) / value
        update_loading(var, f"运行进度：{round(var*100, 2)}%")

    update_loading(1.00, f"运行进度：正在保存文件......")
    
    img.save(os.path.join(save_path, os.path.splitext(os.path.basename(path))[0] + ".png"))
    update_loading(1.00, f"运行进度：编码完成")

def decode(path: str, save_path: str):
    update_loading(0.00, f"运行进度：正在读取文件......")

    img = Image.open(path)
    pixel = img.load()
    file = list()
    for ty in range(0, img.size[0]):
        for tx in range(0, img.size[1]):
            for byte in pixel[tx, ty]:
                file.append(byte)
        var = (ty+1) / img.size[0]
        update_loading(var, f"运行进度：{round(var*100, 2)}%")

    file = bytes(file)
    info = file.split(split.encode("utf-8"))

    def error_info():
        update_loading(0.00, f"程序版本异常 ⚠ 需求版本：{info[1]}")

    try:
        if info[1] == VERSION.encode("utf-8"):
            update_loading(1.00, f"运行进度：正在保存文件......")
            with open(os.path.join(save_path, info[0].decode("utf-8")), mode="wb") as f:
                f.write(split.encode("utf-8").join(info[3:])[0: int(info[2].decode("utf-8"))])
        else:
            error_info()
    except:
        error_info()

    update_loading(1.00, f"运行进度：解码完成")

def update_loading(value, text: str):
    loading['value'] = value
    loading_text.config(text=text)
    root.update_idletasks()

if __name__=="__main__":
    root = tk.Tk()
    root.geometry("250x170+648+648")
    root.title("FileToImage")
    file_path = None
    path = os.path.dirname(os.path.abspath(__file__))

    def file_path_get():
        global file_path
        file_path = os.path.normpath(filedialog.askopenfilename())

    def path_get():
        global path
        path = os.path.normpath(filedialog.askdirectory()) + os.sep

    tk.Label(root, text=f"File to Image    作者：INF    版本：{VERSION}").place(x=10, y=5)
    tk.Button(root, text="选择文件", command=file_path_get).place(x=10, y=40)
    tk.Button(root, text="选择路径", command=path_get).place(x=10, y=80)
    tk.Button(root, text="编码", command=lambda: Thread(target=encode, args=(file_path, path)).start()).place(x=80, y=40)
    tk.Button(root, text="解码", command=lambda: Thread(target=decode, args=(file_path, path)).start()).place(x=80, y=80)

    loading_text = tk.Label(root, text=f"运行进度：{0.00}%")
    loading_text.place(x=10, y=120)
    loading = ttk.Progressbar(root, length=230)
    loading.place(x=10, y=140)
    loading["maximum"] = 1
    loading["value"] = 0

    root.mainloop()