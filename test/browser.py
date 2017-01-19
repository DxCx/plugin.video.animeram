#!/usr/local/bin/python2
import redgreenunittest as unittest

__all__ = [ "TestBrowser" ]

class TestBrowser(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

if __name__ == "__main__":
    unittest.main()
