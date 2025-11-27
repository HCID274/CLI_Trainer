import argparse
import sys

from .config import Config
from .engine import run


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="CLI Trainer - 关卡式命令行训练器")
    parser.add_argument("--levels", help="指定题库 JSON 文件路径")
    parser.add_argument("--no-color", action="store_true", help="关闭彩色输出")
    parser.add_argument("--category", choices=["linux_shell", "windows_cmd", "docker", "vim_normal"], help="按类别过滤题库")
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard"], help="按难度过滤题库")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    config = Config(color_enabled=not args.no_color)

    try:
        run(
            override_levels_path=args.levels,
            config=config,
            category_filter=args.category,
            difficulty_filter=args.difficulty,
        )
    except KeyboardInterrupt:
        print("\n已退出训练，欢迎下次再来。")
    except Exception as exc:  # noqa: BLE001 - 顶层捕获并打印友好信息
        print(f"程序运行出错：{exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
