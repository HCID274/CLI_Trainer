import json
from pathlib import Path
from typing import List, Optional, Set, Tuple

from .models import Level

BUNDLED_INDEX = Path(__file__).resolve().parent / "bundled_levels" / "index.json"


def _candidate_paths(override: Optional[str]) -> List[Path]:
    """Candidate paths in priority order."""
    candidates: List[Path] = []
    seen: Set[Path] = set()

    def add(path: Path) -> None:
        resolved = path.resolve()
        if resolved not in seen and path.exists():
            seen.add(resolved)
            candidates.append(path)

    if override:
        add(Path(override))

    add(Path("index.json"))
    add(Path("levels/index.json"))
    add(Path("levels.json"))
    add(BUNDLED_INDEX)
    return candidates


def _load_from_index(index_path: Path, visited: Set[Path]) -> List[Level]:
    """Load levels from an index.json that lists other JSON files."""
    resolved = index_path.resolve()
    if resolved in visited:
        raise ValueError(f"检测到循环引用的索引文件: {index_path}")
    visited.add(resolved)

    with index_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    if not isinstance(payload, list) or not all(isinstance(item, str) for item in payload):
        raise ValueError(f"索引文件 {index_path} 顶层应为字符串数组，指向其他 JSON 文件。")

    levels: List[Level] = []
    base = index_path.parent
    for entry in payload:
        sub_path = Path(entry)
        if not sub_path.is_absolute():
            sub_path = (base / sub_path).resolve()
        if sub_path.is_dir():
            # 若引用目录，默认目录下需要有 index.json
            sub_path = sub_path / "index.json"
        if not sub_path.exists():
            raise FileNotFoundError(f"索引 {index_path} 引用的文件不存在: {entry}")
        levels.extend(_load_levels_from_path(sub_path, visited))
    return levels


def _load_levels_from_path(path: Path, visited: Optional[Set[Path]] = None) -> List[Level]:
    """Load levels from a path which may be a levels file, an index file, or a directory."""
    visited = visited or set()

    target = path
    if path.is_dir():
        target = path / "index.json"
        if not target.exists():
            raise FileNotFoundError(f"目录 {path} 缺少 index.json")

    with target.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    # If payload is a string list, treat as index listing.
    if isinstance(payload, list) and payload and all(isinstance(item, str) for item in payload):
        return _load_from_index(target, visited)

    if not isinstance(payload, list):
        raise ValueError(f"题库 JSON 顶层必须是数组: {target}")

    levels = [Level.from_dict(item) for item in payload]
    return levels


def load_levels(override_path: Optional[str] = None) -> Tuple[List[Level], Path]:
    paths = _candidate_paths(override_path)
    if not paths:
        raise FileNotFoundError("未找到可用的题库文件，请提供 levels.json 或 index.json。")

    last_error: Optional[Exception] = None
    for path in paths:
        try:
            levels = _load_levels_from_path(path)
            return levels, path
        except Exception as exc:  # noqa: BLE001 - 需要完整错误信息
            last_error = exc
            continue

    if last_error:
        raise ValueError(f"加载题库失败: {last_error}")
    raise FileNotFoundError("未找到可用的题库文件，请提供 levels.json 或 index.json。")
