import os
import random
import sys
from typing import List

from .config import Config
from .models import Level


COLOR_CODES = {
    "green": "\033[92m",
    "red": "\033[91m",
    "yellow": "\033[93m",
    "cyan": "\033[96m",
    "reset": "\033[0m",
}


SUCCESS_MESSAGES: List[str] = [
    "干得漂亮！",
    "这波操作很稳！",
    "命令敲得很准！",
    "熟练度 +1！",
    "漂亮收工！",
    "保持这个节奏！",
    "手感在线！",
    "思路清晰，执行到位！",
    "这下拿捏了！",
    "就该这么干！",
    "很好，很强大！",
    "操作行云流水！",
    "完全正确，继续！",
    "稳如老狗！",
    "掌握得很扎实！",
    "优秀，继续保持！",
    "命令肌肉记忆正在形成！",
    "棒极了，下一关！",
    "节奏稳，进步快！",
    "这才是命令行的味道！",
    "越敲越顺手！",
]


def colorize(text: str, color: str, enabled: bool = True) -> str:
    if not enabled:
        return text
    prefix = COLOR_CODES.get(color)
    if not prefix:
        return text
    return f"{prefix}{text}{COLOR_CODES['reset']}"


def print_success(text: str, config: Config) -> None:
    print(colorize(text, "green", config.color_enabled))


def print_error(text: str, config: Config) -> None:
    print(colorize(text, "red", config.color_enabled), file=sys.stderr)


def print_info(text: str, config: Config) -> None:
    print(colorize(text, "cyan", config.color_enabled))


def random_success_message() -> str:
    return random.choice(SUCCESS_MESSAGES)


def render_prompt(level: Level, config: Config) -> str:
    return config.prompt_symbols.get(level.category, "$ ")


def clear_screen() -> None:
    """Clear the terminal screen in a cross-platform way."""
    command = "cls" if os.name == "nt" else "clear"
    # Ignore non-zero exit; fallback ANSI will still run.
    os.system(command)
    # Fallback ANSI clear (useful in limited environments).
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()
