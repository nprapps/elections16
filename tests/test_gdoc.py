#!/usr/bin/env python

import unittest

from app.gdoc import DocParser


class DocParserTestCase(unittest.TestCase):
    """
    Test bootstrapping postgres database
    """
    def setUp(self):
        with open('tests/data/testdoc.html') as f:
            html_string = f.read()

        self.parser = DocParser(html_string)
        self.contents = self.parser.soup.body.contents

    def test_h1(self):
        self._is_tag(self.contents[0], 'h1')

    def test_h1_has_no_children(self):
        child_length = len(self.contents[0].find_all())
        self.assertEqual(child_length, 0)

    def test_h2(self):
        self._is_tag(self.contents[1], 'h2')

    def test_h3(self):
        self._is_tag(self.contents[2], 'h3')

    def test_p(self):
        self._is_tag(self.contents[3], 'p')

    def test_strong(self):
        self._contains_tag(self.contents[4], 'strong')

    def test_em(self):
        self._contains_tag(self.contents[5], 'em')

    def test_u(self):
        self._contains_tag(self.contents[6], 'u')

    def test_ignore_html(self):
        self._contains_tag(self.contents[7], 'strong', 0)

    def test_a(self):
        self._contains_tag(self.contents[8], 'a')

    def test_ahref(self):
        href = self.contents[8].a.attrs['href'][0]
        self.assertEqual(href, 'http://npr.org')

    def test_ul(self):
        self._is_tag(self.contents[9], 'ul')

    def test_ul_li(self):
        count_li = len(self.contents[9].find_all('li'))
        self.assertEqual(count_li, 3)

    def test_ol(self):
        self._is_tag(self.contents[10], 'ol')

    def test_ol_li(self):
        count_li = len(self.contents[10].find_all('li'))
        self.assertEqual(count_li, 3)

    def test_img(self):
        self._contains_tag(self.contents[11], 'img')

    def test_strange_has_no_children(self):
        child_length = len(self.contents[12].find_all())
        self.assertEqual(child_length, 0)

    def test_tabletag(self):
        self._is_tag(self.contents[13], 'table')

    def test_tabletd(self):
        self._contains_tag(self.contents[13], 'td', 4)

    def test_tabletr(self):
        self._contains_tag(self.contents[13], 'tr', 2)

    def _is_tag(self, tag, tag_name):
        self.assertEqual(tag.name, tag_name)

    def _contains_tag(self, tag, tag_name, count=1):
        child_length = len(tag.findAll(tag_name))
        self.assertEqual(child_length, count)


if __name__ == '__main__':
    unittest.main()
