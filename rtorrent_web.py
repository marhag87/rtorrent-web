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


class MyTorrent():
    def __init__(self, torrent):
        self.torrent = torrent
        self.name = torrent[0]

        self.bytes_done = torrent[1]
        self.bytes_left = torrent[2]
        self.completed_percent = int(
            (self.bytes_done/(self.bytes_done + self.bytes_left))*100
        )

        self.state = torrent[3]
        self.complete = torrent[4]
        if self.state == 0:
            self.status = "Closed"
        elif self.state == 1 and self.complete:
            self.status = "Seeding"
        elif self.state == 1 and not self.complete:
            self.status = "Downloading"

        self.custom1 = torrent[5]
        self.torrent_hash = torrent[6]

        self.peers_connected = torrent[7]
        self.seeders = torrent[8]
        self.leechers = self.peers_connected - self.seeders

        self.up_rate = torrent[9]
        self.down_rate = torrent[10]
        self.size = torrent[11]
        self.uploaded = torrent[12]
        self.ratio = torrent[13]/1000


def all_torrents(client):
    rtorrent = Rtorrent(client.get('url'))
    return [
        MyTorrent(x)
        for
        x
        in
        rtorrent.multicall([
            'name',
            'bytes_done',
            'left_bytes',
            'state',
            'complete',
            'custom1',
            'hash',
            'peers_connected',
            'peers_complete',
            'get_up_rate',
            'get_down_rate',
            'size_bytes',
            'get_up_total',
            'ratio',
        ])
    ]


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
def do_action(action, client_title, torrent_hash):
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
