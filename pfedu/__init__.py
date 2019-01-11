import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'pfedu.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        ADMINS=[('admin','admin@localhost')]
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register db
    from pfedu.models import db, init_db_command, clean_db_command, \
            reinit_db_command
    db.init_app(app)
    app.cli.add_command(init_db_command)
    app.cli.add_command(clean_db_command)
    app.cli.add_command(reinit_db_command)

    # register auth
    from . import auth
    auth.login_mgr.init_app(app)
    app.register_blueprint(auth.bp)

    # register admin
    from . import admin
    app.register_blueprint(admin.bp)


    # register blog required
    from . import routes, models
    app.register_blueprint(routes.bp)
    app.add_url_rule('/', endpoint='index')

    return app
