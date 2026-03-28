from typing import NotRequired, TypedDict


class PluralValues(TypedDict):
    """
    Represents the quantity-based strings for an Android plurals resource.

    Attributes:
        zero: String for quantity 0 (optional).
        one: String for quantity 1 (optional).
        two: String for quantity 2 (optional).
        few: String for quantity 'few' (optional).
        many: String for quantity 'many' (optional).
        other: The default fallback string (required).
    """

    zero: NotRequired[str]
    one: NotRequired[str]
    two: NotRequired[str]
    few: NotRequired[str]
    many: NotRequired[str]
    other: str
