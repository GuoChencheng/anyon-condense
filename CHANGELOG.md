# Changelog
## [0.1.0-dev] - Init (M1-A1)
- Project skeleton, version/CLI entrypoint, configs and placeholders.
## [0.1.0-dev] - Add code quality baseline (M1-A2)
- Added ruff/mypy/pytest configuration
- Added pre-commit hooks
- Added CI workflow
## [0.1.0-dev] - Added Schema v0 examples and validation tests
- Added schema field documentation (`docs/schema_v0.md`).
- Added good/bad example JSON files.
- Added pytest schema validation tests.
## [Unreleased]
- M1-C1 完成：schema 装载与缓存接口（load_schema/validate/list_schemas/clear_caches，支持 AC_SCHEMA_DIR 覆盖，缓存命中测试通过）

## [0.1.0-dev] - 初始
- 项目骨架与 CLI --version
## [0.1.0-dev] - Add schema loader & IO layer (M1-C1,C2)
- Schema caching and validation API, unified IO load_*/write_* functions with new exceptions.
## [0.1.0-dev] - Schema 装载与 IO 统一入口 (M1-C1,C2)
- Schema 装载与缓存；IO 统一入口（load_*/write_*）与异常模型。
## [0.1.0-dev] - Schema 装载与缓存；IO 统一入口 (M1-C1,C2)
- Schema 装载与缓存；IO 统一入口（load_*/write_*）与异常模型。
