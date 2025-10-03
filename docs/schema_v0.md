# Schema v0 字段表（ac-mfusion / ac-umtc 输入与 ac-umtc 输出）

> 本文档描述 v0 版 JSON Schema 的字段含义与取值范围。仅为“结构/类型约束”，不包含物理/数学验证。

## 共同元信息（顶层字段）

| 字段名 | 类型/取值 | 必填 | 说明 |
|---|---|---|---|
| `format` | "ac-mfusion" \| "ac-umtc" | 是 | 文件格式标识。 |
| `version` | `string` | 是 | 任意非空字符串（建议语义化版本）。 |
| `encoding` | "exact" \| "float" | 是 | 数值表达形式：精确字符串 / 浮点。 |
| `number_field` | `string`（`cyclotomic(n)`） | 是 | 圆分域占位符样式，n 为正整数。 |
| `category_type` | "mfusion" \| "umtc" | 是 | 类别类型：multi-fusion 或 UMTC。 |
| `_meta` | `object` | 否 | 自由备注，不受限。 |
| `additionalProperties` | **禁止** | — | 顶层不允许未知键，防误拼写。 |

---

## ac-mfusion 输入（`schemas/mfusion_input.schema.json`）

| 字段名 | 类型/取值 | 必填 | 说明 |
|---|---|---|---|
| `simple_objects` | `string[]`，唯一 | 是 | 简单对象名列表，最少 1 个。 |
| `dual` | `object (str → str)` | 是 | 每个对象的对偶对象名。 |
| `fusion_rules` | `object` | 是 | 键为 `"(a,b)"` 形式；值为 `{ c: mult }`，其中 `mult` 为 `>=1` 的整数。 |

**注意**：v0 不做“交叉一致性”（如 `c` 是否在 `simple_objects` 内）；该类校验在 M1-C 实现。

---

## ac-umtc 输入（`schemas/umtc_input.schema.json`）

在 ac-mfusion 基础上**新增**：

| 字段名 | 类型/取值 | 必填 | 说明 |
|---|---|---|---|
| `F_symbols` | `object` \| `array` \| `null` | 否 | v0 占位，结构不校验。 |
| `R_symbols` | `object` \| `array` \| `null` | 否 | v0 占位，结构不校验。 |

---

## ac-umtc 输出（`schemas/umtc_output.schema.json`）

| 字段名 | 类型/取值 | 必填 | 说明 |
|---|---|---|---|
| `objects` | `string[]` | 是 | 对象名顺序。 |
| `scalar` | `number` \| `string` | — | v0 内部复用的“标量”类型别名。 |
| `qdim` | `object (str → scalar)` | 是 | 各对象的量子维（v0：可数可串）。 |
| `global_dim` | `scalar` | 是 | 全局维的标量。 |
| `twist` | `object (str → scalar)` | 是 | 各对象的 twist。 |
| `matrix` | `scalar[][]` | — | v0 内部复用的“矩阵”类型别名。 |
| `S`/`T` | `matrix` | 是 | S/T 矩阵（v0 不验证维度匹配）。 |
| `checks` | `object` | 是 | 任意检查报告容器。 |
| `hashes` | `object` | 是 | 稳定哈希/指纹容器。 |
| `provenance` | `object` | 是 | 溯源信息，至少含 `generated_by` / `date` / `sources`。 |

**provenance 子字段**
- `generated_by: string`（例如 `"ac 0.1.0-dev"`）
- `date: string (date-time)`（ISO 8601）
- `sources: string[]`（至少 1 个）
- `toolchain_version / exact_backend_id / numeric_policy`（可空）

---
