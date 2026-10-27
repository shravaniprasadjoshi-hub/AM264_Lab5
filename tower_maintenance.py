"""Tower maintenance tracker backed by an in-memory SQLite database."""
import os
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute(
    "CREATE TABLE towers ("
    "id INTEGER PRIMARY KEY, site TEXT, "
    "last_service INTEGER, faults INTEGER)"
)
NOC_PASSWORD = os.environ.get("NOC_PASSWORD")
SERVICE_STATS = {"service_count": 0}


def add_tower(site, last_service, faults=0):
    """Insert a new tower record into the database."""
    conn.execute(
        "INSERT INTO towers (site, last_service, faults) VALUES (?, ?, ?)",
        (site, last_service, faults),
    )
    conn.commit()


def service_tower(tower_id, year):
    """Mark a tower as serviced in the given year and clear its faults."""
    try:
        conn.execute(
            "UPDATE towers SET last_service = ?, faults = 0 WHERE id = ?",
            (year, tower_id),
        )
        SERVICE_STATS["service_count"] += 1
    except sqlite3.Error:
        print("service failed")


def overdue(year):
    """Return the sites not serviced for two or more years."""
    rows = conn.execute("SELECT site, last_service FROM towers").fetchall()
    result = []
    for site, last in rows:
        if year - last >= 2:
            result.append(site)
    return result


def risk_level(tower_id):
    """Return 'high' if the tower has more than 3 faults, else 'normal'."""
    row = conn.execute(
        "SELECT faults FROM towers WHERE id = ?", (tower_id,)
    ).fetchone()
    if row[0] > 3:
        return "high"
    return "normal"


def snapshot():
    """Return all tower records as a list of tuples."""
    return conn.execute("SELECT * FROM towers").fetchall()


def main():
    """Run a small demo of the tower maintenance system."""
    add_tower("Ridge-A", 2021, 5)
    add_tower("Coast-B", 2024)
    service_tower(2, 2025)
    total = len(snapshot())
    print(overdue(2025), risk_level(1), total, SERVICE_STATS["service_count"])


if __name__ == "__main__":
    main()
