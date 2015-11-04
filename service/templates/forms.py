from flask_wtf import Form                                           # type: ignore
from wtforms.fields import IntegerField, StringField, PasswordField  # type: ignore
from wtforms.validators import Required, Length                      # type: ignore


class SigninForm(Form):  # type: ignore
    username = StringField('username', [Required(message='Username is required'),
                                        Length(min=4, max=70, message='Username is incorrect')])
    password = PasswordField('password', [Required(message='Password is required')])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)


class TitleSearchForm(Form):  # type: ignore
    search_term = StringField('search_term',
                              [Required(message='Search term is required'),
                               Length(min=3, max=70, message='Search term is too short/long')])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)


class AccountForm(Form):  # type: ignore
    name = StringField('Your name', [Required(message='Name is required'), Length(min=4, max=70, message='Name is too short/long')])
    business_name = StringField('Business name (optional)')
    telephone_number = StringField('Telephone number (optional)')
    address_line_1 = StringField('Building name/number and street', validators=[Required(message='First line of address is required'), Length(min=4, max=70, message='First line of address is too short/long')])
    address_line_2 = StringField('')
    town = StringField('Town or city')
    county = StringField('County (optional)')
    postcode = StringField('Postcode')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)


class PaymentForm(Form):  # type: ignore
    full_name = StringField('Full name', [Required(message='Full name is required'), Length(min=4, max=70, message='Full name is too short/long')])
    card_number = IntegerField('Card number', [Required(message='Card number is required')])
    card_security_code = IntegerField('Card security code', [Required(message='Card security code')])
    expiry_month = IntegerField(label='Month', validators=[Required(message='Expiry date month is required')])
    expiry_year = IntegerField(label='Year', validators=[Required(message='Expiry date year is required')])
    building_and_street_1 = StringField('Building and street', [Required(message='First line of address is required'), Length(min=4, max=70, message='First line of address is too short/long')])
    building_and_street_2 = StringField('')
    town = StringField('Town', [Required(message='Town or city is required'), Length(min=4, max=70, message='Town or city is too short/long')])
    county = StringField('County (optional)')
    postcode = StringField('Postcode', [Required(message='Postcode is required'), Length(min=5, max=8, message='Postcode is too short/long')])
    email = StringField('Email', [Required(message='Email is required'), Length(min=6, max=70, message='Email is too short/long')])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

class AccountCreationForm(Form): # type: ignore
    email = StringField('')
    password = StringField('')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
