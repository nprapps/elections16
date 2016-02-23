Copyright 2016 NPR.  All rights reserved.  No part of these materials may be reproduced, modified, stored in a retrieval system, or retransmitted, in any form or by any means, electronic, mechanical or otherwise, without prior written permission from NPR.

(Want to use this code? Send an email to nprapps@npr.org!)


Elections 2016
========================

* [What is this?](#what-is-this)
* [Assumptions](#assumptions)
* [What's in here?](#whats-in-here)
* [Bootstrap the project](#bootstrap-the-project)
* [Data commands](#data-commands)
* [Hide project secrets](#hide-project-secrets)
* [Save media assets](#save-media-assets)
* [Add a page to the site](#add-a-page-to-the-site)
* [Run the project](#run-the-project)
* [COPY configuration](#copy-configuration)
* [COPY editing](#copy-editing)
* [Arbitrary Google Docs](#arbitrary-google-docs)
* [Run Python tests](#run-python-tests)
* [Run Javascript tests](#run-javascript-tests)
* [Compile static assets](#compile-static-assets)
* [Test the rendered app](#test-the-rendered-app)
* [Deploy to S3](#deploy-to-s3)
* [Deploy to EC2](#deploy-to-ec2)
* [Install cron jobs](#install-cron-jobs)
* [Install web services](#install-web-services)
* [Run a remote fab command](#run-a-remote-fab-command)
* [Report analytics](#report-analytics)

What is this?
-------------

A rig to consume and display 2016 election results, from primaries through the general election.

Assumptions
-----------

The following things are assumed to be true in this documentation.

* You are running OSX.
* You are using Python 2.7. (Probably the version that came OSX.)
* You have [virtualenv](https://pypi.python.org/pypi/virtualenv) and [virtualenvwrapper](https://pypi.python.org/pypi/virtualenvwrapper) installed and working.
* You have NPR's AWS credentials stored as environment variables locally.
* You have a local PostgreSQL instance running (RDS required for AWS deployment).

For more details on the technology stack used with the app-template, see our [development environment blog post](http://blog.apps.npr.org/2013/06/06/how-to-setup-a-developers-environment.html).

What's in here?
---------------

The project contains the following folders and important files:

* ``admin`` -- A [Flask](http://flask.pocoo.org/) app to be deployed to a server that provides the admin UI.
  - ``__init__.py``: The admin Flask app.
  - ``templates``: Admin app templates.
* ``app`` -- A [Flask](http://flask.pocoo.org/) app used to build the public, static site.
  - ``__init__.py``: The public Flask app.
  - ``templates``: Public app templates.
* ``app_config.py`` -- Global project configuration for scripts, deployment, etc.
* ``confs`` -- Server configuration files for [nginx](https://www.nginx.com/resources/wiki/) and [uwsgi](https://uwsgi-docs.readthedocs.org/en/latest/). Edit the templates and run ``fab <dev/production/staging> servers.render_confs``, don't edit anything in ``confs/rendered`` directly.
* ``crontab`` -- Cron jobs to be installed as part of the project.
* ``data`` -- Data files, such as those used to generate HTML.
* ``etc`` -- Miscellaneous scripts and metadata for project bootstrapping.
* ``fabfile`` -- [Fabric](http://docs.fabfile.org/en/latest/) commands for automating setup, deployment, data processing, etc.
* ``jst`` -- Javascript ([Underscore.js](http://documentcloud.github.com/underscore/#template)) templates.
* ``less`` -- [LESS](http://lesscss.org/) files, will be compiled to CSS and concatenated for deployment.
* ``oauth`` -- [Flask blueprint](http://flask.pocoo.org/docs/0.10/blueprints/) that manages access to Google Drive.
* ``render_utils.py`` -- Code supporting template rendering.
* ``requirements.txt`` -- Python requirements.
* ``static`` -- [Flask blueprint](http://flask.pocoo.org/docs/0.10/blueprints/) that serves up static files.
* ``tests`` -- [Nose2](https://github.com/nose-devs/nose2) Python unit tests.
* ``www`` -- Static and compiled assets to be deployed. (a.k.a. "the output")
* ``www/assets`` -- Synchronizes with an S3 bucket containing binary assets (images, audio).
* ``www/live-data`` -- "Live" data deployed to S3 via cron jobs or other mechanisms. (Not deployed with the rest of the project.)
* ``www/js/test`` -- Javascript tests and supporting files.

Bootstrap the project
---------------------

Node.js is required for the static asset pipeline. If you don't already have it, get it like this:

```
brew install node
curl https://npmjs.org/install.sh | sh
```

Then bootstrap the project:

```
cd elections16
mkvirtualenv elections16
pip install -r requirements.txt
npm install
fab update
fab data.bootstrap_db
fab data.load_results
fab data.create_calls
fab data.load_delegates
```

**Problems installing requirements?** You may need to run the pip command as ``ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future pip install -r requirements.txt`` to work around an issue with OSX.

Data commands
-------------

Reset the database and rebuild from scratch:

```
fab dev data.bootstrap_db
```

Load results for next election:

```
fab dev data.load_results
```

Load results for specific election with a date parameter:

```
fab dev data.load_results:2015-11-03
```

To run on a server:

```
fab staging master servers.fabcast:data.load_results:2015-11-03
```

Controlling State
------------------

There are four states to the app: before, during, after and inactive.

You can control the app state separately for local development, staging, and production through the `meta` sheet of the copy spreadsheet. Those variables are called `dev_state`, `stage_state`, and `prod_state` respectively.

Defining a state determines the card stack that the app renders. Those card stacks are defined in their respective sheets in the copy spreadsheet.

Additionally, you can control the state of the live audio in the app. For live audio to function in the app, the `live_audio` card must be in the stack that matches the state of the app, and the `live_audio` variable in the `meta` sheet must be set to `live`. If the live audio card is in the current stack, but you want to turn the live audio off, set `live_audio` in the `meta` sheet to `inactive`.

## Live events

### Bootstrapping Database

To get ready for a new live election event, ensure you do the following before results come in from the AP.

1. Ensure `NEXT_ELECTION_DATE` in `app_config.py` is set to the current election date.
2. Ensure `ELEX_FLAGS` under the `else` deployment target in `app_config.py` is empty.
3. Rebootstrap your local database: `fab data.bootstrap_db`
4. Check the results cards locally and make sure the data is zeroed out, showing the correct elections and candidates.
5. Ensure `ELEX_FLAGS` under the `production` deployment target in `app_config.py` is empty.
6. Ensure `RESULTS_DEPLOY_INTERVAL` under the `production` deployment target in `app_config.py` is set to 15.
7. If you made any changes to app_config, deploy the latest to Github and make sure it is merged into the stable branch.
8. Ensure the server's code base is up-to-date: `fab production stable servers.checkout_latest`
9. Bootstrap the database on the server: `fab production servers.fabcast:data.bootstrap_db`
10. Deploy to the server and restart the deploy service: `fab production stable deploy_server`
11. Go to [54.189.43.202/elections16/calls](54.189.43.202/elections16/calls)  and set all races to accept AP calls unless Domenico/Beth have noted an exception.

### Changing the card stack

1. Change `dev_state` in the `meta` sheet of the copy spreadsheet to the state you are moving to.
2. If we are going to during mode with live audio, make sure `live_audio` in the `meta` sheet of the copy spreadsheet is set to `live`.
3. Pull the spreadsheet locally with `fab text`.
4. Ensure that all the cards are supposed to be in the stack. Check [this document](https://docs.google.com/drawings/d/1wzBoldr0cE5K6a0_eLAMm0lVjvcLqcVFaFvDZ_aPOx8/edit) to see what each stack should contain. Also make sure that audio is playing in the app if applicable.
5. Ensure production server code base is up-to-date: `fab production stable servers.checkout_latest`
6. Deploy the latest to the client: `fab production stable servers.fabcast:deploy_client`

### Ending the live event

It is likely that the live audio coverage will end before the data stops coming in and before the after mode cards are ready. To account for  this scenario, do the following:

1. Change `live_audio` in the `meta` sheet of the copy spreadsheet to `inactive`.
2. If you have the app open with live audio running, make sure that the audio stops itself within a few minutes.

When the after cards are ready, follow the steps for changing the card stack.


Generating custom font
----------------------

This project uses a custom font build powered by [Fontello](http://fontello.com)
If the font does not exist, it will be created when running `fab update`.
To force generation of the custom font, run:

```
fab utils.install_font:true
```

Editing the font is a little tricky -- you have to use the Fontello web gui.
To open the gui with your font configuration, run:

```
fab utils.open_font
```

Now edit the font, download the font pack, copy the new config.json into this
project's `fontello` directory, and run `fab utils.install_font:true` again.

Hide project secrets
--------------------

Project secrets should **never** be stored in ``app_config.py`` or anywhere else in the repository. They will be leaked to the client if you do. Instead, always store passwords, keys, etc. in environment variables and document that they are needed here in the README.

Any environment variable that starts with ``$PROJECT_SLUG_`` will be automatically loaded when ``app_config.get_secrets()`` is called.

Save media assets
-----------------

Large media assets (images, videos, audio) are synced with an Amazon S3 bucket specified in ``app_config.ASSETS_S3_BUCKET`` in a folder with the name of the project. (This bucket should not be the same as any of your ``app_config.PRODUCTION_S3_BUCKETS`` or ``app_config.STAGING_S3_BUCKETS``.) This allows everyone who works on the project to access these assets without storing them in the repo, giving us faster clone times and the ability to open source our work.

Syncing these assets requires running a couple different commands at the right times. When you create new assets or make changes to current assets that need to get uploaded to the server, run ```fab assets.sync```. This will do a few things:

* If there is an asset on S3 that does not exist on your local filesystem it will be downloaded.
* If there is an asset on that exists on your local filesystem but not on S3, you will be prompted to either upload (type "u") OR delete (type "d") your local copy.
* You can also upload all local files (type "la") or delete all local files (type "da"). Type "c" to cancel if you aren't sure what to do.
* If both you and the server have an asset and they are the same, it will be skipped.
* If both you and the server have an asset and they are different, you will be prompted to take either the remote version (type "r") or the local version (type "l").
* You can also take all remote versions (type "ra") or all local versions (type "la"). Type "c" to cancel if you aren't sure what to do.

Unfortunantely, there is no automatic way to know when a file has been intentionally deleted from the server or your local directory. When you want to simultaneously remove a file from the server and your local environment (i.e. it is not needed in the project any longer), run ```fab assets.rm:"www/assets/file_name_here.jpg"```

Adding a page to the site
-------------------------

A site can have any number of rendered pages, each with a corresponding template and view. To create a new one:

* Add a template to the ``templates`` directory. Ensure it extends ``_base.html``.
* Add a corresponding view function to ``app.py``. Decorate it with a route to the page name, i.e. ``@app.route('/filename.html')``
* By convention only views that end with ``.html`` and do not start with ``_``  will automatically be rendered when you call ``fab render``.

Run the project
---------------

A flask app is used to run the project locally. It will automatically recompile templates and assets on demand.

```
workon $PROJECT_SLUG
fab app
```

Visit [localhost:8000](http://localhost:8000) in your browser.

COPY configuration
------------------

This app uses a Google Spreadsheet for a simple key/value store that provides an editing workflow.

To access the Google doc, you'll need to create a Google API project via the [Google developer console](http://console.developers.google.com).

Enable the Drive API for your project and create a "web application" client ID.

For the redirect URIs use:

* `http://localhost:8000/authenticate/`
* `http://127.0.0.1:8000/authenticate`
* `http://localhost:8888/authenticate/`
* `http://127.0.0.1:8888/authenticate`

For the Javascript origins use:

* `http://localhost:8000`
* `http://127.0.0.1:8000`
* `http://localhost:8888`
* `http://127.0.0.1:8888`

You'll also need to set some environment variables:

```
export GOOGLE_OAUTH_CLIENT_ID="something-something.apps.googleusercontent.com"
export GOOGLE_OAUTH_CONSUMER_SECRET="bIgLonGStringOfCharacT3rs"
export AUTHOMATIC_SALT="jAmOnYourKeyBoaRd"
```

Note that `AUTHOMATIC_SALT` can be set to any random string. It's just cryptographic salt for the authentication library we use.

Once set up, run `fab app` and visit `http://localhost:8000` in your browser. If authentication is not configured, you'll be asked to allow the application for read-only access to Google drive, the account profile, and offline access on behalf of one of your Google accounts. This should be a one-time operation across all app-template projects.

It is possible to grant access to other accounts on a per-project basis by changing `GOOGLE_OAUTH_CREDENTIALS_PATH` in `app_config.py`.


COPY editing
------------

View the [sample copy spreadsheet](https://docs.google.com/spreadsheet/pub?key=0AlXMOHKxzQVRdHZuX1UycXplRlBfLVB0UVNldHJYZmc#gid=0).

This document is specified in ``app_config`` with the variable ``COPY_GOOGLE_DOC_KEY``. To use your own spreadsheet, change this value to reflect your document's key. (The long string of random looking characters in your Google Docs URL. For example: ``1DiE0j6vcCm55Dyj_sV5OJYoNXRRhn_Pjsndba7dVljo``)

A few things to note:

* If there is a column called ``key``, there is expected to be a column called ``value`` and rows will be accessed in templates as key/value pairs
* Rows may also be accessed in templates by row index using iterators (see below)
* You may have any number of worksheets
* This document must be "published to the web" using Google Docs' interface

The app template is outfitted with a few ``fab`` utility functions that make pulling changes and updating your local data easy.

To update the latest document, simply run:

```
fab text.update
```

Note: ``text.update`` runs automatically whenever ``fab render`` is called.

At the template level, Jinja maintains a ``COPY`` object that you can use to access your values in the templates. Using our example sheet, to use the ``byline`` key in ``templates/index.html``:

```
{{ COPY.attribution.byline }}
```

More generally, you can access anything defined in your Google Doc like so:

```
{{ COPY.sheet_name.key_name }}
```

You may also access rows using iterators. In this case, the column headers of the spreadsheet become keys and the row cells values. For example:

```
{% for row in COPY.sheet_name %}
{{ row.column_one_header }}
{{ row.column_two_header }}
{% endfor %}
```

When naming keys in the COPY document, please attempt to group them by common prefixes and order them by appearance on the page. For instance:

```
title
byline
about_header
about_body
about_url
download_label
download_url
```

Arbitrary Google Docs
----------------------

Sometimes, our projects need to read data from a Google Doc that's not involved with the COPY rig. In this case, we've got a helper function for you to download an arbitrary Google spreadsheet.

This solution will download the uncached version of the document, unlike those methods which use the "publish to the Web" functionality baked into Google Docs. Published versions can take up to 15 minutes up update!

Make sure you're authenticated, then call `oauth.get_document(key, file_path)`.

Here's an example of what you might do:

```
from copytext import Copy
from oauth import get_document

def read_my_google_doc():
    file_path = 'data/extra_data.xlsx'
    get_document('0AlXMOHKxzQVRdHZuX1UycXplRlBfLVB0UVNldHJYZmc', file_path)
    data = Copy(file_path)

    for row in data['example_list']:
        print '%s: %s' % (row['term'], row['definition'])

read_my_google_doc()
```

Run Python tests
----------------

Python unit tests are stored in the ``tests`` directory. Run them with ``fab tests``.

Run Javascript tests
--------------------

With the project running, visit [localhost:8000/test/SpecRunner.html](http://localhost:8000/test/SpecRunner.html).

Compile static assets
---------------------

Compile LESS to CSS, compile javascript templates to Javascript and minify all assets:

```
workon elections16
fab render
```

(This is done automatically whenever you deploy to S3.)

Test the rendered app
---------------------

If you want to test the app once you've rendered it out, just use the Python webserver:

```
cd www
python -m SimpleHTTPServer
```

Deploy to S3
------------

```
fab staging master deploy
```

Deploy to EC2
-------------

You can deploy to EC2 for a variety of reasons. We cover two cases: Running a dynamic web application (`public_app.py`) and executing cron jobs (`crontab`).

Servers capable of running the app can be setup using our [servers](https://github.com/nprapps/servers) project.

For running a Web application:

* In ``app_config.py`` set ``DEPLOY_TO_SERVERS`` to ``True``.
* Also in ``app_config.py`` set ``DEPLOY_WEB_SERVICES`` to ``True``.
* Run ``fab staging master servers.setup`` to configure the server.
* Run ``fab staging master deploy`` to deploy the app.

For running cron jobs:

* In ``app_config.py`` set ``DEPLOY_TO_SERVERS`` to ``True``.
* Also in ``app_config.py``, set ``INSTALL_CRONTAB`` to ``True``
* Run ``fab staging master servers.setup`` to configure the server.
* Run ``fab staging master deploy`` to deploy the app.

You can configure your EC2 instance to both run Web services and execute cron jobs; just set both environment variables in the fabfile.

You will also need to set any secrets that for local development come from workinprivate in `/etc/environment'.

Install cron jobs
-----------------

Cron jobs are defined in the file `crontab`. Each task should use the `cron.sh` shim to ensure the project's virtualenv is properly activated prior to execution. For example:

```
* * * * * ubuntu bash /home/ubuntu/apps/elections16/repository/cron.sh fab $DEPLOYMENT_TARGET cron_jobs.test
```

To install your crontab set `INSTALL_CRONTAB` to `True` in `app_config.py`. Cron jobs will be automatically installed each time you deploy to EC2.

The cron jobs themselves should be defined in `fabfile/cron_jobs.py` whenever possible.

Install web services
---------------------

Web services are configured in the `confs/` folder.

Running ``fab servers.setup`` will deploy your confs if you have set ``DEPLOY_TO_SERVERS`` and ``DEPLOY_WEB_SERVICES`` both to ``True`` at the top of ``app_config.py``.

To check that these files are being properly rendered, you can render them locally and see the results in the `confs/rendered/` directory.

```
fab servers.render_confs
```

You can also deploy only configuration files by running (normally this is invoked by `deploy`):

```
fab servers.deploy_confs
```

Run a  remote fab command
-------------------------

Sometimes it makes sense to run a fabric command on the server, for instance, when you need to render using a production database. You can do this with the `fabcast` fabric command. For example:

```
fab staging master servers.fabcast:deploy
```

If any of the commands you run themselves require executing on the server, the server will SSH into itself to run them.

Analytics
---------

The Google Analytics events tracked in this application are:

|Category|Action|Label|Value|
|--------|------|-----|-----|
|elections16|tweet|`location`||
|elections16|facebook|`location`||
|elections16|email|`location`||
|elections16|new-comment||
|elections16|open-share-discuss||
|elections16|close-share-discuss||
|elections16|summary-copied||
|elections16|featured-tweet-action|`action`|
|elections16|featured-facebook-action|`action`|
