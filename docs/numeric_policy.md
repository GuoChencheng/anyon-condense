# Numeric Policy & Normalized Hashing

## Why normalize first?
- 同一个浮点值在不同平台/解释器上可能呈现为不同字符串（例如 `0.000000000001` vs `1e-12`）。
- 如果直接对 canonical JSON 串化结果做 sha256，同语义对象可能得到不同指纹。
- 解决方案：**数值归一化 → canonical → sha256**。
  - 归一化会统一 `-0.0` 为 `+0.0`，拒绝 `NaN/±Inf`，并在十进制域按策略量化；
  - 可选地对纯标量扁平数组排序，减少平台差异；
  - 归一化后的对象仍是「数值语义」，因此 canonical/哈希不会改变业务信息。

## NumericPolicy: fields & defaults

```json
{
  "mode": "float",
  "fmt": "auto",
  "precision": 12,
  "round_half": "even",
  "tol_abs": 1e-10,
  "tol_rel": 1e-10,
  "array_reorder": false,
  "clip_small": true
}
```

| 字段 | 说明 |
| --- | --- |
| `fmt` | `fixed`：固定 `precision` 位小数；`scientific`：`precision` 位有效数字；`auto`：中等量级用定点，小/大量级用科学计数法。 |
| `precision` | 十进制量化精度，与 `fmt` 共同作用。 |
| `round_half` | `even`（银行家舍入）或 `away`（远离 0）。 |
| `tol_abs` / `tol_rel` | M2-C1 的近似比较阈值。 |
| `array_reorder` | 仅在数组元素全为纯 `int/float` 时排序，含 `bool`/嵌套时保持原序。 |
| `clip_small` | 在阈值内裁剪为 0，稳定串化。 |

## Configuration: defaults < env < overrides

| 层级 | 示例 |
| --- | --- |
| 环境变量 | `AC_NUMERIC_FMT=scientific AC_NUMERIC_PREC=6`<br>`AC_TOL_ABS=1e-12 AC_TOL_REL=1e-9`<br>`AC_ARRAY_REORDER=true` |
| CLI 覆盖 | `ac num dump --fmt fixed --precision 6 --in file.json` |

常用环境变量：`AC_NUMERIC_FMT`、`AC_NUMERIC_PREC`、`AC_TOL_ABS`、`AC_TOL_REL`、`AC_ARRAY_REORDER`、`AC_CLIP_SMALL`。

## Hashing: raw vs normalized

- `sha256_of_payload(obj)`: **raw**；不做归一化，保留 M1 兼容行为。
- `sha256_of_payload_normalized(obj, policy)`: **推荐**；先 `normalize_payload_numbers`，再 canonical，最后 sha256。

使用建议：
- **发布、对拍、快照基线** → 用 normalized；
- **兼容历史数据** → 使用 raw，同时在文档里说明潜在的跨平台差异。

## CLI quick reference

```bash
# 查看当前策略（已经吸收 env 覆盖）
ac num show-policy

# 归一化串化预览（默认策略）
ac num dump --in tests/examples/Vec_Z2_mfusion.json

# CLI 覆盖（示例：fixed，6 位小数）
ac num dump --in tests/examples/Vec_Z2_mfusion.json --fmt fixed --precision 6
```

`show-policy` 输出 canonical JSON 快照；`dump` 打印两行：

```
PREFIX: {<canonical json prefix, first 120 chars>}
SHA256: sha256:<hash>
```

## Provenance

写出路径可将策略快照写入 `provenance.numeric_policy`：

```json
"provenance": {
  "generated_by": "ac 0.1.0-dev",
  "date": "2025-10-05T23:52:51Z",
  "toolchain_version": "py3.12|Darwin-arm64",
  "numeric_policy": {
    "mode": "float",
    "tol_abs": 1e-10,
    "tol_rel": 1e-10,
    "fmt": "auto",
    "precision": 12,
    "round_half": "even",
    "array_reorder": false,
    "clip_small": true
  },
  "sources": ["tests/examples/Vec_Z2_mfusion.json"]
}
```

这样任何人都可以在另一台机器上复用相同策略 → 归一化 → canonical → hash 的流程。
