"""
Demo web app: enter a link, extract its data, show it in the browser.

Run:
    python app.py
Then open:
    http://127.0.0.1:5001

Reuses the extraction logic from extract.py and renders with Jinja2
(Flask uses Jinja2 under the hood, so templates/ is shared).
"""

from flask import Flask, render_template, request

from extract import extract

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    url = request.args.get("url", "").strip()
    data = None
    error = None

    if url:
        try:
            data = extract(url)
        except Exception as exc:  # keep the demo simple: show any failure
            error = str(exc)

    return render_template("index.html.j2", url=url, data=data, error=error)


if __name__ == "__main__":
    # Different port (5001) for manual testing.
    app.run(host="127.0.0.1", port=5001, debug=True)
