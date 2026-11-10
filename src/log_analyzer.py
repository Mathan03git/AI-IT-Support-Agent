
from pathlib import Path
from collections import Counter

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_DIR / "data" / "sample.log"


# Basic rule-based troubleshooting knowledge
TROUBLESHOOTING_RULES = {
    "database connection failed": {
        "title": "Database connection failure",
        "action": (
            "Check database availability, connection settings, "
            "credentials, and network connectivity."
        ),
    },
    "memory usage": {
        "title": "High memory usage",
        "action": (
            "Inspect memory consumption and identify processes "
            "using excessive memory."
        ),
    },
    "response time exceeded": {
        "title": "Slow application response",
        "action": (
            "Check application performance, database query times, "
            "and server resource usage."
        ),
    },
}


def diagnose_error(message):
    """Suggest an action based on known error patterns."""

    message_lower = message.lower()

    for pattern, diagnosis in TROUBLESHOOTING_RULES.items():
        if pattern in message_lower:
            return diagnosis

    return {
        "title": "Unknown issue",
        "action": (
            "Review the full log entry and investigate the "
            "related application or system component."
        ),
    }


def analyze_logs(file_path):
    """Analyze log entries and suggest troubleshooting actions."""

    if not file_path.exists():
        print(f"Error: Log file not found: {file_path}")
        return

    severity_counts = Counter()
    error_counts = Counter()
    warning_messages = []

    with file_path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            for severity in ("ERROR", "WARNING", "INFO"):
                if f" {severity} " in line:
                    severity_counts[severity] += 1

                    message = line.split(
                        f" {severity} ", 1
                    )[1]

                    if severity == "ERROR":
                        error_counts[message] += 1

                    elif severity == "WARNING":
                        warning_messages.append(message)

                    break

    print("\n===== IT LOG ANALYSIS =====")
    print(f"Total log entries: {sum(severity_counts.values())}")

    for severity in ("ERROR", "WARNING", "INFO"):
        print(f"{severity}: {severity_counts[severity]}")

    print("\n===== ERROR DIAGNOSIS =====")

    if not error_counts:
        print("No errors detected.")

    for message, count in error_counts.items():
        diagnosis = diagnose_error(message)

        print(f"\nIssue: {diagnosis['title']}")
        print(f"Occurrences: {count}")
        print(f"Log message: {message}")
        print(f"Suggested action: {diagnosis['action']}")

    print("\n===== WARNINGS =====")

    if warning_messages:
        for warning in warning_messages:
            diagnosis = diagnose_error(warning)

            print(f"\nWarning: {warning}")
            print(f"Suggested action: {diagnosis['action']}")
    else:
        print("No warnings detected.")


if __name__ == "__main__":
    analyze_logs(LOG_FILE)




