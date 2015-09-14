# drv-flask-based-prototype

This repo stores prototypes of the Digital Register View. It is based on digital-register-frontend, and just like that project is written in Python and uses the Flask framework. The intention is that by staying close to digital-register-frontend we will be able to quickly copy features that have been tested by User Research back in to the real app.

## Cloning specific versions

Previous versions of the prototype used different directories for each version. We think it's better to use different branches in Git for each version.

If you need to get different versions of the prototype you can use the following command to clone a version branch into a directory with the same name. This command gets version 11 ("v11"):

```
    git clone git@github.com:LandRegistry/drv-flask-based-prototype.git v11 -b v11
```

## Setup

To create a virtual env, run the following from a shell:

```
    mkvirtualenv -p /usr/bin/python3 drv-flask-based-prototype
    source environment.sh
    pip install -r requirements.txt
```

## Run the server

### Run in dev mode

To run the server in dev mode, execute the following command:

    ./run_flask_dev.sh

### Run using gunicorn

To run the server using gunicorn, activate your virtual environment, add the application directory to python path
(e.g. `export PYTHONPATH=/vagrant/apps/drv-flask-based-prototype/:$PYTHONPATH`) and execute the following commands:

    pip install gunicorn
    gunicorn -p /tmp/gunicorn-drv-flask-based-prototype.pid service.server:app -c gunicorn_settings.py

## SASS libraries

### GOV.UK template

[govuk_template](http://alphagov.github.io/govuk_template/)

In order to update:
* download the 'plain HTML' version and replace the `static/govuk_template` folder with its assets
* replace the `govuk_template.html` file in the `static/templates` folder with its HTML file

### GOV.UK frontend toolkit

[govuk_frontend_toolkit](https://github.com/alphagov/govuk_frontend_toolkit)

It is included in our `static` folder as a gitsubmodule. It can be updated by bumping up its commit hash.

## Dependencies

WeasyPrint (used to generate the PDFs) needs some dependencies. They can be installed by running the following command from inside the dev environment:

`sudo yum install cairo pango gdk-pixbuf2 libffi-devel libxslt-devel libxml2-devel python-cairosvg`

The GDSTransportWebsite fonts should also be installed (although you can generate the PDFs without them - they just wont look as nice). Copy GDSTransportWebsite.ttf and GDSTransportWebsite-Bold.ttf to /usr/share/fonts/GDSTransportWebsite/
