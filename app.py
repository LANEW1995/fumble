import requests
import re
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)
CORS(app)

URL_REGEX = re.compile(r"URL='([^']*)'")

@app.route("/")
def get_wiby_url():
    try:
        response = requests.get("https://wiby.me/surprise/")
        response.raise_for_status()
        if match := URL_REGEX.search(response.text):
            return jsonify(url=match.group(1))
        return "URL not found in meta tag", 404
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}", 500

@app.route("/proxy")
def proxy_request():
    target_url = request.args.get('url')
    if not target_url:
        return "No URL provided.", 400

    try:
        resp = requests.get(target_url, timeout=15)
        
        # Check if the content is HTML to rewrite links
        if 'text/html' in resp.headers.get('Content-Type', ''):
            soup = BeautifulSoup(resp.text, 'html.parser')

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
            return Response(resp.content, status=resp.status_code, content_type=resp.headers['Content-Type'])

    except requests.exceptions.RequestException as e:
        return f"Could not proxy request: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)