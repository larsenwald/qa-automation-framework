"""Read-only SQL access to the app's database, for verifying what the UI/API actually saved."""
import sqlite3
from contextlib import closing


class DbClient:
    def __init__(self, db_path):
        # mode=ro: tests check the data, they never change it behind the app's back.
        self.uri = f"file:{db_path}?mode=ro"

    def query(self, sql, params=()):
        with closing(sqlite3.connect(self.uri, uri=True)) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(r) for r in conn.execute(sql, params).fetchall()]

    def query_one(self, sql, params=()):
        rows = self.query(sql, params)
        assert len(rows) <= 1, f"expected at most one row, got {len(rows)}"
        return rows[0] if rows else None

    def scalar(self, sql, params=()):
        row = self.query_one(sql, params)
        return next(iter(row.values())) if row else None

    # -- domain helpers -------------------------------------------------------
    def user_id(self, username):
        return self.scalar("SELECT id FROM users WHERE username = ?", (username,))

    def stock_of(self, sku):
        return self.scalar("SELECT stock FROM products WHERE sku = ?", (sku,))

    def latest_order(self, username):
        return self.query_one(
            """SELECT o.* FROM orders o JOIN users u ON u.id = o.user_id
               WHERE u.username = ? ORDER BY o.id DESC LIMIT 1""",
            (username,),
        )

    def order_items(self, order_id):
        return self.query(
            """SELECT p.sku, oi.quantity, oi.unit_price_cents
               FROM order_items oi JOIN products p ON p.id = oi.product_id
               WHERE oi.order_id = ? ORDER BY p.sku""",
            (order_id,),
        )

    def cart_size(self, username):
        return self.scalar(
            """SELECT COALESCE(SUM(c.quantity), 0) FROM cart_items c JOIN users u ON u.id = c.user_id
               WHERE u.username = ?""",
            (username,),
        )
