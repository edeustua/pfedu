from datetime import datetime
import click
from flask.cli import with_appcontext
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import generate_password_hash, \
    check_password_hash

db = SQLAlchemy()

# User
# Users and passwords
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    admin = db.Column(db.Boolean)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}, {}>'.format(self.username, self.email)

# Molecule
# This holds the molecules for the semester
class Molecule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True)
    html = db.Column(db.String(100))

    def __repr__(self):
        return '<Molecule {}, {}>'.format(self.id, self.name)

# StatMech
# All thermo and statistical mechanical data
class StatMech(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True,
            default=datetime.utcnow)
    temp = db.Column(db.Float)
    q_trans = db.Column(db.Float)
    q_rot = db.Column(db.Float)
    q_vib = db.Column(db.Float)
    q_elec = db.Column(db.Float)
    q_tot = db.Column(db.Float)
    delta_g = db.Column(db.Float)
    delta_h = db.Column(db.Float)
    delta_s = db.Column(db.Float)
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mol_id = db.Column(db.Integer, db.ForeignKey('molecule.id'))

    def __repr__(self):
        return '<StatMech {}, {}>'.format(self.id, self.timestamp)

class Reaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True,
            default=datetime.utcnow)
    temp = db.Column(db.Float)
    delta_g = db.Column(db.Float)
    delta_h = db.Column(db.Float)
    delta_s = db.Column(db.Float)
    k_p = db.Column(db.Float)

    def __repr__(self):
        return '<Reaction {}, {}>'.format(self.id, self.temp)

class ReactionB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True,
            default=datetime.utcnow)
    temp = db.Column(db.Float)
    delta_g = db.Column(db.Float)
    delta_h = db.Column(db.Float)
    delta_s = db.Column(db.Float)
    k_p = db.Column(db.Float)

    def __repr__(self):
        return '<Reaction {}, {}>'.format(self.id, self.temp)


# Database management
def init_db():
    db.create_all()
    from flask import current_app

    for user, email in current_app.config['ADMINS']:
        admin = User(username=user, email=email,
                admin=True)
        admin.set_password(user)
        db.session.add(admin)

    try:
        db.session.commit()
        click.echo('Initialized the database.')
    except:
        click.echo("Could not initialize tables")

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Create new tables."""
    init_db()

@click.command('clean-db')
@with_appcontext
def clean_db_command():
    """Clear the existing data."""
    db.drop_all()
    db.session.commit()
    click.echo('Database cleaned.')

@click.command('reinit-db')
@with_appcontext
def reinit_db_command():
    """Clear the existing data and create new tables."""
    db.drop_all()
    click.echo('Database cleaned.')
    init_db()
