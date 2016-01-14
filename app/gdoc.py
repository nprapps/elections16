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
        for tag in self.soup.findAll():
            self.remove_attrs(tag)
            self.remove_empty(tag)

        for tag in self.soup.findAll('span'):
            self.unwrap_span(tag)

    def remove_attrs(self, tag):
        for k,v in tag.attrs.items():
            if k not in WHITELIST_ATTRIBUTES:
                del tag.attrs[k]

    def unwrap_span(self, tag):
        if tag.name == 'span':
            tag.unwrap()

    def remove_empty(self, tag):
        return
        if not tag.text:
            tag.extract()

    def __unicode__(self):
        return '\n'.join([unicode(tag) for tag in self.soup.body.children])

    def __str__(self):
        return '\n'.join([str(tag) for tag in self.soup.body.children])
