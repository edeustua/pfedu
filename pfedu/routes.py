from flask import (
        Blueprint, Flask, request, session, g,
        redirect, url_for, abort,  render_template, flash,
        )

from flask_login import login_required, current_user

from pfedu.forms import StatMechForm, ReactionForm
from pfedu.models import db, Molecule, StatMech, Reaction, ReactionB
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

# [TODO] sort routes properly
# Reaction routes

# Show reaction thermodynamic parameters
@bp.route('/reaction/<reaction>')
@login_required
def reaction(reaction):
    if reaction == 'a':
        reacs = Reaction.query.order_by(Reaction.temp).all()
    elif reaction == 'b':
        reacs = ReactionB.query.order_by(ReactionB.temp).all()
    mols = Molecule.query.all()
    return render_template('reaction.html', reaction=reaction, reacs=reacs, mols=mols)


@bp.route('/add_reaction/<reaction>', methods=('GET', 'POST'))
@login_required
def add_reaction(reaction):
    mols = Molecule.query.all()

    # If temperature record already exists, reroute to edit
    # Make sure that this is not an admin account first
    if not current_user.admin:
        temp = float(current_user.username)
        if reaction == 'a':
            reac = Reaction.query.filter_by(temp=temp).first()
        elif reaction == 'b':
            reac = ReactionB.query.filter_by(temp=temp).first()

        if reac:
            flash('A record with your temperature exists. Editing instead.')
            return redirect(url_for('routes.edit_reaction',
                reaction=reaction,
                reac_id=reac.id))

    form = ReactionForm()
    # Check for submission
    if form.validate_on_submit():

        # Load form data into typed variables
        if not current_user.admin:
            temp = float(current_user.username)
        else:
            temp = float(form.temp.data)

        delta_g = float(form.delta_g.data)
        delta_h = float(form.delta_h.data)
        delta_s = float(form.delta_s.data)
        k_p = float(form.k_p.data)

        if reaction == 'a':
            reac = Reaction(temp=temp, delta_g=delta_g, delta_h=delta_h,
                    delta_s=delta_s, k_p=k_p)
        elif reaction == 'b':
            reac = ReactionB(temp=temp, delta_g=delta_g, delta_h=delta_h,
                    delta_s=delta_s, k_p=k_p)

        db.session.add(reac)
        db.session.commit()
        flash('Your entry has been added!')
        return redirect(url_for('routes.reaction', reaction=reaction))


    #    if process(mol_id, form):
    #        flash('Your entry has been added!')
    #        return redirect(url_for('routes.show', mol_id=mol_id))

    return render_template('add_reaction.html', mols=mols, form=form,
            reaction=reaction)

@bp.route('/edit_reaction/<reaction>/<int:reac_id>', methods=('GET', 'POST'))
@login_required
def edit_reaction(reaction, reac_id):
    mols = Molecule.query.all()

    # Query reaction data
    if reaction == 'a':
        reac = Reaction.query.get(reac_id)
    elif reaction == 'b':
        reac = ReactionB.query.get(reac_id)
    if not reac:
        flash("Can't find entry")
        return redirect(url_for('routes.reaction', reaction=reaction))


    # Load data into form
    form = ReactionForm(obj=reac)

    # Check for submission
    if form.validate_on_submit():

        # Load form data into typed variables
        if not current_user.admin:
            reac.temp = float(current_user.username)
        else:
            reac.temp = float(form.temp.data)

        reac.delta_g = float(form.delta_g.data)
        reac.delta_h = float(form.delta_h.data)
        reac.delta_s = float(form.delta_s.data)
        reac.k_p = float(form.k_p.data)

        db.session.commit()
        flash('Your entry has been edited!')
        return redirect(url_for('routes.reaction', reaction=reaction))

    return render_template('edit_reaction.html', reaction=reaction, mols=mols, form=form,
            reac_id=reac_id)

@bp.route('/delete_reaction/<reaction>/<int:reac_id>')
@login_required
def delete_reaction(reaction, reac_id):
    if reaction == 'a':
        reac = Reaction.query.get(reac_id)
    elif reaction == 'b':
        reac = ReactionB.query.get(reac_id)

    # add temperature failsafe, so that people can't delete each
    # others stuff
    if not current_user.admin:
        if int(reac.temp) == int(current_user.username):
            flash('Entry deleted')
            db.session.delete(reac)
            db.session.commit()
    else:
        flash('Entry deleted')
        db.session.delete(reac)
        db.session.commit()

    return redirect(url_for('routes.reaction', reaction=reaction))

@bp.route('/plot_reaction/<reaction>')
@login_required
def plot_reaction(reaction):
    mols = Molecule.query.all()

    data_delta_g = {"temp": [], "d": []}
    data_delta_h = {"temp": [], "d": []}
    data_delta_s = {"temp": [], "d": []}
    data_k_p = {"temp": [], "d": []}

    if reaction == 'a':
        reacs = Reaction.query.order_by(Reaction.temp).all()
    elif reaction == 'b':
        reacs = ReactionB.query.order_by(ReactionB.temp).all()
    for reac in reacs:
        data_delta_g["temp"].append(reac.temp)
        data_delta_g["d"].append(reac.delta_g)
        data_delta_h["temp"].append(reac.temp)
        data_delta_h["d"].append(reac.delta_h)
        data_delta_s["temp"].append(reac.temp)
        data_delta_s["d"].append(reac.delta_s)
        data_k_p["temp"].append(reac.temp)
        data_k_p["d"].append(reac.k_p)

    graph = [
            dict(
                x=data_delta_g["temp"],
                y=data_delta_g["d"],
                name=r"$\Delta G^0$",
                line= dict(
                    color='rgb(164, 194, 244)',
                    )
                ),
            dict(
                x=data_delta_h["temp"],
                y=data_delta_h["d"],
                name=r"$\Delta H^0$",
                ),
            dict(
                x=data_delta_s["temp"],
                y=data_delta_s["d"],
                name=r"$\Delta S$",
                ),
            dict(
                x=data_k_p["temp"],
                y=data_k_p["d"],
                name=r"$K_p$",
                )
    ]

    data = json.dumps(graph)

    return render_template('plot_reaction.html', reaction=reaction, mols=mols,
            data=data)




# Process molecule form
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
        st.q_vib = float(form.q_vib.data)
        st.q_elec = float(form.q_elec.data)
        #st.q_vib = 0.0
        #st.q_elec = 0.0
        st.user_id = current_user.id

    else:
        try:
            q_trans = float(form.q_trans.data)
            q_rot = float(form.q_rot.data)
            q_vib = float(form.q_vib.data)
            q_elec = float(form.q_elec.data)
            #q_vib = 0.0
            #q_elec = 0.0
            user_id = current_user.id
        except ValueError:
            flash('Data has not the right type')
            return False

        st = StatMech(mol_id=mol_id, temp=temp, q_trans=q_trans,
                q_rot=q_rot, q_vib=q_vib, q_elec=q_elec)
        #st = StatMech(mol_id=mol_id, temp=temp, q_trans=q_trans,
        #        q_rot=q_rot)
        #try:
        db.session.add(st)
        #except:
        #    flash('There was an error adding your data')
        #    return False

    db.session.commit()
    return True


# Add a new entry. If one already exists (with the same temperature)
# go to edit instead.
@bp.route('/add/<int:mol_id>', methods=('GET', 'POST'))
@login_required
def add(mol_id):
    mols = Molecule.query.all()
    mol = Molecule.query.filter_by(id=mol_id).first()

    # If temperature record already exists, reroute to edit
    # Make sure that this is not an admin account first
    if not current_user.admin:
        temp = float(current_user.username)
        st = StatMech.query.filter_by(temp=temp).filter_by(mol_id=mol_id).first()

        if st:
            flash('A record with your temperature exists. Editing instead.')
            return redirect(url_for('routes.edit', mol_id=mol_id,
                st_id=st.id))

    form = StatMechForm()
    #del form.q_vib
    #del form.q_elec
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
    #del form.q_vib
    #del form.q_elec
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
    data_vib = {"temp": [], "q": []}
    data_elec = {"temp": [], "q": []}
    if mol:
        sts = None
        sts = StatMech.query.filter_by(mol_id=mol_id).order_by(StatMech.temp).all()
        for st in sts:
            data_trans["temp"].append(st.temp)
            data_trans["q"].append(st.q_trans)
            data_rot["temp"].append(st.temp)
            data_rot["q"].append(st.q_rot)
            data_vib["temp"].append(st.temp)
            data_vib["q"].append(st.q_vib)
            data_elec["temp"].append(st.temp)
            data_elec["q"].append(st.q_elec)

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
                dict(
                    x=data_vib["temp"],
                    y=data_vib["q"],
                    name="q vib",
                    ),
                dict(
                    x=data_elec["temp"],
                    y=data_elec["q"],
                    name="q elec",
                    )
        ]

        data = json.dumps(graph)

        return render_template('plot.html', mol=mol, mols=mols,
                data=data)

    else:
        flash('Molecule not found!')
        return redirect(url_for('index'))
