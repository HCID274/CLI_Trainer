from dataclasses import dataclass, field
from typing import Dict


DEFAULT_PROMPT_SYMBOLS: Dict[str, str] = {
    "linux_shell": "root@debian:~$ ",
    "windows_cmd": "C:\\Users\\Admin> ",
    "docker": "root@container:/app# ",
    "vim_normal": "[Vim Normal]: ",
    "git": "repo(main)$ ",
}


@dataclass
class Config:
    color_enabled: bool = True
    default_case_sensitive: bool = True
    prompt_symbols: Dict[str, str] = field(default_factory=lambda: DEFAULT_PROMPT_SYMBOLS.copy())
