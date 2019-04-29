from flask import (
        Blueprint, Flask, request, session, g,
        redirect, url_for, abort,  render_template, flash,
        make_response, send_file
        )

from flask_login import login_required, current_user

from pfedu.forms import UserForm, MoleculeForm, PasswdForm
from pfedu.models import db, Molecule, StatMech, User

from datetime import datetime
import zipfile
import io

from sqlalchemy.exc import IntegrityError

import pandas as pd

bp = Blueprint('admin', __name__, url_prefix='/admin')



# List partition functions
@bp.route('/')
@login_required
def index():
    if not current_user.admin:
        return redirect(url_for('index'))

    mols = Molecule.query.all()

    return render_template('admin/index.html', mols=mols)

@bp.route('/passwd', methods=['GET', 'POST'])
@login_required
def passwd():
    if not current_user.admin:
        return redirect(url_for('index'))

    form = PasswdForm()
    if form.validate_on_submit():
        current_user.set_password(form.passwd.data)
        db.session.commit()
        flash('Password changed')
        return redirect(url_for('admin.index'))

    return render_template('admin/passwd.html', form=form)


@bp.route('/get_data/<int:mol_id>')
@login_required
def get_data(mol_id):
    if not current_user.admin:
        return redirect(url_for('index'))

    mol = Molecule.query.get(mol_id)

    # Generate CSV
    sts = StatMech.query.filter_by(mol_id=mol_id).all()
    data = []
    for st in sts:
        data.append([st.temp, st.q_trans, st.q_rot, st.q_vib,
            st.q_elec, st.delta_g, st.delta_h, st.delta_s])
        #data.append([st.temp, st.q_trans, st.q_rot])
    #df = pd.DataFrame(data=data,columns=['temperature', 'q_trans',
    #'q_rot', 'q_vib', 'q_elec'])
    df = pd.DataFrame(data=data,columns=['temperature', 'q_trans',
    'q_rot', 'q_vib', 'q_elec', 'delta_g', 'delta_h', 'delta_s'])
    df = df.set_index('temperature')
    df = df.sort_index()

    res = make_response(df.to_csv())
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    res.headers["Content-Disposition"] = \
            "attachment; filename=cem484_{}_{}.csv".format(mol.name, timestamp)
    res.headers["Content-Type"] = "text/csv"
    return res

@bp.route('/get_data_all')
@login_required
def get_data_all():
    if not current_user.admin:
        return redirect(url_for('index'))

    mols = Molecule.query.all()

    # Generate CSV
    zip_file = io.BytesIO()
    with zipfile.ZipFile(zip_file, mode='w') as z:
        for mol in mols:
            sts = StatMech.query.filter_by(mol_id=mol.id).all()
            data = []

            for st in sts:
                data.append([st.temp, st.q_trans, st.q_rot, st.q_vib,
                    st.q_elec, st.delta_g, st.delta_h, st.delta_s])

            df = pd.DataFrame(data=data,columns=['temperature', 'q_trans',
            'q_rot', 'q_vib', 'q_elec', 'delta_g', 'delta_h', 'delta_s'])
            df = df.set_index('temperature')
            df = df.sort_index()
            z.writestr(mol.name+".csv", df.to_csv())

    zip_file.seek(0)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    return send_file(zip_file,
            mimetype='application/zip',
            as_attachment=True,
            attachment_filename='cem484_{}.zip'.format(timestamp))



# Users
@bp.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.admin:
        return redirect(url_for('index'))

    form = UserForm()
    if form.validate_on_submit():
        if form.username.data:
            # Temporary username
            i = str(form.username.data)
            digs = [int(x) for x in str(i)]
            user = User(username=str(i),admin=False)
            user.set_password(str(sum(digs)))
            db.session.add(user)
        elif form.start_temp.data and form.end_temp.data:
            start = int(form.start_temp.data)
            end = int(form.end_temp.data)
            step = int(form.step_temp.data)
            for i in range(start, end+1, step):
                digs = [int(x) for x in str(i)]
                user = User(username=str(i),admin=False)
                user.set_password(str(sum(digs)))
                db.session.add(user)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Molecule already added')

        flash('Molecule added')
        return redirect(url_for('admin.list_user'))

    return render_template('admin/user/add.html', form=form,
    title='Add')

@bp.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if not current_user.admin:
        return redirect(url_for('index'))

    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('admin.list_user'))

@bp.route('/delete_user_all')
@login_required
def delete_user_all():
    if not current_user.admin:
        return redirect(url_for('index'))

    for user in User.query.filter_by(admin=False).all():
        db.session.delete(user)
    db.session.commit()

    return redirect(url_for('admin.list_user'))

@bp.route('/list_user')
@login_required
def list_user():
    if not current_user.admin:
        return redirect(url_for('index'))

    users = User.query.filter_by(admin=False).all()

    return render_template('admin/user/list.html', users=users)


# Molecules
@bp.route('/add_mol', methods=['GET', 'POST'])
@login_required
def add_mol():
    if not current_user.admin:
        return redirect(url_for('index'))

    form = MoleculeForm()
    if form.validate_on_submit():
        if not form.html.data:
            form.html.data = form.name.data
        mol = Molecule(name=form.name.data,html=form.html.data)
        db.session.add(mol)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Molecule already added')

        flash('Molecule added')
        return redirect(url_for('admin.list_mol'))

    return render_template('admin/mol/add.html', form=form,
    title='Add')

@bp.route('/edit_mol/<int:mol_id>', methods=['GET', 'POST'])
@login_required
def edit_mol(mol_id):
    if not current_user.admin:
        return redirect(url_for('index'))

    mol = Molecule.query.get(mol_id)
    if not mol:
        flash("Can't find molecule")
        return redirect(url_for('admin.list_mol'))

    form = MoleculeForm(obj=mol)
    if form.validate_on_submit():
        if not form.html.data:
            mol.html = form.name.data
        else:
            mol.html = form.html.data
        mol.name = form.name.data
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Molecule could not be updated')

        flash('Molecule edited')
        return redirect(url_for('admin.list_mol'))

    return render_template('admin/mol/add.html', form=form,
    title='Edit', mol_id=mol.id)

@bp.route('/delete_mol/<int:mol_id>')
@login_required
def delete_mol(mol_id):
    if not current_user.admin:
        return redirect(url_for('index'))

    mol = Molecule.query.get(mol_id)
    db.session.delete(mol)
    db.session.commit()

    return redirect(url_for('admin.list_mol'))

@bp.route('/list_mol')
@login_required
def list_mol():
    if not current_user.admin:
        return redirect(url_for('index'))


    mols = Molecule.query.all()

    return render_template('admin/mol/list.html', mols=mols)

