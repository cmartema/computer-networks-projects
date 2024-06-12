import logging
import sys
from importlib import reload

from flask import Flask

from .routes import configure_routes

# Initialize logging
# logging.basicConfig(level=logging.INFO)

app = Flask(__name__, template_folder="./templates", static_folder="./static")
configure_routes(app)

if __name__ == "__main__":
    reload(logging)
    logging.basicConfig(format="%(message)s", level=logging.INFO)
    port = 5000  # Default port
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    app.run(debug=True, host="0.0.0.0", port=port)
