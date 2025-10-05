
# Numeric Policy (M2-A2)

`NumericPolicy` 统一管理浮点容差、格式化与数组重排，保证跨机器可复现。

## 默认参数

```yaml
mode: float
fmt: auto
precision: 12
tol_abs: 1e-10
tol_rel: 1e-10
round_half: even
array_reorder: false
clip_small: true
```

- **tol_abs / tol_rel**：混合容差，比较时使用 `max(tol_abs, tol_rel * max(|a|, |b|))`。
- **fmt**：`auto` 根据数量级在定点/科学计数法间切换；`fixed` 固定小数位；`scientific` 使用有效数字。
- **round_half**：`even`（银行家舍入）或 `away`（ties away from zero）。
- **clip_small**：将 `|x| < 10^(-(precision+1))` 的数裁剪为 `0.0`。
- **array_reorder**：如果数组为纯标量且允许重排，则按升序排序（先统一负零）。

## 核心函数

| 函数 | 功能 |
| --- | --- |
| `NumericPolicy.snapshot()` | 返回可写入 provenance 的策略快照 |
| `approx_equal(a, b, policy)` | 近似比较，自动归一负零/裁剪噪声 |
| `format_float(x, policy)` | 根据策略生成十进制字符串 |
| `clip_small(x, policy)` | 单值归一：拒绝非有限、统一负零、裁剪极小值 |
| `reorder_scalar_array(arr, policy)` | 纯标量数组可按升序重排，其它保持原序 |
| `policy_from_env(env, overrides)` | 读取环境变量并应用 overrides |

## 环境变量

| 变量 | 说明 |
| --- | --- |
| `AC_NUMERIC_FMT` | 设置 `fmt`（auto/fixed/scientific） |
| `AC_NUMERIC_PREC` | 设置 `precision` |
| `AC_TOL_ABS` / `AC_TOL_REL` | 设置绝对/相对容差 |
| `AC_ROUND_HALF` | 设置舍入策略（even/away） |
| `AC_ARRAY_REORDER` | `true/false` 控制数组重排 |
| `AC_CLIP_SMALL` | `true/false` 控制极小值裁剪 |

## 配置优先级

`NumericPolicy` 的最终取值遵循：默认值 < 环境变量 < 显式 overrides。

- `get_numeric_policy(env=os.environ, overrides=...)` 会按顺序合并，确保调用方可通过参数覆盖演示/调试设置。
- CLI 子命令 `ac num --show-policy` / `ac num --dump` 也走同一通道，因此可以用 `AC_NUMERIC_*` 环境变量批量设置，再在命令行通过 `--fmt/--precision` 临时覆盖。

## CLI 演示

```bash
ac num --show-policy
ac num --dump --in tests/examples/Vec_Z2_mfusion.json --fmt fixed --precision 6
```

`show-policy` 输出 canonical JSON 快照，`dump` 会做数值归一化 → canonical 串化 → 对归一化 payload 取哈希，仅打印串化前 120 个字符与 `sha256`。

## 使用场景

1. **数值比对**：在 `check_*` 家族中调用 `approx_equal`。
2. **串化输出**：结合 `format_float` 提供稳定的十进制表示，准备在 M2-A3 中进入 normalized dump。
3. **数组排序**：对纯数值数组进行稳定排序，避免序列化 diff。
4. **追溯**：通过 `policy.snapshot()` 将策略写入 provenance，方便重放与审计。
