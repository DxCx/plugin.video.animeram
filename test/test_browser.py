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

    def test_get_anime_list(self):
        "get_anime_list returns "
        anime_list = self.browser.get_anime_list('O')
        self.assertGreater(len(anime_list), 10)
        self.assertEqual(anime_list[0], {
            'url': 'animes/oban-star-racers/',
            'is_dir': True,
            'image': '',
            'name': 'Oban Star-Racers'
        })

if __name__ == "__main__":
    unittest.main()
