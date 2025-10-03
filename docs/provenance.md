# Provenance (最小溯源) 规范 v0

写出 `ac-umtc` 时必须包含 `provenance`，最小字段：
- `generated_by`: 生成工具与版本（`"ac <__version__>"`）
- `date`: UTC 时间，ISO8601，形如 `YYYY-MM-DDTHH:MM:SSZ`
- `toolchain_version`: `"pyX.Y|ruff<ver/空>|mypy<ver/空>"`
- `exact_backend_id`: 暂置 `null`
- `numeric_policy`: 暂置 `null`
- `sources`: 非空字符串数组。优先从输入 `_sources`（私有键）读取，否则为 `["<unspecified>"]`

合并策略：若已有 `provenance`，仅补缺不改已有值。写出前会移除临时键 `_sources`。
