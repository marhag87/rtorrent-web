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


@app.route('/torrents/')
@app.route('/torrents/<active>')
def torrents(active=False):
    clients = []
    for client in app.config.get('clients'):
        clients.append(
            fetch_torrents(client, active),
        )
    return render_template(
        'torrents.html',
        clients=clients,
        active=active,
    )


@app.route('/<action>/<client_title>/<torrent_hash>')
def stop(action, client_title, torrent_hash):
    found = False
    for client in app.config['clients']:
        if client.get('title') == client_title:
            rtorrent = Rtorrent(client.get('url'))
            found = True

    if not found:
        return "Could not find torrent", 404

    torrent = rtorrent.torrent_by_hash(torrent_hash)
    if action == 'stop':
        torrent.stop()
        message = "stopped"
    elif action == 'start':
        torrent.start()
        message = "started"
    elif action == 'remove':
        torrent.erase()
        message = "removed"
    elif action == 'seen':
        torrent.custom1 = 'Seen'
        message = "marked as seen"
    else:
        return "Action not supported", 404

    return "Torrent {}".format(message)


@app.route('/mark_all_seen')
def mark_all_seen():
    for client in app.config['clients']:
        rtorrent = Rtorrent(client.get('url'))
        for torrent in rtorrent.all_torrents():
            torrent.custom1 = 'Seen'

    return "Marked all as seen"

if __name__ == '__main__':
    _CONFIG = load_config('config.yaml')
    app.config['clients'] = _CONFIG.get('clients')
    app.run(debug=_CONFIG.get('debug'))
