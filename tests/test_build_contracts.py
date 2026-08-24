from execution.build.contracts import comparison_url, hash_data, hash_text
from execution.build.publication import PUBLIC_COMPARISON_IDS, select_public_comparisons


class Comparison:
    def __init__(self, identifier: str):
        self.id = identifier


def test_hashing_accepts_unicode_text_with_current_xxhash():
    assert hash_text("龙井茶") == hash_text("龙井茶")
    assert hash_data({"tea": "龙井", "tier": 1}) == hash_data({"tier": 1, "tea": "龙井"})


def test_comparison_url_is_order_independent():
    expected = "/compare/alishan-oolong-vs-dong-ding/"
    assert comparison_url("dong-ding", "alishan-oolong") == expected
    assert comparison_url("alishan-oolong", "dong-ding") == expected


def test_publication_policy_is_explicit_and_sorted():
    records = [Comparison("not-public"), Comparison(max(PUBLIC_COMPARISON_IDS)), Comparison(min(PUBLIC_COMPARISON_IDS))]
    selected = select_public_comparisons(records)
    assert [item.id for item in selected] == sorted([min(PUBLIC_COMPARISON_IDS), max(PUBLIC_COMPARISON_IDS)])
