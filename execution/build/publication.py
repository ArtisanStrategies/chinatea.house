"""Explicit publication policy for generated page families.

The source database contains every mechanically valid tea pair. That is useful
for analysis, but it is not a publication decision. Only pairs listed here may
be rendered and linked on the public site.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar


T = TypeVar("T")


# These pairs earned impressions/clicks in Search Console or represent a
# particularly useful same-style comparison. They remain noindex until their
# copy is independently reviewed; inclusion here only makes the on-site tool
# available and prevents thousands of orphaned generated pages.
PUBLIC_COMPARISON_IDS = frozenset({
    "alishan-oolong-vs-dong-ding",
    "alishan-oolong-vs-lishan-oolong",
    "alishan-oolong-vs-tieguanyin-classic",
    "gunpowder-vs-chunmee",
    "osmanthus-oolong-vs-daye-oolong",
    "tie-guan-yin-vs-osmanthus-oolong",
    "tie-guan-yin-vs-tieguanyin-classic",
    "xi-hu-longjing-vs-shi-feng-longjing",
})


def select_public_comparisons(comparisons: Iterable[T]) -> list[T]:
    """Return public comparison records in deterministic ID order."""
    selected = [item for item in comparisons if item.id in PUBLIC_COMPARISON_IDS]
    return sorted(selected, key=lambda item: item.id)
