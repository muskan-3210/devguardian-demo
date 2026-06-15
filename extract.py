"""
Demo: extract data from a web link and render it with a Jinja2 template.

Run:
    python extract.py                       # uses a default demo URL
    python extract.py https://example.com   # any URL you like

Output:
    report.html  (open it in a browser)

Uses only `requests` + `jinja2` + the Python standard library, so it
runs without installing anything extra (no BeautifulSoup needed).
"""

import sys
from html.parser import HTMLParser

import requests
from jinja2 import Environment, FileSystemLoader

DEFAULT_URL = "https://example.com"


class PageParser(HTMLParser):
    """Tiny HTML parser that pulls out the title, links and visible text."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.links = []          # list of (href, text)
        self.paragraphs = []     # visible <p> text

        self._in_title = False
        self._in_p = False
        self._in_a = False
        self._current_href = ""
        self._buffer = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "p":
            self._in_p = True
            self._buffer = []
        elif tag == "a":
            self._in_a = True
            self._current_href = attrs.get("href", "")
            self._buffer = []

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "p" and self._in_p:
            self._in_p = False
            text = "".join(self._buffer).strip()
            if text:
                self.paragraphs.append(text)
        elif tag == "a" and self._in_a:
            self._in_a = False
            text = "".join(self._buffer).strip()
            if self._current_href and text:
                self.links.append((self._current_href, text))

    def handle_data(self, data):
        if self._in_title:
            self.title += data.strip()
        if self._in_p or self._in_a:
            self._buffer.append(data)


def extract(url):
    """Fetch a URL and return a dict of the data we care about."""
    resp = requests.get(url, timeout=10, headers={"User-Agent": "demo-bot/1.0"})
    resp.raise_for_status()

    parser = PageParser()
    parser.feed(resp.text)

    return {
        "url": url,
        "status": resp.status_code,
        "title": parser.title or "(no title found)",
        "links": parser.links,
        "paragraphs": parser.paragraphs,
        "link_count": len(parser.links),
    }


def render(data, template_dir="templates", template_name="report.html.j2"):
    """Render the extracted data through a Jinja2 template -> HTML string."""
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=True,  # escape HTML so scraped content is safe to display
    )
    template = env.get_template(template_name)
    return template.render(**data)


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    print(f"Fetching: {url}")

    data = extract(url)
    print(f"  status      : {data['status']}")
    print(f"  title       : {data['title']}")
    print(f"  links found : {data['link_count']}")
    print(f"  paragraphs  : {len(data['paragraphs'])}")

    html = render(data)
    out_file = "report.html"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nDone. Open {out_file} in your browser.")


if __name__ == "__main__":
    main()
