#!/bin/env python3
from flask import (
    Flask,
    render_template,
)
from pyyamlconfig import load_config
from pyrtorrent import Rtorrent

app = Flask(__name__)
_CLIENTS = load_config('config.yaml').get('clients')


def fetch_torrents(client, active, sort=True):
    rtorrent = Rtorrent(client.get('url'))
    torrents = rtorrent.all_torrents()
    if sort:
        torrents.sort(key=lambda x: x.name)
    my_dict = {
        'torrents': torrents,
        'title': client.get('title'),
    }
    if active == client.get('title'):
        my_dict['active'] = True
    return my_dict


@app.route('/')
@app.route('/<active>')
def dashboard(active=False):
    clients = []
    for client in _CLIENTS:
        clients.append(
            fetch_torrents(client, active),
        )
    return render_template(
        'index.html',
        clients=clients,
        active=active,
    )

if __name__ == '__main__':
    app.run()
