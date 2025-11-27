from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Level:
    id: str
    category: str
    topic: str
    difficulty: str
    title: str
    prompt: str
    valid_answers: List[str]
    description: str = ""
    tags: List[str] = field(default_factory=list)
    case_sensitive: Optional[bool] = None
    anti_patterns: List[Dict[str, str]] = field(default_factory=list)
    outputs: Dict[str, str] = field(default_factory=dict)
    hint: str = ""
    explanation: str = ""

    @staticmethod
    def required_fields() -> List[str]:
        return [
            "id",
            "category",
            "topic",
            "difficulty",
            "title",
            "prompt",
            "valid_answers",
        ]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Level":
        missing = [k for k in cls.required_fields() if k not in data]
        if missing:
            raise ValueError(f"关卡缺少必填字段: {', '.join(missing)}")

        if not isinstance(data.get("valid_answers"), list):
            raise ValueError("字段 valid_answers 必须是字符串列表")

        return cls(
            id=str(data["id"]),
            category=str(data["category"]),
            topic=str(data["topic"]),
            difficulty=str(data["difficulty"]),
            title=str(data["title"]),
            prompt=str(data["prompt"]),
            valid_answers=[str(v) for v in data["valid_answers"]],
            description=str(data.get("description", "")),
            tags=[str(t) for t in data.get("tags", [])],
            case_sensitive=data.get("case_sensitive"),
            anti_patterns=[
                {"pattern": str(item.get("pattern", "")), "hint": str(item.get("hint", ""))}
                for item in data.get("anti_patterns", [])
                if isinstance(item, dict)
            ],
            outputs={
                str(k): str(v) for k, v in data.get("outputs", {}).items() if isinstance(data.get("outputs", {}), dict)
            },
            hint=str(data.get("hint", "")),
            explanation=str(data.get("explanation", "")),
        )
