"""
HeatGuard AI
Heatwave severity classification and sample advisory generation.
"""

def classify_severity(temperature):
    """
    Classify a temperature using illustrative thresholds.

    Returns:
        Severity category as a string.
    """
    if temperature >= 42:
        return "Extreme"
    elif temperature >= 40:
        return "High"
    elif temperature >= 37:
        return "Moderate"
    else:
        return "Low"


def get_priority(severity):
    """
    Convert severity into OS scheduling priority.
    Lower priority number means higher scheduling priority.
    """
    priority_map = {
        "Extreme": 1,
        "High": 2,
        "Moderate": 3,
        "Low": 4
    }

    return priority_map.get(severity, 4)


def generate_advisory(severity, region):
    """
    Generate a simple demonstration advisory for a region.
    """
    advisories = {
        "Extreme": (
            "Very high simulated heat risk. Avoid strenuous "
            "outdoor activity during peak heat, stay hydrated, "
            "and follow official local advisories."
        ),
        "High": (
            "High simulated heat risk. Reduce prolonged "
            "outdoor exposure and take regular cooling breaks."
        ),
        "Moderate": (
            "Moderate simulated heat risk. Stay hydrated "
            "and monitor changes in local conditions."
        ),
        "Low": (
            "Lower simulated heat risk under the current "
            "demonstration thresholds. Continue monitoring."
        )
    }

    message = advisories.get(
        severity,
        "Continue monitoring local weather conditions."
    )

    return f"{region}: {message}"
