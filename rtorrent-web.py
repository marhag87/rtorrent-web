#!/bin/env python3
from flask import (
    Flask,
    render_template,
)
from pyyamlconfig import load_config
from pyrtorrent import Rtorrent

app = Flask(__name__)
_CLIENTS = load_config('config.yaml').get('clients')


def fetch_torrents(client, sort=True):
    rtorrent = Rtorrent(client.get('url'))
    torrents = rtorrent.all_torrents()
    if sort:
        torrents.sort(key=lambda x: x.name)
    return {
        'torrents': torrents,
        'title': client.get('title'),
    }


@app.route('/')
def dashboard():
    clients = []
    for client in _CLIENTS:
        clients.append(
            fetch_torrents(client),
        )
    return render_template(
        'index.html',
        clients=clients,
    )

if __name__ == '__main__':
    app.run()
