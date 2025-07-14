import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

URL_REGEX = re.compile(r"URL='([^']*)'")

@app.route("/")
def get_wiby_url():
    try:
        wiby_response = requests.get("https://wiby.me/surprise/")
        wiby_response.raise_for_status()

        if match := URL_REGEX.search(wiby_response.text):
            url = match.group(1)

            # ── log the fumbled URL ───────────────────────────
            with open("fumbled_urls.txt", "a", encoding="utf-8") as log:
                log.write(url + "\n")
            # ─────────────────────────────────────────────────

            return jsonify(url=url)

        return "URL not found in meta tag", 404

    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}", 500


@app.route("/proxy")
def proxy_request():
    target_url = request.args.get('url')
    if not target_url:
        return "No URL provided.", 400

    try:
        proxy_response = requests.get(target_url, timeout=15)
        
        # Check if the content is HTML to rewrite links
        if 'text/html' in proxy_response.headers.get('Content-Type', ''):
            soup = BeautifulSoup(proxy_response.text, 'html.parser')

            # Rewrite links for all tags with an 'href'
            for tag in soup.find_all(href=True):
                # Turn relative URL into absolute, then point it to our proxy
                absolute_url = urljoin(target_url, tag['href'])
                tag['href'] = f'/proxy?url={absolute_url}'

            # Rewrite links for all tags with a 'src'
            for tag in soup.find_all(src=True):
                absolute_url = urljoin(target_url, tag['src'])
                tag['src'] = f'/proxy?url={absolute_url}'
            
            return str(soup)
        else:
            # If not HTML (image, css, etc.), just stream it
            return Response(proxy_response.content, status=proxy_response.status_code, content_type=proxy_response.headers['Content-Type'])

    except requests.exceptions.RequestException as e:
        return f"Could not proxy request: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)