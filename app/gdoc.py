import app_config
import urlparse

from bs4 import BeautifulSoup
from oauth.blueprint import get_credentials

DOC_URL_TEMPLATE = 'https://www.googleapis.com/drive/v3/files/%s/export?mimeType=text/html'


def get_google_doc(key):
    """
    Return the HTML string for a Google doc.
    """
    credentials = get_credentials()
    url = DOC_URL_TEMPLATE % key
    response = app_config.authomatic.access(credentials, url)
    return response.content


class DocParser:
    """
    Clean up Google Doc html.

    To use, create a doc parser instance:

    .. code:: python

        parser = DocParser('<html><body><h1>My fake doc</h1></body></html>')

    Access rendered, parsed document:

    .. code:: python

        print unicode(parser)

    Access parsed, Beautifulsoup object:

    ..code:: python

        soup = parser.soup
    """
    def __init__(self, html_string):
        """
        Constructor takes an HTML string and sets up object.
        """
        self.soup = BeautifulSoup(html_string, 'html.parser')
        self.parse()

    def parse(self):
        """
        Run all parsing functions.
        """
        for tag in self.soup.findAll('span'):
            self.create_italic(tag)
            self.create_strong(tag)
            self.create_underline(tag)
            self.unwrap_span(tag)

        for tag in self.soup.findAll():
            self.remove_empty(tag)
            self.parse_attrs(tag)

    def create_italic(self, tag):
        """
        See if span tag has italic style and wrap with em tag.
        """
        if tag.get('style') == 'font-style:italic':
            tag.wrap(self.soup.new_tag('em'))

    def create_strong(self, tag):
        """
        See if span tag has bold style and wrap with strong tag.
        """
        if tag.get('style') == 'font-weight:bold':
            tag.wrap(self.soup.new_tag('strong'))

    def create_underline(self, tag):
        """
        See if span tag has underline style and wrap with u tag.
        """
        if tag.get('style') == 'text-decoration:underline':
            tag.wrap(self.soup.new_tag('u'))

    def unwrap_span(self, tag):
        """
        Remove span tags while preserving contents.
        """
        tag.unwrap()

    def parse_attrs(self, tag):
        """
        Preserve and parse hrefs.

        Preserve src attributes.

        Throw the rest away.
        """
        for k, v in tag.attrs.items():
            if k == 'href':
                tag.attrs[k] = self.parse_href(v)
            elif k != 'src':
                del tag.attrs[k]

    def remove_empty(self, tag):
        """
        Remove non-self-closing tags with no children *and* no content.
        """
        has_children = len(tag.contents)
        has_text = len(list(tag.stripped_strings))
        if not has_children and not has_text and not tag.is_empty_element:
            tag.extract()

    def parse_href(self, href):
        """
        Extract "real" URL from Google redirected url by getting `q` querystring
        parameter.
        """
        params = urlparse.parse_qs(urlparse.urlsplit(href).query)
        return params.get('q')

    def __unicode__(self):
        return '\n'.join([unicode(tag) for tag in self.soup.body.children])

    def __str__(self):
        return '\n'.join([str(tag) for tag in self.soup.body.children])
