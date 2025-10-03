import pytest

from anyon_condense.core.exceptions import CanonicalizationError
from anyon_condense.core.hashing import hash_json_value, sha256_of_payload
from anyon_condense.core.utils import canonical_json_dump


def test_canonical_same_dict_different_key_order_equal_strings():
    # 相同语义，不同键顺序
    a = {"b": 2, "a": 1, "c": {"y": 2, "x": 1}}
    b = {"c": {"x": 1, "y": 2}, "a": 1, "b": 2}

    sa = canonical_json_dump(a)
    sb = canonical_json_dump(b)

    # 1) 字符级相等
    assert sa == sb

    # 2) 基础形状：键被排序；无空格、无换行；UTF-8 直出
    assert sa.startswith('{"a":')
    assert " " not in sa and "\n" not in sa
    assert "\\u" not in sa  # 允许非 ASCII 直出


def test_hash_same_payload_equal_and_stable():
    a = {"foo": 1, "bar": {"x": 2, "y": 3.0}}
    b = {"bar": {"y": 3.0, "x": 2}, "foo": 1}  # 键顺序不同

    ha = sha256_of_payload(a)
    hb = sha256_of_payload(b)

    assert ha.startswith("sha256:") and hb.startswith("sha256:")
    assert ha == hb  # 顺序不影响哈希


def test_hash_changes_when_value_changes():
    a = {"k": 1}
    b = {"k": 2}  # 仅值不同
    assert sha256_of_payload(a) != sha256_of_payload(b)


def test_negative_zero_normalized_consistency():
    # -0.0 与 0.0 归一后 canonical 串与哈希应一致（稳健性附加用例）
    a = {"x": -0.0, "y": 1.0}
    b = {"x": 0.0, "y": 1.0}
    sa = canonical_json_dump(a)
    sb = canonical_json_dump(b)
    assert sa == sb
    assert sha256_of_payload(a) == sha256_of_payload(b)


def test_hash_json_value_scalar_and_list_smoke():
    # 兼测 hash_json_value（用于对子结构求指纹的通用通道）
    h1 = hash_json_value(["a", 1, 2.0, True, None])
    h2 = hash_json_value(["a", 1, 2.0, True, None])
    assert h1 == h2 and h1.startswith("sha256:")


def test_canonical_rejects_nonfinite_and_top_level_type():
    import math

    # 非有限浮点应抛 CanonicalizationError
    with pytest.raises(CanonicalizationError):
        canonical_json_dump({"x": math.nan})

    # 顶层必须是 dict
    with pytest.raises(CanonicalizationError):
        canonical_json_dump(["x", "y"])  # type: ignore[arg-type]
