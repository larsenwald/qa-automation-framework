"""Demo data so the app (and the test suite) always starts from a known state."""
import click
from werkzeug.security import generate_password_hash

from .db import get_db, init_db

USERS = [
    ("standard_user", "secret_sauce"),
    ("qa_lead", "Passw0rd!"),
]

PRODUCTS = [
    ("KB-001", "Mechanical Keyboard", "Electronics", 8999, 25, "Hot-swappable switches, RGB backlight."),
    ("MS-002", "Wireless Mouse", "Electronics", 2999, 40, "Silent clicks, 70-hour battery."),
    ("HD-003", "Noise-Cancelling Headphones", "Electronics", 14999, 10, "Over-ear, 30 hours of playback."),
    ("MN-004", "27in 4K Monitor", "Electronics", 32999, 5, "IPS panel, USB-C power delivery."),
    ("BK-005", "Clean Code", "Books", 3499, 30, "A handbook of agile software craftsmanship."),
    ("BK-006", "The Art of Software Testing", "Books", 4299, 12, "The classic on test design."),
    ("BK-007", "Lessons Learned in Software Testing", "Books", 3899, 8, "293 lessons from the trenches."),
    ("MG-008", "Bug Hunter Mug", "Home", 1499, 60, "12oz ceramic, dishwasher safe."),
    ("DL-009", "Desk Lamp", "Home", 3999, 15, "Dimmable LED with USB charging port."),
    ("PL-010", "Desk Plant", "Home", 1999, 0, "Low-maintenance pothos. Currently out of stock."),
    ("ST-011", "Sticker Pack", "Accessories", 599, 200, "Ten vinyl dev stickers."),
    ("BP-012", "Laptop Backpack", "Accessories", 6999, 18, "Fits 16in laptops, water resistant."),
]


def seed():
    init_db()
    db = get_db()
    db.executemany(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        [(u, generate_password_hash(p)) for u, p in USERS],
    )
    db.executemany(
        "INSERT INTO products (sku, name, category, price_cents, stock, description) VALUES (?, ?, ?, ?, ?, ?)",
        PRODUCTS,
    )
    db.commit()


@click.command("seed")
def seed_command():
    """Reset the database and load demo users and products."""
    seed()
    click.echo(f"Seeded {len(USERS)} users and {len(PRODUCTS)} products.")
