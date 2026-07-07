"""ShopLite: a small storefront used as the application under test."""
import os
import secrets

from flask import Flask

from . import db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SHOPLITE_SECRET_KEY", secrets.token_hex(16)),
        DATABASE=os.environ.get("SHOPLITE_DB", os.path.join(app.instance_path, "shoplite.sqlite")),
    )
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)

    from . import auth, shop
    app.register_blueprint(auth.bp)
    app.register_blueprint(shop.bp)

    return app
