# Changelog

## [0.1.0-dev] - M1 初始化
- 项目骨架与最小 CLI（`ac --version/--info`）
- Schema v0（mfusion/umtc-input/umtc-output）
- 统一 IO（load_*/write_*）、日志规范（D1/C3）
- Canonical JSON 串化（D2）与哈希/指纹（D3）
- Provenance 最小注入与来源链（E）
- README（M1 版）与 Demo 脚本
## [0.1.0-dev] - M2-A1/A2 浮点基础层
- 新增 `float_backend`（有限性检测、Neumaier 求和、稳定二范数、负零统一）
- 新增 `NumericPolicy`（容差、格式化、数组重排、env 覆盖与快照）
- CLI 增补 `ac num --show-policy`；README/文档记录数值策略示例
