import unittest
from libbmc.fetcher import *


class TestFetcher(unittest.TestCase):
    def test_download(self):
        dl, contenttype = download('http://arxiv.org/pdf/1312.4006.pdf')
        self.assertIn(contenttype, ['pdf', 'djvu'])
        self.assertNotEqual(dl, '')

    def test_download_invalid_type(self):
        self.assertEqual(download('http://phyks.me/'), (None, None))

    def test_download_invalid_url(self):
        self.assertEqual(download('a'), (None, None))
