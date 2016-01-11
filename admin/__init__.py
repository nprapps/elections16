import app_config
import datetime
import json
import logging

from . import utils
from collections import OrderedDict
from flask import Flask, make_response, render_template
from flask_admin import Admin
from flask_admin.contrib.peewee import ModelView
from models import models
from render_utils import make_context, smarty_filter, urlencode_filter
from static.blueprint import static
from werkzeug.debug import DebuggedApplication

app = Flask(__name__)
app.debug = app_config.DEBUG

try:
    file_handler = logging.FileHandler('%s/admin_app.log' % app_config.SERVER_LOG_PATH)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
except IOError:
    print 'Could not open %s/admin_app.log, skipping file-based logging' % app_config.SERVER_LOG_PATH

app.logger.setLevel(logging.INFO)

app.register_blueprint(static, url_prefix='/%s' % app_config.PROJECT_SLUG)

app.add_template_filter(smarty_filter, name='smarty')
app.add_template_filter(urlencode_filter, name='urlencode')

admin = Admin(app, url='/%s/admin' % app_config.PROJECT_SLUG)
admin.add_view(ModelView(models.Result))
admin.add_view(ModelView(models.Call))

# Example application views
@app.route('/%s/calls/' % app_config.PROJECT_SLUG, methods=['GET'])
def calls_admin():
    results = utils.filter_results()
    grouped = utils.group_results_by_race(results)

    context = make_context(asset_depth=1)
    context.update({
        'races': grouped
    })

    return make_response(render_template('calls.html', **context))

@app.route('/%s/calls/call-npr' % app_config.PROJECT_SLUG, methods=['POST'])
def call_npr():
    pass

@app.route('/%s/calls/accept-ap' % app_config.PROJECT_SLUG, methods=['POST'])
def accept_ap():
    from flask import request

    race_id = request.form.get('race_id')

    results = models.Result.select().where(
        (models.Result.raceid == race_id)
    )

    for result in results:
        call = result.call[0]
        if call.accept_ap == True:
            call.accept_ap = False
        else:
            call.accept_ap = True
        call.save()

    return 'Success', 200


@app.route('/%s/test/' % app_config.PROJECT_SLUG, methods=['GET'])
def _test_app():
    """
    Test route for verifying the application is running.
    """
    app.logger.info('Test URL requested.')

    return make_response(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# Example of rendering index.html with admin_app
@app.route ('/%s/' % app_config.PROJECT_SLUG, methods=['GET'])
def index():
    """
    Example view rendering a simple page.
    """
    context = make_context(asset_depth=1)

    return make_response(render_template('index.html', **context))

# Enable Werkzeug debug pages
if app_config.DEBUG:
    wsgi_app = DebuggedApplication(app, evalex=False)
else:
    wsgi_app = app
