import re
from typing import Dict

from .models import Level


def check_answer(level: Level, user_input: str, default_case_sensitive: bool = True) -> Dict[str, object]:
    case_sensitive = level.case_sensitive
    if case_sensitive is None:
        case_sensitive = default_case_sensitive

    flags = 0 if case_sensitive else re.IGNORECASE

    for pattern in level.valid_answers:
        if re.fullmatch(pattern, user_input, flags=flags):
            return {"ok": True, "anti": False, "hint": None, "matched_pattern": pattern}

    for anti in level.anti_patterns:
        pattern = anti.get("pattern")
        if pattern and re.fullmatch(pattern, user_input, flags=flags):
            return {"ok": False, "anti": True, "hint": anti.get("hint", ""), "matched_pattern": pattern}

    return {"ok": False, "anti": False, "hint": None, "matched_pattern": None}
