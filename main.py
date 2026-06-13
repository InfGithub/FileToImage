import sys
from argparse import ArgumentParser
from ui import GUI, CLI
from core import encode, decode
from data import workspace, compress_types

def main() -> None:
    if len(sys.argv) == 1:
        gui = GUI()
        gui.run()
        return

    parser = ArgumentParser(
        description="FileToImage - 文件与图片互转工具"
    )
    parser.add_argument(
        "-e", "--encode", action="store_true",
        help="编码模式（文件→图片）"
    )
    parser.add_argument(
        "-d", "--decode", action="store_true",
        help="解码模式（图片→文件）"
    )
    parser.add_argument(
        "-p", "--password", default="",
        help="密钥（建议在终端中交互式输入以避免记录，留空则需要在 CLI 提示符输入）"
    )
    parser.add_argument(
        "-f", "--file", default="",
        help="输入文件路径（编码：原文件；解码：图片文件）"
    )
    parser.add_argument(
        "-o", "--output-dir", default=workspace,
        help="输出目录，默认工作区"
    )
    parser.add_argument(
        "-t", "--compress-type", choices=compress_types, default="zlib",
        help="压缩类型（仅编码时有效）"
    )
    parser.add_argument(
        "-l", "--compress-level", type=int, default=6,
        help="压缩级别 0-9（仅编码时有效）"
    )

    args = parser.parse_args()

    # 构选 CLI 实例
    cli = CLI(
        password=args.password,
        file_path=args.file,
        dir_path=args.output_dir,
        compress_type=args.compress_type,
        compress_level=args.compress_level
    )

    if args.encode:
        encode(ui=cli)
    elif args.decode:
        decode(ui=cli)
    else:
        # 如果提供了参数但未指定 -e/-d，回退到 GUI
        gui = GUI()
        gui.run()

if __name__ == "__main__":
    main()