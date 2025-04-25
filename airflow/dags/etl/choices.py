class Listing:
    statuses: list[str] = ["active", "sold", "expired"]
    conditions: dict[str, list] = {
        "new": ["excellent", "good"],
        "used": ["excellent", "good", "fair", "poor"]
    }
    seller_types: list[str] = ["dealer", "private"]

class User:
    user_type: list[str] = Listing.seller_types
