import urlparse

from bs4 import BeautifulSoup

WHITELIST_ATTRIBUTES = ['href']


class DocParser:
    """
    Clean up Google Doc html.
    """
    def __init__(self, html_string):
        """
        Constructor takes an HTML string and sets up object.
        """
        self.soup = BeautifulSoup(html_string, 'html.parser')
        self.parse()

    def parse(self):
        for tag in self.soup.findAll('span'):
            self.create_italic(tag)
            self.create_strong(tag)
            self.unwrap_span(tag)

        for tag in self.soup.findAll():
            self.remove_empty(tag)
            self.parse_attrs(tag)

    def create_italic(self, tag):
        if tag.get('style') == 'font-style:italic':
            tag.wrap(self.soup.new_tag('em'))

    def create_strong(self, tag):
        if tag.get('style') == 'font-weight:bold':
            tag.wrap(self.soup.new_tag('strong'))

    def unwrap_span(self, tag):
        tag.unwrap()

    def parse_attrs(self, tag):
        for k, v in tag.attrs.items():
            if k == 'href':
                tag.attrs[k] = self.parse_href(v)
            elif k != 'src':
                del tag.attrs[k]

    def remove_empty(self, tag):
        has_children = len(tag.contents)
        has_text = len(list(tag.stripped_strings))
        if not has_children and not has_text and not tag.is_empty_element:
            tag.extract()

    def parse_href(self, href):
        params = urlparse.parse_qs(urlparse.urlsplit(href).query)
        return params.get('q')

    def __unicode__(self):
        return '\n'.join([unicode(tag) for tag in self.soup.body.children])

    def __str__(self):
        return '\n'.join([str(tag) for tag in self.soup.body.children])
