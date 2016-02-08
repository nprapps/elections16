import app_config
import urlparse

from bs4 import BeautifulSoup
from oauth.blueprint import get_credentials

DOC_URL_TEMPLATE = 'https://www.googleapis.com/drive/v3/files/%s/export?mimeType=text/html'
ATTR_WHITELIST = {
    'a': ['href'],
    'img': ['src', 'alt'],
}


def get_google_doc(key):
    """
    Return the HTML string for a Google doc.
    """
    credentials = get_credentials()
    url = DOC_URL_TEMPLATE % key
    response = app_config.authomatic.access(credentials, url)
    return response.content


def get_google_doc_html(key):
    html_string = get_google_doc(key)
    return DocParser(html_string)


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
        self.headline = None
        self.subhed = None
        self.banner = None
        self.image = None
        self.mobile_image = None
        self.credit = None
        self.audio_url = None
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

        for tag in self.soup.findAll('a'):
            self.remove_comments(tag)

        for tag in self.soup.body.findAll():
            self.remove_empty(tag)
            self.parse_attrs(tag)
            self.find_token(tag, 'HEADLINE', 'headline')
            self.find_token(tag, 'SUBHED', 'subhed')
            self.find_token(tag, 'BANNER', 'banner')
            self.find_token(tag, 'PHOTOCREDIT', 'credit')
            self.find_token(tag, 'AUDIOURL', 'audio_url')
            self.find_image_token(tag, 'BACKGROUNDIMAGE', 'image')
            self.find_image_token(tag, 'MOBILEIMAGE', 'mobile_image')

    def remove_comments(self, tag):
        """
        Remove comments.
        """
        if tag.get('id', '').startswith('cmnt'):
            tag.parent.extract()

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
        Reject attributes not defined in ATTR_WHITELIST.
        """
        if tag.name in ATTR_WHITELIST.keys():
            for attr, value in tag.attrs.items():
                if attr in ATTR_WHITELIST[tag.name]:
                    tag.attrs[attr] = self._parse_attr(tag.name, attr, value)
                else:
                    del tag.attrs[attr]
        else:
            tag.attrs = {}

    def remove_empty(self, tag):
        """
        Remove non-self-closing tags with no children *and* no content.
        """
        has_children = len(tag.contents)
        has_text = len(list(tag.stripped_strings))
        if not has_children and not has_text and not tag.is_empty_element:
            tag.extract()

    def find_token(self, tag, token, attr):
        try:
            if not getattr(self, attr):
                text = tag.text
                if text.startswith(token):
                    setattr(self, attr, text.split(':', 1)[-1].strip())
                    tag.extract()
        except TypeError:
            pass

    def find_image_token(self, tag, token, attr):
        try:
            if not getattr(self, attr):
                text = tag.text
                if text.startswith(token):
                    value = text.split(':', 1)[-1].strip()
                    if value.startswith('http://media.npr.org'):
                        value = value.replace('http://media.npr.org', 'https://secure.npr.org')
                    setattr(self, attr, value)

                    tag.extract()
        except TypeError:
            pass

    def _parse_href(self, href):
        """
        Extract "real" URL from Google redirected url by getting `q` querystring
        parameter.
        """
        params = urlparse.parse_qs(urlparse.urlsplit(href).query)
        return params.get('q')

    def _parse_attr(self, tagname, attr, value):
        """
        Parse attribute. Delegate to href parser for hrefs, otherwise return
        value.
        """
        if tagname == 'a' and attr == 'href':
            return self._parse_href(value)
        else:
            return value

    def __unicode__(self):
        return '\n'.join([unicode(tag) for tag in self.soup.body.children])

    def __str__(self):
        return '\n'.join([str(tag) for tag in self.soup.body.children])
