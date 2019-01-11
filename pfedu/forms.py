from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, ValidationError, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    passwd = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign in')

class PasswdForm(FlaskForm):
    passwd = PasswordField('Password',
            validators=[DataRequired(),EqualTo('confirm',
            message='Passwords must match')])
    confirm = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Change password')

class MoleculeForm(FlaskForm):
    name = StringField('Molecule name', validators=[DataRequired()])
    html = StringField('HTML')
    submit = SubmitField('Submit data')

class UserForm(FlaskForm):
    username = StringField('Username (temperature)')
    start_temp = StringField('Start temperature')
    end_temp = StringField('End temperature')
    step_temp = StringField('Step size')
    submit = SubmitField('Submit data')

class StatMechForm(FlaskForm):
    temp = StringField(r'Temperature')
    #        validators=[DataRequired()])
    q_trans = StringField(r'q<sub>trans</sub>',
            validators=[DataRequired()])
    q_rot = StringField(r'q<sub>rot</sub>',
            validators=[DataRequired()])
    q_vib = StringField(r'q<sub>vib</sub>',
            validators=[DataRequired()])
    q_elec = StringField(r'q<sub>elec</sub>',
            validators=[DataRequired()])
    submit = SubmitField('Submit data')

    def validate_temp(self, temp):
        if temp.data:
            try:
                float(temp.data)
            except ValueError:
                raise ValidationError('Temperature needs to be a number')

    def validate_q_trans(self, q_trans):
        try:
            float(q_trans.data)
        except ValueError:
            raise ValidationError(r'\(q_\text{trans}\) needs to be a number')

    def validate_q_rot(self, q_rot):
        try:
            float(q_rot.data)
        except ValueError:
            raise ValidationError(r'\(q_\text{rot}\) needs to be a number')

    def validate_q_vib(self, q_vib):
        try:
            float(q_vib.data)
        except ValueError:
            raise ValidationError(r'\(q_\text{vib}\) needs to be a number')

    def validate_q_elec(self, q_elec):
        try:
            float(q_elec.data)
        except ValueError:
            raise ValidationError(r'\(q_\text{elec}\) needs to be a number')
