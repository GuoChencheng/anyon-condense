# 主干开发（直推 main）工作流

## 日常操作
1. 确保本地钩子安装：
   ```bash
   pre-commit install --install-hooks --hook-type pre-commit --hook-type pre-push
   ```
2. 开发 → 保存 → 本地检查：
   ```bash
   pre-commit run -a
   pytest -q
   ```
3. 直推 main：
   ```bash
   git add -A
   git commit -m "feat: <改动概要>"
   git push origin main
   ```
4. 云端 CI 会在 push 后自动跑 ruff/mypy/pytest。

## 版本与发布（可选）
- 修改版本号：同步更新 `anyon_condense/__init__.py` 与 `pyproject.toml`。
- 打 Tag：
  ```bash
  git tag v0.1.0
  git push origin v0.1.0
  ```
- `release-on-tag.yml` 会被触发（后续可扩展 PyPI 发布）。

## 回滚与修复
- 发现 main 上一笔提交让 CI 变红：
  - 快速修复：追加修复提交并 push。
  - 临时回滚（无共享历史改写）：
    ```bash
    git revert <坏提交的hash>
    git push origin main
    ```
- 禁止强推（force push），保留线性历史便于追溯。

## 约定
- 提交信息建议使用 Conventional Commits，例如 `feat` / `fix` / `chore` / `docs` / `test` / `refactor` / `ci`。
- 严禁直接修改 `schemas/` 与 `tests/examples/` 而不更新相关测试。
