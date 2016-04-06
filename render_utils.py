#!/usr/bin/env python

import app_config
import codecs
import copydoc
import copytext
import json
import subprocess
import time
import urllib

from datetime import datetime
from flask import Markup, g, render_template, request
from slimit import minify
from smartypants import smartypants

GDOC_TOKENS = (
    ('HEADLINE', 'headline'),
    ('SUBHED', 'subhed'),
    ('LIVEAUDIOHEADLINE', 'live_audio_headline'),
    ('LIVEAUDIOSUBHED', 'live_audio_subhed'),
    ('BANNER', 'banner'),
    ('PHOTOCREDIT', 'credit'),
    ('MOBILEPHOTOCREDIT', 'mobile_credit'),
    ('PREVIEWPHOTOCREDIT', 'preview_credit'),
    ('PREVIEWMOBILEPHOTOCREDIT', 'preview_mobile_credit'),
    ('AUDIOURL', 'audio_url'),
    ('BACKGROUNDIMAGE', 'image'),
    ('MOBILEIMAGE', 'mobile_image'),
    ('PREVIEWBACKGROUNDIMAGE', 'preview_image'),
    ('PREVIEWMOBILEIMAGE', 'preview_mobile_image'),
)

class BetterJSONEncoder(json.JSONEncoder):
    """
    A JSON encoder that intelligently handles datetimes.
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            encoded_object = obj.isoformat()
        else:
            encoded_object = json.JSONEncoder.default(self, obj)

        return encoded_object

class Includer(object):
    """
    Base class for Javascript and CSS psuedo-template-tags.

    See `make_context` for an explanation of `asset_depth`.
    """
    def __init__(self, asset_depth=0):
        self.includes = []
        self.tag_string = None
        self.asset_depth = asset_depth

    def push(self, path):
        self.includes.append(path)

        return ''

    def _compress(self):
        raise NotImplementedError()

    def _relativize_path(self, path):
        relative_path = path
        if relative_path.startswith('www/'):
            relative_path = relative_path[4:]

        depth = len(request.path.split('/')) - (2 + self.asset_depth)

        while depth > 0:
            relative_path = '../%s' % relative_path
            depth -= 1

        return relative_path

    def _get_datetime(self):
        return int(time.time())

    def render(self, path):
        if getattr(g, 'compile_includes', False):
            if path not in g.compiled_includes:
                out_path = 'www/%s' % path

                if path not in g.compiled_includes:
                    if not getattr(g, 'no_compress', False):
                        print 'Rendering %s' % out_path
                        with codecs.open(out_path, 'w', encoding='utf-8') as f:
                            f.write(self._compress())

            g.compiled_includes[path] = path
            markup = Markup(self.tag_string % (self._relativize_path(path), self._get_datetime()))
        else:
            response = ','.join(self.includes)

            response = '\n'.join([
                self.tag_string % (self._relativize_path(src), self._get_datetime()) for src in self.includes
            ])

            markup = Markup(response)

        del self.includes[:]

        return markup

class JavascriptIncluder(Includer):
    """
    Psuedo-template tag that handles collecting Javascript and serving appropriate clean or compressed versions.
    """
    def __init__(self, *args, **kwargs):
        Includer.__init__(self, *args, **kwargs)

        self.tag_string = '<script type="text/javascript" src="%s?%s"></script>'

    def _compress(self):
        output = []
        src_paths = []

        for src in self.includes:
            src_paths.append('www/%s' % src)

            with codecs.open('www/%s' % src, encoding='utf-8') as f:
                print '- compressing %s' % src
                output.append(minify(f.read()))

        context = make_context()
        context['paths'] = src_paths

        header = render_template('_js_header.js', **context)
        output.insert(0, header)

        return '\n'.join(output)

class CSSIncluder(Includer):
    """
    Psuedo-template tag that handles collecting CSS and serving appropriate clean or compressed versions.
    """
    def __init__(self, *args, **kwargs):
        Includer.__init__(self, *args, **kwargs)

        self.tag_string = '<link rel="stylesheet" type="text/css" href="%s?%s" />'

    def _compress(self):
        output = []

        src_paths = []

        for src in self.includes:

            src_paths.append('%s' % src)

            try:
                compressed_src = subprocess.check_output(["node_modules/less/bin/lessc", "-x", src])
                output.append(compressed_src)
            except:
                print 'It looks like "lessc" isn\'t installed. Try running: "npm install"'
                raise

        context = make_context()
        context['paths'] = src_paths

        header = render_template('_css_header.css', **context)
        output.insert(0, header)


        return '\n'.join(output)

def flatten_app_config():
    """
    Returns a copy of app_config containing only
    configuration variables.
    """
    config = {}

    # Only all-caps [constant] vars get included
    for k, v in app_config.__dict__.items():
        if k.upper() == k:
            config[k] = v

    return config

COPY = copytext.Copy(app_config.COPY_PATH)

def make_context(asset_depth=0):
    """
    Create a base-context for rendering views.
    Includes app_config and JS/CSS includers.

    `asset_depth` indicates how far into the url hierarchy
    the assets are hosted. If 0, then they are at the root.
    If 1 then at /foo/, etc.
    """
    context = flatten_app_config()

    context['COPY'] = COPY
    context['JS'] = JavascriptIncluder(asset_depth=asset_depth)
    context['CSS'] = CSSIncluder(asset_depth=asset_depth)
    context['refresh_rate'] = 0

    if app_config.DEPLOYMENT_TARGET == 'production':
        state_var = 'prod_state'
    elif app_config.DEPLOYMENT_TARGET == 'staging':
        state_var = 'stage_state'
    else:
        state_var = 'dev_state'

    context['state'] = context['COPY']['meta'][state_var]['value']

    return context

def make_gdoc_context(doc_name):
    with open('data/%s.html' % doc_name) as f:
        html = f.read()

    gdoc = copydoc.CopyDoc(html, GDOC_TOKENS)

    gdoc_context = {}
    gdoc_context['content'] = gdoc

    for token, keyword in GDOC_TOKENS:
        if hasattr(gdoc, keyword) and getattr(gdoc, keyword):
            gdoc_context['%s' % keyword] = getattr(gdoc, keyword)

    return gdoc_context

def urlencode_filter(s):
    """
    Filter to urlencode strings.
    """
    if type(s) == 'Markup':
        s = s.unescape()

    # Evaulate COPY elements
    if type(s) is not unicode:
        s = unicode(s)

    s = s.encode('utf8')
    s = urllib.quote_plus(s)

    return Markup(s)

def smarty_filter(s):
    """
    Filter to smartypants strings.
    """
    if type(s) == 'Markup':
        s = s.unescape()

    # Evaulate COPY elements
    if type(s) is not unicode:
        s = unicode(s)

    s = s.encode('utf-8')
    s = smartypants(s)

    try:
        return Markup(s)
    except:
        return Markup(s.decode('utf-8'))
