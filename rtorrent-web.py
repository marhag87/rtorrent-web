#!/bin/env python3
from flask import (
    Flask,
    render_template,
)
from pyrtorrent import Rtorrent
app = Flask(__name__)
series_client = Rtorrent('http://192.168.1.2:8008')
movies_client = Rtorrent('http://192.168.1.2:8009')

@app.route('/')
def hello():
    series = series_client.all_torrents()
    series.sort(key=lambda x: x.name)
    movies = movies_client.all_torrents()
    movies.sort(key=lambda x: x.name)
    return render_template(
        'index.html',
        series=series,
        movies=movies,
    )

if __name__ == '__main__':
    app.run()
