import unittest

from docfu import util

class UtilTest(unittest.TestCase):

    def test_uri_parse(self):
        u = 'feltnerm/foo'
        self.assertEqual(util.uri_parse(u), 'http://github.com/%s' % u)
        u = 'http://github.com/feltnerm/foo.git'
        self.assertEqual(util.uri_parse(u), u)
        u = '/User/mark/foo'
        self.assertEqual(util.uri_parse(u), 'file://' + u)

if __name__ == '__main__':
    unittest.main()

