# Week 3 · Exercise 2 — Josep Coll
# Derived from week-03/demos/03-mcp-server-minimal/server.py
# © 2026 Marc Alier i Forment (UPC) — CC BY-NC-SA 4.0. Derivative under the same license.

"""
🔌 The same minimal MCP server, grown fat: 1 tool -> 6 tools.

The bodies are canned strings — they cost nothing. What costs is the REGISTRY:
the name, the description and the JSON schema of every tool, which the client
reads with tools/list and hands to the model at the head of EVERY request,
whether the model uses them or not.

So the descriptions here are written the way you would write them for real: a
useless description makes a useless tool, and an honest measurement needs
honest descriptions.

Run it over stdio:  uv run server_6tools.py
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("acme-robotics")

# canned data — offline, so the demo needs no network
_SPECS = {
    "pallet pup": "Pallet Pup: top speed 2.4 m/s, 9 h battery, carries up to 600 kg, runs PupOS.",
    "shelf cat":  "Shelf Cat: top speed 0.9 m/s, reaches 8 m racking, shares the PupOS platform.",
}


@mcp.tool()
def get_robot_spec(model: str) -> str:
    """Return the spec sheet for an Acme Robotics model (e.g. 'Pallet Pup', 'Shelf Cat')."""
    return _SPECS.get(model.strip().lower(), f"No spec on file for {model!r}.")


# ---------------------------------------------------------------------------
# Five more tools, in the style of the one above. Canned bodies, real descriptions.
# ---------------------------------------------------------------------------

@mcp.tool()
def get_warehouse_map(site: str, floor: int = 0) -> str:
    """Return the aisle-by-aisle layout of an Acme customer warehouse, including
    charging docks, racking heights and the no-go zones the robots must avoid.
    Use the site code printed on the customer contract (e.g. 'GIR-01') and the
    floor number, counting the ground floor as 0."""
    return (f"{site} floor {floor}: aisles A1-A14 (racking 8 m), charging docks D1-D3 "
            f"by the loading bay, no-go zone around the freight lift.")


@mcp.tool()
def open_support_ticket(robot_id: str, severity: str, summary: str) -> str:
    """Open a support ticket with Acme Robotics field service for a robot that is
    misbehaving. Severity must be one of 'low', 'normal', 'high' or 'line-down';
    'line-down' pages the on-call engineer immediately. The summary should say
    what the robot was doing when the fault appeared. Returns the ticket id."""
    return f"Ticket ACM-4471 opened for {robot_id} ({severity}): {summary}"


@mcp.tool()
def check_battery_health(robot_id: str) -> str:
    """Report the battery health of one robot: charge cycles used, measured
    capacity against the factory rating, and the date the pack is due for
    replacement. Use it before promising a customer a full shift of autonomy."""
    return (f"{robot_id}: 812 cycles, 91% of rated capacity, pack due for "
            f"replacement 2027-03.")


@mcp.tool()
def schedule_maintenance(robot_id: str, date: str, task: str) -> str:
    """Book a maintenance slot for a robot with the field-service team. The date
    must be ISO (YYYY-MM-DD) and the task should name the work to be done, for
    example 'replace drive wheel' or 'annual safety inspection'. Slots are held
    for 48 h and then released."""
    return f"Maintenance for {robot_id} booked on {date}: {task}. Slot held 48 h."


@mcp.tool()
def list_firmware_versions(platform: str = "PupOS") -> str:
    """List the firmware versions available for an Acme robot platform, newest
    first, marking which one is the current long-term-support release and which
    ones are withdrawn. Use it before advising a customer to upgrade."""
    return ("PupOS 4.2.1 (LTS, current), 4.1.7, 4.0.9 (withdrawn — braking bug), "
            "3.9.4 (end of support 2026-12).")


@mcp.resource("acme://company")
def company() -> str:
    """Background facts about Acme Robotics that the model may read."""
    return ("Acme Robotics, founded 2019 in Girona, builds small autonomous warehouse "
            "robots. CEO Berta Comas. Motto: 'small robots, heavy lifting.'")


if __name__ == "__main__":
    mcp.run()  # stdio transport (JSON-RPC over stdin/stdout)
