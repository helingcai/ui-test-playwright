from decimal import Decimal
import re

"""字符串中获取价格"""


def parse_money(text: str) -> Decimal:
    """
        从 'Item total: $39.98' 提取 Decimal('39.98')
        """
    match = re.search(r"\$([\d.]+)", text)
    assert match, f"无法从文本中解析金额：{text}"
    return Decimal(match.group(1))
