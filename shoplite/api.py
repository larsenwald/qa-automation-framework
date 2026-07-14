"""JSON REST API. Auth is a signed, expiring bearer token (no server-side session)."""
import functools

from flask import Blueprint, current_app, g, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash

from .db import get_db
from .shop import CartError, add_item, cart_rows, get_order, place_order, stock_problems, tax_for, validate_checkout

bp = Blueprint("api", __name__, url_prefix="/api")
TOKEN_MAX_AGE = 3600


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="api-token")


def error(message, status, **extra):
    return jsonify({"error": message, **extra}), status


def token_required(view):
    @functools.wraps(view)
    def wrapped(**kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return error("Missing bearer token", 401)
        try:
            user_id = _serializer().loads(header[7:], max_age=TOKEN_MAX_AGE)
        except SignatureExpired:
            return error("Token expired", 401)
        except BadSignature:
            return error("Invalid token", 401)
        g.api_user = get_db().execute("SELECT id, username FROM users WHERE id = ?", (user_id,)).fetchone()
        if g.api_user is None:
            return error("Invalid token", 401)
        return view(**kwargs)
    return wrapped


def product_json(row):
    return {
        "id": row["id"],
        "sku": row["sku"],
        "name": row["name"],
        "category": row["category"],
        "price_cents": row["price_cents"],
        "stock": row["stock"],
        "in_stock": row["stock"] > 0,
        "description": row["description"],
    }


def order_json(order, items):
    return {
        "id": order["id"],
        "status": order["status"],
        "full_name": order["full_name"],
        "email": order["email"],
        "subtotal_cents": order["subtotal_cents"],
        "tax_cents": order["tax_cents"],
        "total_cents": order["total_cents"],
        "created_at": order["created_at"],
        "items": [
            {"sku": i["sku"], "name": i["name"], "quantity": i["quantity"], "unit_price_cents": i["unit_price_cents"]}
            for i in items
        ],
    }


@bp.errorhandler(404)
def not_found(_e):
    return error("Not found", 404)


@bp.get("/health")
def health():
    return jsonify({"status": "ok"})


@bp.post("/auth/token")
def issue_token():
    data = request.get_json(silent=True) or {}
    user = get_db().execute("SELECT * FROM users WHERE username = ?", (data.get("username", ""),)).fetchone()
    if user is None or not check_password_hash(user["password_hash"], data.get("password", "")):
        return error("Invalid username or password", 401)
    return jsonify({"token": _serializer().dumps(user["id"]), "token_type": "Bearer", "expires_in": TOKEN_MAX_AGE})


@bp.get("/products")
def list_products():
    sql, params = "SELECT * FROM products WHERE 1=1", []
    if q := request.args.get("q", "").strip():
        sql += " AND (name LIKE ? OR description LIKE ?)"
        params += [f"%{q}%", f"%{q}%"]
    if category := request.args.get("category"):
        sql += " AND category = ?"
        params.append(category)
    rows = get_db().execute(sql + " ORDER BY id", params).fetchall()
    return jsonify({"count": len(rows), "items": [product_json(r) for r in rows]})


@bp.get("/products/<int:product_id>")
def get_product(product_id):
    row = get_db().execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if row is None:
        return error("Product not found", 404)
    return jsonify(product_json(row))


def cart_json(user_id):
    rows = cart_rows(user_id)
    subtotal = sum(r["line_total"] for r in rows)
    return {
        "items": [
            {"product_id": r["id"], "sku": r["sku"], "name": r["name"], "quantity": r["quantity"],
             "unit_price_cents": r["price_cents"], "line_total_cents": r["line_total"]}
            for r in rows
        ],
        "subtotal_cents": subtotal,
        "tax_cents": tax_for(subtotal),
    }


@bp.get("/cart")
@token_required
def get_cart():
    return jsonify(cart_json(g.api_user["id"]))


@bp.post("/cart")
@token_required
def add_cart_item():
    data = request.get_json(silent=True) or {}
    product_id, quantity = data.get("product_id"), data.get("quantity", 1)
    if not isinstance(product_id, int) or not isinstance(quantity, int):
        return error("product_id and quantity must be integers", 400)
    product = get_db().execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if product is None:
        return error("Product not found", 404)
    try:
        add_item(g.api_user["id"], product, quantity)
    except CartError as exc:
        return error(str(exc), 422)
    return jsonify(cart_json(g.api_user["id"])), 201


@bp.delete("/cart/<int:product_id>")
@token_required
def remove_cart_item(product_id):
    db = get_db()
    cur = db.execute("DELETE FROM cart_items WHERE user_id = ? AND product_id = ?", (g.api_user["id"], product_id))
    db.commit()
    if cur.rowcount == 0:
        return error("Item not in cart", 404)
    return "", 204


@bp.get("/orders")
@token_required
def list_orders():
    rows = get_db().execute(
        "SELECT id, status, total_cents, created_at FROM orders WHERE user_id = ? ORDER BY id DESC",
        (g.api_user["id"],),
    ).fetchall()
    return jsonify({"count": len(rows), "items": [dict(r) for r in rows]})


@bp.get("/orders/<int:order_id>")
@token_required
def get_order_api(order_id):
    order, items = get_order(order_id, g.api_user["id"])
    return jsonify(order_json(order, items))


@bp.post("/orders")
@token_required
def create_order():
    data = request.get_json(silent=True) or {}
    form = {k: str(data.get(k, "")) for k in ("full_name", "email", "address", "zip_code")}
    errors = validate_checkout(form)
    if errors:
        return error("Validation failed", 422, fields=errors)
    rows = cart_rows(g.api_user["id"])
    if not rows:
        return error("Cart is empty", 409)
    if problems := stock_problems(rows):
        return error("Insufficient stock", 409, details=problems)
    subtotal = sum(r["line_total"] for r in rows)
    order_id = place_order(g.api_user["id"], rows, subtotal, tax_for(subtotal), form)
    order, items = get_order(order_id, g.api_user["id"])
    return jsonify(order_json(order, items)), 201
