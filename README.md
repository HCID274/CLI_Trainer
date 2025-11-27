# CLI Trainer

一个基于关卡的命令行模拟训练器，支持 Linux / Windows / Docker / Vim 基础指令练习。强调“手速 + 肌肉记忆”刷题体验：连敲命令立即判定，命中即可回显伪终端输出 + 鼓励语。支持自定义上传题库（`--levels` 指定文件或 `index.json` 清单），用正则匹配验证用户输入，不执行真实命令。

## 快速开始

```bash
python -m pip install .
cli-trainer               # 进入导航式训练
cli-trainer --levels my_levels.json  # 使用自定义题库
cli-trainer --no-color    # 关闭彩色输出
```

可选过滤参数：
- `--category`：`linux_shell` / `windows_cmd` / `docker` / `vim_normal`
- `--difficulty`：`easy` / `medium` / `hard`

退出：任意输入处使用 `exit` / `quit` / `:q` 或 `Ctrl+C`。

## 题库格式（自定义上传接口）

顶层为数组，每个元素是一道关卡。必填字段：`id`, `category`, `topic`, `difficulty`, `title`, `prompt`, `valid_answers`。

```json
[
  {
    "id": "linux_ls_basic",
    "category": "linux_shell",          // linux_shell | windows_cmd | docker | vim_normal
    "topic": "filesystem",              // 主题/线路：filesystem/process/navigation/image/container 等
    "difficulty": "easy",               // easy | medium | hard
    "title": "列出当前目录所有文件",
    "prompt": "请列出当前目录所有文件。",
    "description": "练习使用 ls 命令查看目录内容。",
    "tags": ["ls", "filesystem"],
    "valid_answers": ["^ls$", "^ls\\s+-la?$"],   // 正则列表
    "case_sensitive": true,             // 可选；缺省使用全局默认（大小写敏感）
"anti_patterns": [
  { "pattern": "^dir$", "hint": "这是 Linux 环境，请使用 ls 而不是 dir。" }
],
"outputs": {
  "^ls$": "README.md\napp.py\ndata\nlogs",
  "^ls\\s+-la?$": "total 4\n-rw-r--r-- 1 root root 120 README.md\n-rw-r--r-- 1 root root 2048 app.py\ndrwxr-xr-x 2 root root 4096 data\ndrwxr-xr-x 2 root root 4096 logs"
},
"hint": "使用 ls 命令列出当前目录内容。",
"explanation": "ls 会列出当前目录内容，搭配 -l -a 可以查看更多信息。"
}
]
```

- `valid_answers`：正则列表；全部作为参考答案在 `answer` 命令中展示。
- `anti_patterns`：命中时显示专属提示 `hint`。
- `outputs`：可选，键为正则（可与 valid_answers 对应），值为“伪输出”。匹配成功后会先打印对应输出，再给鼓励/解析。
- `topic`：用于二级导航；可以自定义任意主题名。
- 可选字段缺省时自动填充空串或全局默认。

加载优先级：`--levels` 指定路径 > 当前目录 `index.json` > 当前目录 `levels/index.json` > 当前目录 `levels.json`。

### 多文件题库：index.json 清单

- 你可以用目录+清单的方式拆分题库：在目录下放一个 `index.json`，内容是字符串数组，列出要加载的子文件（相对该 index 的路径）。
- 示例：

```
levels/
  index.json       # ["linux.json", "windows.json", "docker.json", "vim.json"]
  linux.json
  windows.json
  docker.json
  vim.json
```

`index.json` 内容示例：

```json
[
  "linux.json",
  "windows.json",
  "docker.json",
  "vim.json"
]
```

任意子文件仍是“关卡数组”格式；Loader 会按 index 中的顺序依次合并。若 `--levels` 指向目录，默认读取其中的 `index.json`；若指向某个 `index.json`，按其中清单加载。

## 交互要点

- 指令提示：`hint` 查看提示，`explain` 查看解析，`answer` 查看全部参考答案，`exit|quit|:q` 退出。
- 成功反馈：绿色输出 + 随机中文鼓励语（≥20 条）+ 解析。
- 提示符：按类别自动切换（Linux/Windows/Docker/Vim）。

## 模块概览

- `cli_trainer/main.py`：入口，解析参数，启动引擎
- `cli_trainer/engine.py`：导航选择、关卡循环、特殊命令处理
- `cli_trainer/levels_loader.py`：题库加载与校验
- `cli_trainer/matcher.py`：正则匹配与 anti_patterns 检测
- `cli_trainer/ui.py`：彩色输出、提示符、鼓励语
- `cli_trainer/config.py`：默认配置（颜色、提示符、大小写默认）
- `cli_trainer/models.py`：`Level` 数据类与字段校验

## 后续可扩展

- 远程下载题库、题库版本管理
- 统计与进度保存
- 更丰富的 Vim 场景描述与状态模拟
