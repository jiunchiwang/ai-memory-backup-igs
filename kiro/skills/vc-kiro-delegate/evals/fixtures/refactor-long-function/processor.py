"""Data processing module."""

from datetime import datetime


def process_data(records: list[dict], config: dict) -> dict:
    """Process a list of records and return aggregated statistics.

    This function is intentionally long — it validates, filters, transforms,
    aggregates, and formats in one pass. It should be refactored into smaller
    well-named helpers while keeping the exact same external behavior.
    """
    # Step 1: validate input
    if not isinstance(records, list):
        raise TypeError("records must be a list")
    if not isinstance(config, dict):
        raise TypeError("config must be a dict")
    required_config_keys = {"min_value", "max_value", "date_field", "value_field"}
    missing = required_config_keys - set(config.keys())
    if missing:
        raise ValueError(f"config missing keys: {missing}")

    min_value = config["min_value"]
    max_value = config["max_value"]
    date_field = config["date_field"]
    value_field = config["value_field"]
    category_field = config.get("category_field", "category")

    # Step 2: filter out invalid records
    filtered = []
    for r in records:
        if not isinstance(r, dict):
            continue
        if date_field not in r or value_field not in r:
            continue
        if not isinstance(r[value_field], (int, float)):
            continue
        try:
            parsed_date = datetime.fromisoformat(r[date_field])
        except (ValueError, TypeError):
            continue
        if r[value_field] < min_value or r[value_field] > max_value:
            continue
        r_copy = dict(r)
        r_copy["_parsed_date"] = parsed_date
        filtered.append(r_copy)

    # Step 3: sort by date ascending
    filtered.sort(key=lambda x: x["_parsed_date"])

    # Step 4: aggregate by category
    by_category: dict = {}
    for r in filtered:
        cat = r.get(category_field, "uncategorized")
        if cat not in by_category:
            by_category[cat] = {
                "count": 0,
                "sum": 0.0,
                "min": float("inf"),
                "max": float("-inf"),
                "first_date": None,
                "last_date": None,
            }
        entry = by_category[cat]
        value = r[value_field]
        entry["count"] += 1
        entry["sum"] += value
        if value < entry["min"]:
            entry["min"] = value
        if value > entry["max"]:
            entry["max"] = value
        if entry["first_date"] is None:
            entry["first_date"] = r["_parsed_date"]
        entry["last_date"] = r["_parsed_date"]

    # Step 5: compute averages and format output
    result = {
        "total_records": len(records),
        "valid_records": len(filtered),
        "categories": {},
    }
    for cat, entry in by_category.items():
        avg = entry["sum"] / entry["count"] if entry["count"] else 0.0
        result["categories"][cat] = {
            "count": entry["count"],
            "sum": round(entry["sum"], 2),
            "avg": round(avg, 2),
            "min": entry["min"],
            "max": entry["max"],
            "first_date": entry["first_date"].isoformat() if entry["first_date"] else None,
            "last_date": entry["last_date"].isoformat() if entry["last_date"] else None,
        }

    return result
