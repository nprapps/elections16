#!/usr/bin/env python

"""
Commands for rendering various parts of the app stack.
"""

import codecs
from glob import glob
import os

from fabric.api import local, task

import app

def _fake_context(path):
    """
    Create a fact request context for a given path.
    """
    return app.app.test_request_context(path=path)

def _view_from_name(name):
    """
    Determine what module a view resides in, then get
    a reference to it.
    """
    bits = name.split('.')

    # Determine which module the view resides in
    if len(bits) > 1:
        module, name = bits
    else:
        module = 'app'

    return globals()[module].__dict__[name]

@task
def less():
    """
    Render LESS files to CSS.
    """
    for path in glob('less/*.less'):
        filename = os.path.split(path)[-1]
        name = os.path.splitext(filename)[0]
        out_path = 'www/css/%s.less.css' % name

        try:
            local('node_modules/less/bin/lessc %s %s' % (path, out_path))
        except:
            print 'It looks like "lessc" isn\'t installed. Try running: "npm install"'
            raise

@task
def jst():
    """
    Render Underscore templates to a JST package.
    """
    try:
        local('node_modules/universal-jst/bin/jst.js --template underscore jst www/js/templates.js')
    except:
        print 'It looks like "jst" isn\'t installed. Try running: "npm install"'

@task
def app_config_js():
    """
    Render app_config.js to file.
    """
    from static.blueprint import _app_config_js

    with _fake_context('/js/app_config.js'):
        response = _app_config_js()

    with open('www/js/app_config.js', 'w') as f:
        f.write(response.data)

@task
def copytext_js():
    """
    Render COPY to copy.js.
    """
    from static.blueprint import _copy_js

    with _fake_context('/js/copytext.js'):
        response = _copy_js()

    with open('www/js/copy.js', 'w') as f:
        f.write(response.data)


@task
def render_simple_route(view_name):
    from flask import url_for

    with app.app.test_request_context():
        path = url_for(view_name)

    with app.app.test_request_context(path=path):
        view = app.__dict__[view_name]
        content = view()

    output_path = '.%s_html' % view_name
    _write_file(output_path, path, content)


@task
def render_results():
    from flask import url_for

    view_name = 'results'
    parties = ['gop', 'dem']

    for party in parties:
        with app.app.test_request_context():
            path = url_for(view_name, party=party)

        with app.app.test_request_context(path=path):
            view = app.__dict__[view_name]
            content = view(party)

        output_path = '.%s_html' % view_name
        _write_file(output_path, path, content)


@task
def render_card_route(slug):
    from flask import url_for

    view_name = 'card'

    with app.app.test_request_context():
        full_path = url_for(view_name, slug=slug)
        simplified_path = full_path.replace('/%s' % view_name, '')

    with app.app.test_request_context(path=full_path):
        view = app.__dict__[view_name]
        content = view(slug)

    output_path = '.%s_html' % slug
    _write_file(output_path, simplified_path, content)


def _write_file(output_path, path, content):
    path = '%s%s' % (output_path, path)

    # Ensure path exists
    head = os.path.split(path)[0]

    try:
        os.makedirs(head)
    except OSError:
        pass

    with codecs.open('%sindex.html' % path, 'w', 'utf-8') as f:
        f.write(content)

@task(default=True)
def render_all():
    """
    Render HTML templates and compile assets.
    """
    from flask import g

    less()
    jst()
    app_config_js()
    copytext_js()

    compiled_includes = {}

    # Loop over all views in the app
    for rule in app.app.url_map.iter_rules():
        rule_string = rule.rule
        name = rule.endpoint

        # Skip utility views
        if name != 'index':
            print 'Skipping %s' % name
            continue

        # Convert trailing slashes to index.html files
        if rule_string.endswith('/'):
            filename = 'www' + rule_string + 'index.html'
        elif rule_string.endswith('.html'):
            filename = 'www' + rule_string
        else:
            print 'Skipping %s' % name
            continue

        # Create the output path
        dirname = os.path.dirname(filename)

        if not (os.path.exists(dirname)):
            os.makedirs(dirname)

        print 'Rendering %s' % (filename)

        # Render views, reusing compiled assets
        with _fake_context(rule_string):
            g.compile_includes = True
            g.compiled_includes = compiled_includes

            view = _view_from_name(name)

            content = view().data

            compiled_includes = g.compiled_includes

        # Write rendered view
        # NB: Flask response object has utf-8 encoded the data
        with open(filename, 'w') as f:
            f.write(content)

