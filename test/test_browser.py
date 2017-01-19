#!/usr/local/bin/python2
import unittest
from resources.lib.AnimeramBrowser import AnimeramBrowser

__all__ = [ "TestBrowser" ]

class TestBrowser(unittest.TestCase):
    def __init__(self, *args, **kargs):
        super(TestBrowser, self).__init__(*args, **kargs)
        self.browser = AnimeramBrowser()

    def test_get_latest(self):
        "get_latest resturns at least 10 items"
        latest = self.browser.get_latest()
        self.assertGreater(len(latest), 10)

    def test_get_anime_episodes(self):
        "get_anime_episodes works for one-piece"
        episodes = self.browser.get_anime_episodes("one-piece")
        self.assertEqual(len(episodes) > 750, True)
        self.assertEqual(episodes[-1], {
            'url': 'play/one-piece/1',
            'is_dir': False, 'image': '',
            'name': "One Piece 1 : I'm Luffy! The boy who will become the Pirate King!"
        })

if __name__ == "__main__":
    unittest.main()
