#!/bin/env python3
from flask import (
    Flask,
    render_template,
)
from pyyamlconfig import load_config
from pyrtorrent import Rtorrent

app = Flask(__name__)
_CONFIG = load_config('config.yaml')
_CLIENTS = _CONFIG.get('clients')


@app.template_filter('human_size')
def do_filesizeformat(value, binary=False):
    """Stolen from jinja2, but outputs "B" instad of "Bytes"
    Format the value like a 'human-readable' file size (i.e. 13 kB,
    4.1 MB, 102 Bytes, etc).  Per default decimal prefixes are used (Mega,
    Giga, etc.), if the second parameter is set to `True` the binary
    prefixes are used (Mebi, Gibi).
    """
    value = float(value)
    base = binary and 1024 or 1000
    prefixes = [
        (binary and 'KiB' or 'kB'),
        (binary and 'MiB' or 'MB'),
        (binary and 'GiB' or 'GB'),
        (binary and 'TiB' or 'TB'),
        (binary and 'PiB' or 'PB'),
        (binary and 'EiB' or 'EB'),
        (binary and 'ZiB' or 'ZB'),
        (binary and 'YiB' or 'YB')
    ]
    if value < base:
        return '%d B' % value
    else:
        for i, prefix in enumerate(prefixes):
            unit = base ** (i + 2)
            if value < unit:
                return '%.1f %s' % ((base * value / unit), prefix)
        return '%.1f %s' % ((base * value / unit), prefix)


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
    app.run(debug=_CONFIG.get('debug'))
