# Wiby Fumble
Serve random “old-web” pages in a click.

## Quick start
```bash
git clone https://github.com/LANEW1995/fumble
python -m pip install -r requirements.txt
python app.py
# hit http://localhost:5000/ for JSON, or
# http://localhost:5000/proxy?url=<site> to view through the proxy
```
## Endpoints
| Route | What it does |
| ----- | ------------ |
| `/` | Returns `{ "url": "<random-site>" }` and logs it to `fumbled_urls.txt`. |
| `/proxy?url=<http…>` | Streams or rewrites the target page/assets. |

## License
Apache-2.0