"""Common timezones for locations (USA, Pakistan, UTC). IANA names used by Celery task."""

# Label shown in admin UI, value stored in DB and used with zoneinfo
TIMEZONE_CHOICES: list[tuple[str, str]] = [
    ("UTC", "UTC"),
    # USA
    ("America/New_York", "USA (Eastern)"),
    ("America/Chicago", "USA (Central)"),
    ("America/Denver", "USA (Mountain)"),
    ("America/Los_Angeles", "USA (Pacific)"),
    ("America/Phoenix", "USA (Arizona)"),
    # Pakistan
    ("Asia/Karachi", "Pakistan (PKT)"),
    # Other common
    ("Europe/London", "UK (GMT/BST)"),
    ("Asia/Dubai", "UAE (GST)"),
    ("Asia/Kolkata", "India (IST)"),
]


def get_timezone_options() -> list[dict[str, str]]:
    """Return list of {value, label} for API/dropdowns."""
    return [{"value": value, "label": label} for value, label in TIMEZONE_CHOICES]
