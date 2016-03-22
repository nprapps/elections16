import app_config
import urlparse
import codecs

from bs4 import BeautifulSoup, element
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
    try:
        html_string = get_google_doc(key)
        parser = DocParser(html_string)
        with codecs.open('.{0}'.format(key), 'w', 'utf-8') as f:
            f.write(html_string)
        return parser
    except AttributeError:
        print 'ERROR DOWNLOADING {0}'.format(key)
        with codecs.open('.{0}'.format(key), 'r', 'utf-8') as f:
            return DocParser(f.read())


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
        self.live_audio_headline = None
        self.live_audio_subhed = None
        self.banner = None
        self.image = None
        self.mobile_image = None
        self.credit = None
        self.mobile_credit = None
        self.preview_image = None
        self.preview_mobile_image = None
        self.preview_credit = None
        self.preview_mobile_credit = None
        self.audio_url = None
        self.soup = BeautifulSoup(html_string, 'html.parser')
        self.tags_blacklist = []
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
            self.check_next(tag)

        for tag in self.soup.body.findAll():
            self.remove_empty(tag)
            self.remove_inline_comment(tag)
            self.parse_attrs(tag)
            self.find_token(tag, 'HEADLINE', 'headline')
            self.find_token(tag, 'SUBHED', 'subhed')
            self.find_token(tag, 'LIVEAUDIOHEADLINE', 'live_audio_headline')
            self.find_token(tag, 'LIVEAUDIOSUBHED', 'live_audio_subhed')
            self.find_token(tag, 'BANNER', 'banner')
            self.find_token(tag, 'PHOTOCREDIT', 'credit')
            self.find_token(tag, 'MOBILEPHOTOCREDIT', 'mobile_credit')
            self.find_token(tag, 'PREVIEWPHOTOCREDIT', 'preview_credit')
            self.find_token(tag, 'PREVIEWMOBILEPHOTOCREDIT', 'preview_mobile_credit')
            self.find_token(tag, 'AUDIOURL', 'audio_url')
            self.find_token(tag, 'BACKGROUNDIMAGE', 'image')
            self.find_token(tag, 'MOBILEIMAGE', 'mobile_image')
            self.find_token(tag, 'PREVIEWBACKGROUNDIMAGE', 'preview_image')
            self.find_token(tag, 'PREVIEWMOBILEIMAGE', 'preview_mobile_image')

            self.remove_blacklisted_tags(tag)

    def remove_comments(self, tag):
        """
        Remove comments.
        """
        if tag.get('id', '').startswith('cmnt'):
            tag.parent.extract()

    def check_next(self, tag):
        """
        If next tag is link with same href, combine them.
        """
        if type(tag.next_sibling) == element.Tag and tag.next_sibling.name == 'a':
            next_tag = tag.next_sibling
            if tag.get('href') and next_tag.get('href'):
                href = self._parse_href(tag.get('href'))
                next_href = self._parse_href(next_tag.get('href'))

                if href == next_href:
                    next_text = next_tag.get_text()
                    tag.append(next_text)
                    self.tags_blacklist.append(next_tag)

    def remove_blacklisted_tags(self, tag):
        if tag in self.tags_blacklist:
            tag.decompose()

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

    def remove_inline_comment(self, tag):
        text = tag.text
        if text.startswith('##'):
            tag.extract()

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
