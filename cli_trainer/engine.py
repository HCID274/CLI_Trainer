import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Sequence

from .config import Config
from .levels_loader import load_levels
from .matcher import check_answer
from .models import Level
from .ui import (
    clear_screen,
    print_error,
    print_info,
    print_success,
    random_success_message,
    render_prompt,
)


CATEGORY_LABELS = {
    "linux_shell": "Linux 命令行",
    "windows_cmd": "Windows 命令行",
    "docker": "Docker",
    "vim_normal": "Vim 普通模式",
}

DIFFICULTY_LABELS = {
    "easy": "简单",
    "medium": "中等",
    "hard": "困难",
}

EXIT_COMMANDS = {"exit", "quit", ":q"}
SPECIAL_COMMANDS = {"hint", "explain", "answer"}
STATE_PATH = Path("cli_trainer") / "state.json"


def _load_progress_state(state_path: Path, config: Config) -> Optional[str]:
    try:
        with state_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        print_error("进度文件损坏，已忽略", config)
        return None
    except OSError:
        return None

    level_id = data.get("level_id") if isinstance(data, dict) else None
    if isinstance(level_id, str) and level_id.strip():
        return level_id.strip()
    return None


def _save_progress_state(state_path: Path, level_id: str, config: Config) -> None:
    payload = {"level_id": level_id, "updated_at": datetime.utcnow().isoformat() + "Z"}
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        with state_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
    except OSError:
        print_error("无法写入进度文件，继续训练但不会保存进度。", config)


def _select_from_list(title: str, options: Sequence[str], allow_all: bool = False) -> Optional[str]:
    if not options:
        return None

    print(title)
    if allow_all:
        print("0) 全部")
    for idx, item in enumerate(options, start=1):
        print(f"{idx}) {item}")

    while True:
        choice = input("请输入编号(回车默认选全部): ").strip()
        if allow_all and (choice == "" or choice == "0"):
            return None
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(options):
                return options[index]
        print("无效选择，请重试。")


def _filter_levels(
    levels: List[Level],
    category: Optional[str],
    topic: Optional[str],
    difficulty: Optional[str],
) -> List[Level]:
    result: List[Level] = []
    for level in levels:
        if category and level.category != category:
            continue
        if topic and level.topic != topic:
            continue
        if difficulty and level.difficulty != difficulty:
            continue
        result.append(level)
    return result


def navigate_levels(levels: List[Level], config: Config) -> List[Level]:
    categories = sorted({lvl.category for lvl in levels})
    labels = [CATEGORY_LABELS.get(c, c) for c in categories]
    selected_label = _select_from_list(
        "请选择类别（回车默认全部）：" if len(categories) > 1 else "请选择类别：",
        labels,
        allow_all=len(categories) > 1,
    )
    if selected_label is None:
        selected_category = None
    else:
        selected_category = categories[labels.index(selected_label)]

    topics = sorted({lvl.topic for lvl in levels if (selected_category is None or lvl.category == selected_category)})
    topic = _select_from_list("请选择主题（回车默认全部）：", topics, allow_all=True)

    difficulties = ["easy", "medium", "hard"]
    difficulty = _select_from_list("请选择难度（回车默认全部）：", difficulties, allow_all=True)

    filtered = _filter_levels(levels, selected_category, topic, difficulty)
    if not filtered:
        print_error("筛选后没有可用关卡，请尝试其他选项。", config)
    return filtered


def _show_header(level: Level, config: Config) -> None:
    clear_screen()
    diff_label = DIFFICULTY_LABELS.get(level.difficulty, level.difficulty)
    print_info(f"[{CATEGORY_LABELS.get(level.category, level.category)}] {level.title}（难度：{diff_label}）", config)
    if level.description:
        print(level.description)


def _show_answers(level: Level, config: Config) -> None:
    print_info("参考答案（满足要求的命令）：", config)
    for ans in level.valid_answers:
        print(f"- {ans}")


def _print_fake_output(level: Level, user_input: str, matched_pattern: Optional[str], config: Config) -> None:
    if not level.outputs:
        return
    case_sensitive = level.case_sensitive
    if case_sensitive is None:
        case_sensitive = config.default_case_sensitive
    flags = 0 if case_sensitive else re.IGNORECASE

    # Prefer exact matched pattern key if present.
    if matched_pattern and matched_pattern in level.outputs:
        print(level.outputs[matched_pattern])
        return

    for pattern, text in level.outputs.items():
        try:
            if re.fullmatch(pattern, user_input, flags=flags):
                print(text)
                return
        except re.error:
            continue


def _play_level(level: Level, config: Config) -> bool:
    _show_header(level, config)
    prompt = render_prompt(level, config)

    while True:
        try:
            user_input = input(prompt).rstrip("\n")
        except KeyboardInterrupt:
            return False

        if user_input in EXIT_COMMANDS:
            return False
        if user_input == "hint":
            print_info(level.hint or "????", config)
            continue
        if user_input == "explain":
            print_info(level.explanation or "????", config)
            continue
        if user_input == "answer":
            _show_answers(level, config)
            continue

        result = check_answer(level, user_input, default_case_sensitive=config.default_case_sensitive)
        if result["ok"]:
            _print_fake_output(level, user_input, result.get("matched_pattern"), config)
            print_success(random_success_message(), config)
            if level.explanation:
                print_info(f"???{level.explanation}", config)
            proceed = input("???????????? exit ??: ").strip()
            if proceed in EXIT_COMMANDS:
                return False
            return True

        if result["anti"] and result["hint"]:
            print_error(result["hint"], config)
        else:
            print_error("?????????????", config)


def _resolve_start_index(levels: List[Level], state_path: Path, config: Config) -> int:
    saved_level_id = _load_progress_state(state_path, config)
    if not saved_level_id:
        return 0

    try:
        saved_index = next(idx for idx, lvl in enumerate(levels) if lvl.id == saved_level_id)
    except StopIteration:
        print_info("已保存的关卡在当前题库中不存在，已从头开始。", config)
        return 0

    answer = input("检测到上次练习记录，是否从上次位置继续？(回车默认是，输入 n 跳过): ").strip().lower()
    if answer in {"n", "no"}:
        return 0
    return saved_index


def run(
    override_levels_path: Optional[str],
    config: Config,
    category_filter: Optional[str] = None,
    difficulty_filter: Optional[str] = None,
) -> None:
    levels, source = load_levels(override_levels_path)
    clear_screen()
    print_info(f"题库来源：{source}", config)
    print_info("可用指令：hint(提示) | explain(解析) | answer(参考答案) | exit/quit/:q(退出)", config)

    if category_filter or difficulty_filter:
        levels = _filter_levels(levels, category_filter, None, difficulty_filter)
        if not levels:
            print_error("筛选后没有可用关卡，请检查过滤条件。", config)
            return
    else:
        levels = navigate_levels(levels, config)
        if not levels:
            return

    clear_screen()
    start_index = _resolve_start_index(levels, STATE_PATH, config)

    for level in levels[start_index:]:
        _save_progress_state(STATE_PATH, level.id, config)
        should_continue = _play_level(level, config)
        # ???????????????
        _save_progress_state(STATE_PATH, level.id, config)
        if not should_continue:
            print_info("训练已结束，欢迎下次再来。", config)
            break
    else:
        print_success("恭喜！你已完成所有选定关卡。", config)
