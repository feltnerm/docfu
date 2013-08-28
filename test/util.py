import unittest

import json

from docfu import util

class UtilTest(unittest.TestCase):

    def test_uri_parse(self):
        u = 'feltnerm/foo'
        self.assertEqual(util.uri_parse(u), 'http://github.com/%s' % u)
        u = 'http://github.com/feltnerm/foo.git'
        self.assertEqual(util.uri_parse(u), u)
        u = '/User/mark/foo'
        self.assertEqual(util.uri_parse(u), 'file://' + u)

    def test_parse_package_json(self):
        path = './test-package.json'
        pkg_file = open(path, 'r')
        pkg_obj_control = json.loads(pkg_file.read())
        pkg_obj = util.parse_package_json(path)
        self.assertEqual(pkg_obj_control, pkg_file)

def main():
    unittest.main()

if __name__ == '__main__':
    main()

