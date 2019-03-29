from flask import (
        Blueprint, Flask, request, session, g, redirect, url_for, abort,  render_template, flash
        )

from flask_login import login_required, current_user

from pfedu.forms import StatMechForm
from pfedu.models import db, Molecule, StatMech
import json

bp = Blueprint('routes', __name__)

# List partition functions
@bp.route('/')
@login_required
def index():
    mols = Molecule.query.all()
    return render_template('index.html', mols=mols)

# Show entries
@bp.route('/<int:mol_id>')
@login_required
def show(mol_id):
    mols = Molecule.query.all()
    mol = Molecule.query.filter_by(id=mol_id).first()
    if mol:
        sts = None
        sts = StatMech.query.filter_by(mol_id=mol_id).order_by(StatMech.temp).all()
        return render_template('show.html', sts=sts, mol=mol, mols=mols)

    else:
        flash('Molecule not found!')
        return redirect(url_for('index'))

def process(mol_id, form, st=None):
    try:
        temp = float(current_user.username)
    except ValueError:
        if current_user.admin:
            temp = float(form.temp.data)

    if st:
        st.temp = temp
        st.q_trans = float(form.q_trans.data)
        st.q_rot = float(form.q_rot.data)
        #st.q_vib = float(form.q_vib.data)
        #st.q_elec = float(form.q_elec.data)
        st.user_id = current_user.id

    else:
        try:
            q_trans = float(form.q_trans.data)
            q_rot = float(form.q_rot.data)
            #q_vib = float(form.q_vib.data)
            #q_elec = float(form.q_elec.data)
            user_id = current_user.id
        except ValueError:
            flash('Data has not the right type')
            return False

        #st = StatMech(mol_id=mol_id, temp=temp, q_trans=q_trans,
        #        q_rot=q_rot, q_vib=q_vib, q_elec=q_elec)
        st = StatMech(mol_id=mol_id, temp=temp, q_trans=q_trans,
                q_rot=q_rot)
        #try:
        db.session.add(st)
        #except:
        #    flash('There was an error adding your data')
        #    return False

    db.session.commit()
    return True


@bp.route('/add/<int:mol_id>', methods=('GET', 'POST'))
@login_required
def add(mol_id):
    mols = Molecule.query.all()
    mol = Molecule.query.filter_by(id=mol_id).first()

    form = StatMechForm()
    # Check for submission
    if form.validate_on_submit():

        if process(mol_id, form):
            flash('Your entry has been added!')
            return redirect(url_for('routes.show', mol_id=mol_id))

    return render_template('add.html', mol=mol, mols=mols, form=form)

@bp.route('/edit/<int:mol_id>/<int:st_id>', methods=('GET', 'POST'))
@login_required
def edit(mol_id, st_id):
    mols = Molecule.query.all()
    mol = Molecule.query.filter_by(id=mol_id).first()
    st = StatMech.query.get(st_id)
    if not st:
        flash("Can't find entry")
        return redirect(url_for('routes.show', mol_id=mol_id))

    form = StatMechForm(obj=st)
    # Check for submission
    if form.validate_on_submit():
        if process(mol_id, form, st):
            flash('Your entry has been edited!')
            return redirect(url_for('routes.show', mol_id=mol_id))

    return render_template('edit.html', mol=mol, mols=mols, form=form,
            st_id=st_id)

@bp.route('/delete/<int:mol_id>/<int:st_id>')
@login_required
def delete(mol_id, st_id):
    st = StatMech.query.get(st_id)
    if not current_user.admin:
        if int(st.temp) == int(current_user.username):
            flash('Entry deleted')
            db.session.delete(st)
            db.session.commit()
    else:
        flash('Entry deleted')
        db.session.delete(st)
        db.session.commit()

    return redirect(url_for('routes.show', mol_id=mol_id))

## Plot partition functions
## [TODO] separate tables for each molecules is only temporary. All
## molecules should belong to the same table.
@bp.route('/plot/<int:mol_id>')
@login_required
def plot(mol_id):
    mols = Molecule.query.all()
    mol = Molecule.query.filter_by(id=mol_id).first()

    data_trans = {"temp": [], "q": []}
    data_rot = {"temp": [], "q": []}
    #data_vib = {"temp": [], "q": []}
    #data_elec = {"temp": [], "q": []}
    if mol:
        sts = None
        sts = StatMech.query.filter_by(mol_id=mol_id).order_by(StatMech.temp).all()
        for st in sts:
            data_trans["temp"].append(st.temp)
            data_trans["q"].append(st.q_trans)
            data_rot["temp"].append(st.temp)
            data_rot["q"].append(st.q_rot)
            #data_vib["temp"].append(st.temp)
            #data_vib["q"].append(st.q_vib)
            #data_elec["temp"].append(st.temp)
            #data_elec["q"].append(st.q_elec)

        graph = [
                dict(
                    x=data_trans["temp"],
                    y=data_trans["q"],
                    name="q trans",
                    line= dict(
                        color='rgb(164, 194, 244)',
                        )
                    ),
                dict(
                    x=data_rot["temp"],
                    y=data_rot["q"],
                    name="q rot",
                    ),
                #dict(
                #    x=data_vib["temp"],
                #    y=data_vib["q"],
                #    name="q vib",
                #    ),
                #dict(
                #    x=data_elec["temp"],
                #    y=data_elec["q"],
                #    name="q elec",
                #    )
        ]

        data = json.dumps(graph)

        return render_template('plot.html', mol=mol, mols=mols,
                data=data)

    else:
        flash('Molecule not found!')
        return redirect(url_for('index'))
