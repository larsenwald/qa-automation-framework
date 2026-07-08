"""'Lab' pages that exercise the trickier WebDriver features:
JS alerts, iframes, multiple windows, and content that loads late."""
from flask import Blueprint, render_template

bp = Blueprint("lab", __name__, url_prefix="/lab")

PAGES = [
    ("alerts", "JavaScript alerts", "alert(), confirm() and prompt() dialogs"),
    ("frames", "Frames", "A support chat widget embedded in an iframe"),
    ("windows", "Windows & tabs", "Links that open the store policy in a new window"),
    ("dynamic", "Dynamic loading", "Content and buttons that show up after a delay"),
]


@bp.route("/")
def index():
    return render_template("lab/index.html", pages=PAGES)


@bp.route("/alerts")
def alerts():
    return render_template("lab/alerts.html")


@bp.route("/frames")
def frames():
    return render_template("lab/frames.html")


@bp.route("/frames/chat")
def chat_widget():
    return render_template("lab/chat_widget.html")


@bp.route("/windows")
def windows():
    return render_template("lab/windows.html")


@bp.route("/windows/policy")
def policy():
    return render_template("lab/policy.html")


@bp.route("/dynamic")
def dynamic():
    return render_template("lab/dynamic.html")
