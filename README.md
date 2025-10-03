# Anyon-Condense（M1 版）

> 目标：在既定目录结构下，完成 **Schema v0 + 统一 IO + 日志 + Canonical 串化 + 哈希 + 最小 CLI**，并提供 5 分钟可完成的 Demo。

---

## TL;DR（5 分钟上手）

```bash
# 1) 安装（可编辑）
pip install -e .

# 2) 快速自检
python -m anyon_condense.cli --version
python -m anyon_condense.cli --info

# 3) 跑 M1 Demo（加载并校验 Vec_Z2，打印 canonical 与 sha256）
python tools/demo_m1.py
```

若看到输出里有 `Loaded mfusion input OK`、`canonical[...]`、`sha256:...`，说明环境可用。

---

## 安装（本地 editable）

要求 Python ≥ 3.10。

```bash
git clone <your-repo-url>
cd anyon-condense
pip install -e .
```

可选：安装开发工具

```bash
pip install pytest ruff mypy pre-commit
```

---

## 目录说明（精简）

```
anyon_condense/            # 包根
├─ __init__.py             # __version__
├─ cli.py                  # CLI 入口：python -m anyon_condense.cli
├─ core/
│  ├─ io.py                # 统一 IO：load_* / write_*
│  ├─ schema.py            # JSON Schema 装载与缓存
│  ├─ logging.py           # 日志规范 get_logger(...)
│  ├─ utils.py             # canonical_json_dump(...)
│  ├─ hashing.py           # sha256_of_payload / content_address
│  └─ provenance.py        # provenance 注入与来源链工具
schemas/                   # JSON Schema v0
tests/
├─ examples/               # 示例 JSON（Vec_Z2_mfusion.json 等）
tools/
└─ demo_m1.py              # 本 README 的演示脚本
```

---

## Schema v0（最小集字段表）

### ac-mfusion 输入（`schemas/mfusion_input.schema.json`）

| 字段               | 类型/取值                     | 必填 | 说明                             |
| ---------------- | ------------------------- | -- | ------------------------------ |
| `format`         | `"ac-mfusion"`            | 是  | 固定值                            |
| `version`        | `string`                  | 是  | 任意非空                           |
| `encoding`       | `"exact"`\|`"float"`       | 是  | 数值表达                           |
| `number_field`   | `string`（`cyclotomic(n)`） | 是  | 圆分域占位                          |
| `category_type`  | `"mfusion"`               | 是  | 固定值                            |
| `simple_objects` | `string[]`（唯一）            | 是  | 对象名列表                          |
| `dual`           | `object(str→str)`         | 是  | 对偶映射                           |
| `fusion_rules`   | `object`                  | 是  | 键形如 `"(a,b)"`；值 `{c: mult>=1}` |

### ac-umtc 输出（`schemas/umtc_output.schema.json`）

| 字段                | 类型/取值                | 必填       | 说明            |
| ----------------- | -------------------- | -------- | ------------- |
| `objects`         | `string[]`           | 是        | 对象顺序          |
| `qdim`            | `object(str→scalar)` | 是        | 量子维           |
| `global_dim`      | `scalar(number` \| `string)` | 是 | 全局维 |
| `twist`           | `object(str→scalar)` | 是        | twist         |
| `S`/`T`           | `scalar[][]`         | 是        | 矩阵（v0 不比对维度）  |
| `checks`/`hashes` | `object`             | 是        | 报告/指纹         |
| `provenance`      | `object`             | 是        | 溯源（生成器/时间/来源） |

> 说明：更多字段与示例参见 `docs/schema_v0.md`。

---

## Demo（加载与校验 Vec_Z2，并打印 canonical 与哈希）

运行：

```bash
python tools/demo_m1.py
```

你会看到类似输出（部分）：

```
[demo] Using example: tests/examples/Vec_Z2_mfusion.json
[demo] Loaded mfusion input OK. objects=['1', 'g']
[demo] canonical (first 120 chars):
{"category_type":"mfusion","dual":{"1":"1","g":"g"},"encoding":"float","format":"ac-mfusion","fusion_rules":{"(1,1)":{"1":1},...
[demo] sha256: 6f0e...<64 hex>
```

出现 `Loaded ... OK`、`canonical (...)` 与 `sha256:` 即 Demo 成功。

---

## 故障排查

* **ModuleNotFoundError**：确认已在仓库根执行 `pip install -e .`。
* **JSON 校验失败**：检查 `fusion_rules` 键是否形如 `"(a,b)"`，缺字段会被 schema 拒绝。
* **中文/UTF-8 乱码**：我们使用 `ensure_ascii=False`，终端需 UTF-8。
* **日志级别**：设置 `AC_LOG_LEVEL=DEBUG` 可看到更多细节。

---

## 贡献与变更

* 贡献流程：PR 前请确保 `ruff` / `mypy` / `pytest` 全绿；`pre-commit` 会自动修复末尾空白。
* 变更记录：见 `CHANGELOG.md`（M1 初始化为 `[0.1.0-dev] - M1 初始化`）。

```
