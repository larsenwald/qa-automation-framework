from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from .auth import login_required
from .db import get_db

bp = Blueprint("shop", __name__)

SORTS = {
    "name": "name ASC",
    "price_asc": "price_cents ASC",
    "price_desc": "price_cents DESC",
}


@bp.app_template_filter("money")
def money(cents):
    return f"${cents / 100:,.2f}"


@bp.route("/")
def index():
    db = get_db()
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "")
    sort = request.args.get("sort", "name")

    sql = "SELECT * FROM products WHERE 1=1"
    params = []
    if q:
        sql += " AND (name LIKE ? OR description LIKE ?)"
        params += [f"%{q}%", f"%{q}%"]
    if category:
        sql += " AND category = ?"
        params.append(category)
    sql += " ORDER BY " + SORTS.get(sort, SORTS["name"])

    products = db.execute(sql, params).fetchall()
    categories = [r["category"] for r in db.execute("SELECT DISTINCT category FROM products ORDER BY category")]
    return render_template("index.html", products=products, categories=categories,
                           q=q, category=category, sort=sort)


@bp.route("/product/<int:product_id>")
def product(product_id):
    item = get_db().execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if item is None:
        abort(404)
    return render_template("product.html", product=item)


def cart_rows(user_id):
    return get_db().execute(
        """SELECT p.id, p.name, p.sku, p.price_cents, c.quantity,
                  p.price_cents * c.quantity AS line_total
           FROM cart_items c JOIN products p ON p.id = c.product_id
           WHERE c.user_id = ? ORDER BY p.name""",
        (user_id,),
    ).fetchall()


@bp.app_context_processor
def inject_cart_count():
    if getattr(g, "user", None) is None:
        return {"cart_count": 0}
    row = get_db().execute(
        "SELECT COALESCE(SUM(quantity), 0) FROM cart_items WHERE user_id = ?", (g.user["id"],)
    ).fetchone()
    return {"cart_count": row[0]}


@bp.route("/cart")
@login_required
def cart():
    rows = cart_rows(g.user["id"])
    subtotal = sum(r["line_total"] for r in rows)
    return render_template("cart.html", rows=rows, subtotal=subtotal)


@bp.route("/cart/add/<int:product_id>", methods=("POST",))
@login_required
def add_to_cart(product_id):
    db = get_db()
    item = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if item is None:
        abort(404)
    qty = request.form.get("quantity", 1, type=int)
    db.execute(
        """INSERT INTO cart_items (user_id, product_id, quantity) VALUES (?, ?, ?)
           ON CONFLICT (user_id, product_id) DO UPDATE SET quantity = quantity + excluded.quantity""",
        (g.user["id"], product_id, qty),
    )
    db.commit()
    flash(f"Added {item['name']} to your cart.", "success")
    return redirect(url_for("shop.cart"))


@bp.route("/cart/remove/<int:product_id>", methods=("POST",))
@login_required
def remove_from_cart(product_id):
    db = get_db()
    db.execute("DELETE FROM cart_items WHERE user_id = ? AND product_id = ?", (g.user["id"], product_id))
    db.commit()
    flash("Item removed.", "info")
    return redirect(url_for("shop.cart"))
