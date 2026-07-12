import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from .db import get_db

bp = Blueprint("auth", __name__)


@bp.before_app_request
def load_user():
    user_id = session.get("user_id")
    g.user = None
    if user_id is not None:
        g.user = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def login_required(view):
    @functools.wraps(view)
    def wrapped(**kwargs):
        if g.user is None:
            # Only GET pages can be "returned to". A POST endpoint like /cart/add/2 would
            # answer the post-login GET with 405 (BUG-002).
            next_url = request.full_path.rstrip("?") if request.method == "GET" else None
            flash("Please log in to continue.", "info")
            return redirect(url_for("auth.login", next=next_url))
        return view(**kwargs)
    return wrapped


def safe_next(target):
    """Only allow same-site relative paths, so ?next= can't become an open redirect."""
    if not target or not target.startswith("/") or target.startswith("//") or "\\" in target:
        return None
    return target


@bp.route("/login", methods=("GET", "POST"))
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = get_db().execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user is None or not check_password_hash(user["password_hash"], password):
            error = "Invalid username or password."
        else:
            session.clear()
            session["user_id"] = user["id"]
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(safe_next(request.args.get("next")) or url_for("shop.index"))
    return render_template("login.html", error=error)


@bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
