#!/bin/env python3
from flask import (
    Flask,
    render_template,
)
from pyyamlconfig import load_config
from pyrtorrent import Rtorrent
from jinja2.filters import do_filesizeformat

app = Flask(__name__)


@app.template_filter('human_size')
def human_size(value, binary=False):
    """
    Modify do_filesizeformat from jinja2 to shorten Bytes to B
    """
    size = do_filesizeformat(value, binary=binary)
    size = size.replace('Bytes', 'B')
    size = size.replace('Byte', 'B')
    return size


def all_torrents(client):
    rtorrent = Rtorrent(client.get('url'))
    return rtorrent.all_torrents()


def fetch_torrents(client, active, sort=True):
    torrents = all_torrents(client)
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
    for client in app.config.get('clients'):
        clients.append(
            fetch_torrents(client, active),
        )
    return render_template(
        'index.html',
        clients=clients,
        active=active,
    )

if __name__ == '__main__':
    _CONFIG = load_config('config.yaml')
    app.config['clients'] = _CONFIG.get('clients')
    app.run(debug=_CONFIG.get('debug'))
