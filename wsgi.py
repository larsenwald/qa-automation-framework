"""Entry point: `flask --app wsgi seed` then `flask --app wsgi run`."""
from shoplite import create_app

app = create_app()

if __name__ == "__main__":
    app.run(port=5000, debug=False)
