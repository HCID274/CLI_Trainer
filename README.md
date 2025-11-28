# CLI Trainer

命令行关卡式训练器，涵盖 Linux / Windows CMD / Docker / Vim / Git 常用指令。即时判题、提供伪终端输出和鼓励语，可自定义题库，支持跨平台终端使用。

## 安装与运行

1. 获取代码
```bash
git clone https://github.com/HCID274/CLI_Trainer.git
cd CLI_Trainer
```

2. 安装（推荐开发模式便于改题库立即生效）
```bash
python -m pip install -e .
# 如需正式安装：python -m pip install .
```

3. 启动
```bash
cli-trainer                            # 使用内置题库导航式练习
cli-trainer --levels my_levels.json    # 指向自定义题库文件或目录
cli-trainer --no-color                 # 关闭彩色输出
```

常用过滤：
- `--category`：`linux_shell` / `windows_cmd` / `docker` / `vim_normal` / `git`
- `--difficulty`：`easy` / `medium` / `hard`

退出：任意输入处输入 `exit` / `quit` / `:q` 或 Ctrl+C。

## 进度保存与恢复
- 每道题开始和结束都会把进度写入当前工作目录的 `./cli_trainer/state.json`。
- 下次运行会提示“是否从上次位置继续？”回车默认继续，输入 `n` 跳过。
- 进度仅记录“最后尝试的关卡 id”，恢复时从该关卡重新开始。

## 题库加载优先级
1. `--levels` 指定路径（文件或目录；目录默认找其中的 index.json）
2. 当前目录 `index.json`
3. 当前目录 `levels/index.json`
4. 当前目录 `levels.json`
5. 内置题库 `cli_trainer/bundled_levels/index.json`（随安装包提供，无需额外文件）

## 题库格式（关卡 JSON）

顶层是数组；必填字段：`id`, `category`, `topic`, `difficulty`, `title`, `prompt`, `valid_answers`。

```json
[
  {
    "id": "linux_ls_basic",
    "category": "linux_shell",      // linux_shell | windows_cmd | docker | vim_normal | git
    "topic": "filesystem",
    "difficulty": "easy",           // easy | medium | hard
    "title": "列出当前目录所有文件",
    "prompt": "请列出当前目录所有文件",
    "description": "练习使用 ls 命令查看目录内容",
    "tags": ["ls", "filesystem"],
    "valid_answers": ["^ls$", "^ls\\s+-la?$"],   // 正则列表，须使用 ^...$ 全匹配
    "case_sensitive": true,         // 可选；缺省使用全局默认
    "anti_patterns": [
      { "pattern": "^dir$", "hint": "这是 Linux 环境，请使用 ls 而不是 dir" }
    ],
    "outputs": {
      "^ls$": "README.md\napp.py\ndata\nlogs",
      "^ls\\s+-la?$": "total 4\n-rw-r--r-- 1 root root 120 README.md\n-rw-r--r-- 1 root root 2048 app.py\ndrwxr-xr-x 2 root root 4096 data\ndrwxr-xr-x 2 root root 4096 logs"
    },
    "hint": "使用 ls 命令列出当前目录内容",
    "explanation": "ls 会列出当前目录内容，搭配 -l -a 可以查看更多信息"
  }
]
```

说明：
- `valid_answers`：正则列表；会在 `answer` 命令中展示。
- `anti_patterns`：命中时显示对应 `hint`。
- `outputs`：匹配成功后先打印伪输出再给鼓励/解析。
- `topic`：自定义子类别，用于二级筛选。

### 多文件题库（index.json 清单）

目录下放一个 `index.json`，内容是字符串数组，列出要加载的子文件（相对 index 的路径）：
```json
["linux.json", "windows.json", "docker.json", "vim.json", "git.json"]
```
Loader 会按顺序合并；若 `--levels` 指向目录，则默认读取该目录内的 index.json。

## 交互指令
- `hint` 查看提示
- `explain` 查看解析
- `answer` 查看全部参考答案
- `exit | quit | :q` 退出当前训练

成功反馈包含绿色输出 + 随机中文鼓励语 + 可选解析；提示符按类别自动切换（Linux/Windows/Docker/Vim/Git）。

## 模块概览
- `cli_trainer/main.py`：入口；参数解析与启动
- `cli_trainer/engine.py`：导航选择、关卡循环、进度保存/恢复
- `cli_trainer/levels_loader.py`：题库加载、索引递归解析、内置题库 fallback
- `cli_trainer/matcher.py`：正则匹配与反模式检查
- `cli_trainer/ui.py`：输出样式、提示符、鼓励语
- `cli_trainer/config.py`：默认配置（颜色、提示符、大小写敏感）
- `cli_trainer/models.py`：`Level` 数据类与字段校验

## 后续可扩展
- 远程下载题库、版本管理
- 统计与进度同步
- 更丰富的 Vim 场景描述与状态模拟
