"""标签层级的无状态计算工具。"""

from collections import defaultdict
from typing import Iterable, Optional, Set, Tuple


def collect_descendant_tag_ids(
    root_tag_id: int,
    tag_parent_pairs: Iterable[Tuple[int, Optional[int]]],
) -> Set[int]:
    """返回根标签及其所有后代标签 ID，并在异常循环数据中安全终止。"""
    children_by_parent = defaultdict(list)
    for tag_id, parent_id in tag_parent_pairs:
        children_by_parent[parent_id].append(tag_id)

    descendant_ids = {root_tag_id}
    pending_ids = [root_tag_id]
    while pending_ids:
        parent_id = pending_ids.pop()
        for child_id in children_by_parent[parent_id]:
            if child_id not in descendant_ids:
                descendant_ids.add(child_id)
                pending_ids.append(child_id)
    return descendant_ids
