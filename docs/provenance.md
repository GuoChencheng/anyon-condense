# Provenance (最小溯源) 规范 v0

写出 `ac-umtc` 时必须包含 `provenance`，最小字段：
- `generated_by`: 生成工具与版本（`"ac <__version__>"`）
- `date`: UTC 时间，ISO8601，形如 `YYYY-MM-DDTHH:MM:SSZ`
- `toolchain_version`: `"pyX.Y|ruff<ver/空>|mypy<ver/空>"`
- `exact_backend_id`: 暂置 `null`
- `numeric_policy`: 暂置 `null`
- `sources`: 非空字符串数组。优先从输入 `_sources`（私有键）读取，否则为 `["<unspecified>"]`

合并策略：若已有 `provenance`，仅补缺不改已有值。写出前会移除临时键 `_sources`。

## Hashes（指纹）规范 v0

写出 `ac-umtc` 时应填充 `hashes` 字段，为关键子结构生成稳定的 `sha256` 值（字符串，形如 `sha256:<hex>`）：

- `objects`, `qdim`, `global_dim`, `twist`, `S`, `T`（仅对存在的字段计算）
- 计算使用 canonical JSON（键排序、UTF-8、拒绝 NaN/Inf、-0.0 → 0.0），保证跨机一致。

## 来源链合并

- 写出前从临时 `_sources` 与已有 `provenance.sources` 合并去重（保持出现顺序）。
- `_sources` 不会出现在最终 JSON（避免 schema 拒绝）。
- `sources` 元素建议为绝对路径或 content-address（如 `umtc:sha256:<hex>`）。
