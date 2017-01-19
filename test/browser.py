#!/usr/local/bin/python2
import redgreenunittest as unittest
from resources.lib.AnimeramBrowser import AnimeramBrowser

__all__ = [ "TestBrowser" ]

class TestBrowser(unittest.TestCase):
    def __init__(self, *args, **kargs):
        super(TestBrowser, self).__init__(*args, **kargs)
        self.browser = AnimeramBrowser()

    def test_get_latest(self):
        latest = self.browser.get_latest()
        self.assertEqual(len(latest) > 10, True)

if __name__ == "__main__":
    unittest.main()
