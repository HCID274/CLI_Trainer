# Repository Guidelines

## Project Structure & Module Organization
- `cli_trainer/main.py`: CLI entry point; parses args and boots the engine via `run()`.
- `cli_trainer/engine.py`: Level navigation loop, prompt handling, and success/failure flows.
- `cli_trainer/levels_loader.py`: Resolves the level source (`--levels` override → local `levels/index.json` fallback), loads JSON, and validates shapes.
- `cli_trainer/matcher.py` & `cli_trainer/models.py`: Regex matching logic and the `Level` data model; keep validation close to the model.
- `cli_trainer/ui.py` & `cli_trainer/config.py`: Output styling, prompt symbols, and case-sensitivity defaults.
- `levels/`: Built-in question sets with `index.json` registry plus category files (`linux.json`, `windows.json`, `docker.json`, `vim.json`). Prefer adding new sets via the index to keep ordering explicit.

## Build, Test, and Development Commands
```bash
python -m pip install -e .        # Editable install for local development
cli-trainer                       # Start guided navigation with bundled levels
cli-trainer --levels my.json      # Point to a custom level file or directory containing index.json
cli-trainer --no-color --levels levels/index.json --category linux_shell --difficulty easy
```
- No automated tests are wired yet; prefer `python -m pytest` once tests are added under `tests/`.

## Coding Style & Naming Conventions
- Target Python 3.8+; use 4-space indents, type hints, and dataclasses where stateful structures are needed.
- Keep functions `snake_case`, classes `PascalCase`, and module-level constants `UPPER_SNAKE`.
- Use the helpers in `ui.py` for any user-facing output to keep coloring and tone consistent.
- When extending level formats, mirror existing JSON keys and keep regexes anchored with `^...$` to avoid accidental matches.

## Testing Guidelines
- Add new tests under `tests/` using `test_*.py` naming; structure fixtures around sample files in `levels/`.
- Cover matching behavior (`matcher.check_answer`), loader fallbacks (`levels_loader.load_levels`), and CLI option parsing (`main.parse_args`).
- Keep fake outputs deterministic to avoid brittle assertions; prefer snapshot-friendly strings.

## Commit & Pull Request Guidelines
- No repository history is bundled; follow Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`) in present tense and keep scopes small (e.g., `feat: add docker prompts`).
- Describe behavior changes, CLI flags touched, and level file impacts. Include repro steps or sample commands and paste the relevant CLI output when it affects UX.
- Link any tracking issue; attach screenshots only if they clarify CLI output (color/formatting changes).
