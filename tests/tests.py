from rtorrent_web import app
from unittest import TestCase
import mock


class TestRtorrentWeb(TestCase):
    def assert_has_content(self, content):
        self.assertIn(
            content,
            self.result.data.decode(),
            msg=self.result.data.decode(),
        )

    def setUp(self):
        # Mock torrents
        self.mock_torrents = mock.patch('rtorrent_web.all_torrents').start()
        self.mock_torrent = mock.Mock()
        self.mock_torrents.return_value = [
            self.mock_torrent,
        ]

        # Data for mock torrent
        self.mock_torrent.completed_percent = 100
        self.mock_torrent.up_rate = 1024
        self.mock_torrent.down_rate = 0
        self.mock_torrent.size = 4096
        self.mock_torrent.uploaded = 8192
        self.mock_torrent.ratio = 4.051112
        self.mock_torrent.name = 'Fedora 25 Server'
        self.mock_torrent.status = 'Seeding'

        app.config['clients'] = [
            {
                'url': 'http://example.com:8008',
                'title': 'Fedora',
            }
        ]
        self.app = app.test_client()
        self.result = self.app.get('/')

    def test_title(self):
        """
        Test that there is a title
        """
        self.assert_has_content(
            "Martin's Kickass rTorrent view",
        )

    def test_category(self):
        """
        Test that the category title is shown in the sidebar
        """
        self.assert_has_content(
            '<a href="/?active=Fedora">Fedora</a></li>',
        )

    def test_all_category_active(self):
        """
        Test that the "All" category is active if none are selected
        """
        self.assert_has_content(
            '<li class="active"><a href="/">All<span class="sr-only">(current)</span></a></li>',
        )

    def test_selected_category_active(self):
        """
        Test that the selected category is active
        """
        self.result = self.app.get('/?active=Fedora')
        self.assert_has_content(
            '<li class="active"><span class="sr-only">(current)</span><a href="/?active=Fedora">Fedora</a></li>'
        )

    def test_has_torrents(self):
        """
        Test that a torrent exists
        """
        self.assert_has_content(
            '<td class="torrent_name" id="Fedora 25 Server">',
        )

    def test_has_progressbar(self):
        """
        Test that the torrent has a progress bar
        """
        self.assert_has_content(
            'class="progress-bar progress-bar-success"',
        )

    def test_has_loading_progressbar(self):
        """
        Test that the progress bar is striped if active
        """
        self.mock_torrent.completed_percent = 80
        self.result = self.app.get('/')
        self.assert_has_content(
            'class="progress-bar progress-bar-striped active"',
        )

    def test_human_readable_numbers(self):
        """
        Test that numbers are human readable
        """
        self.assert_has_content(
            '<td class="col-md-1 rate">1.0 kB / 0 B</td>',
        )

    def test_ratio_decimal_places(self):
        """
        Test that ratio only shows a couple of decimal places
        """
        self.assert_has_content(
            '<td class="col-md-1 ratio">4.05</td>'
        )
