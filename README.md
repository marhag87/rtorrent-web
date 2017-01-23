rtorrent-web
============
A simple web client to keep track of your rtorrent clients.
Intended for use with [docker-rtorrent](https://github.com/marhag87/docker-rtorrent), but works with a normal rtorrent client.

Screenshots
-----------
### All torrents
![All torrents](/docs/screenshots/all.png?raw=true)
### Selected client
![Selected client](/docs/screenshots/selected.png?raw=true)
### Closed torrent
![Closed torrent](/docs/screenshots/closed.png?raw=true)
### Search
![Search](/docs/screenshots/search.png?raw=true)
### Settings
![Settings](/docs/screenshots/settings.png?raw=true)

Installation
------------
1. [Set up XMLRPC interface for rtorrent](https://github.com/rakshasa/rtorrent/wiki/RPC-Setup-XMLRPC)
2. Install requirements:
`pip install -r requirements.txt`
3. Run the application:
`./rtorrent_web.py`
