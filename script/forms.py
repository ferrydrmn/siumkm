from email.policy import default
from flask_wtf import FlaskForm
from sqlalchemy import null
# from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField, FloatField, IntegerField
from wtforms.fields.html5 import DateField # TimeField
from wtforms.validators import DataRequired, Length, Email, NumberRange #ValidationError
from wtforms.widgets import TextArea, HiddenInput
from script.models import Business_Category, District, Province, Owner

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

# class UmkmForm(FlaskForm):
#     # Mengambil data desa untuk mengisi value dan name ada SELECT INPUT
#     villages_data = Village.query.all()
#     villages_list = []
#     for village in villages_data:
#         village_tupple = (village.id, village.name)
#         villages_list.append(village_tupple)

#     phone_number = StringField('Nomor HP Pemilik', validators=[DataRequired(), Length(min=8, max=15)])
#     name = StringField('Nama UMKM', validators=[DataRequired(), Length(min=2, max=40)])
#     open = TimeField('Waktu Buka', validators=[DataRequired()], format='%H:%M')
#     close = TimeField('Waktu Buka', validators=[DataRequired()], format='%H:%M')
#     shipping_free = BooleanField('Gratis Ongkir')
#     shipping_price = FloatField('Ongkir', validators=[DataRequired()])
#     location_link = StringField('Link Alamat Google Map', validators=[DataRequired(), Length(min=2, max=50)])
#     location_desc = StringField('Deskripsi Alamat', validators=[DataRequired(), Length(min=2, max=50)])
#     description = TextAreaField('Deskripsi UMKM', validators=[DataRequired(), Length(min=1, max=1000)])
#     id_village = SelectField('Desa', choices=villages_list, validators=[DataRequired()])
#     picture = FileField('Foto UMKM', validators=[FileAllowed(['jpg', 'png'])])
#     submit = SubmitField('Submit')

class OwnerForm(FlaskForm):

    # Mengambil data provinsi untuk mengisi value dan name pada SELECT INPUT
    def province_choices():
        provinces_data = Province.query.all()
        provinces_list = [(0,'- Pilih Provinsi -')]
        for province in provinces_data:
            province_tupple = (province.id, province.name)
            provinces_list.append(province_tupple)
        return provinces_list

    id_owner = IntegerField(widget=HiddenInput(), default=0)
    nik = StringField('NIK*', validators=[DataRequired(), Length(max=255)])
    name = StringField('Nama Lengkap*', validators=[DataRequired(), Length(max=255)])
    province = SelectField('Provinsi*', choices=province_choices(), validators=[DataRequired()], coerce=int)
    district = SelectField('Kota/Kabupaten*',  validators=[DataRequired()], validate_choice=False, coerce=int)
    sub_district = SelectField('Kecamatan*', validators=[DataRequired()], validate_choice=False, coerce=int)
    ward = SelectField('Desa*', validators=[DataRequired()], validate_choice=False, coerce=int)
    address = StringField('Alamat Domisili KTP*', validators=[DataRequired()], widget=TextArea())
    postal_code = StringField('Kode Pos*', validators=[DataRequired(), Length(max=255)])
    note = StringField('Catatan Keanggotaan', validators=[Length(max=1020)], widget=TextArea())
    npwp = StringField('NPWP', validators=[Length(max=255)])
    submit = SubmitField('Submit')

class UmkmForm(FlaskForm):
    # Mengambil data provinsi untuk mengisi value dan name pada SELECT INPUT
    def province_choices():
        provinces_data = Province.query.all()
        provinces_list = [(0,'- Pilih Provinsi -')]
        for province in provinces_data:
            province_tupple = (province.id, province.name)
            provinces_list.append(province_tupple)
        return provinces_list
    
    # Mengambil data kategori bisnis untuk mengisi value dan name pada SELECT INPUT
    def business_cat_choices():
        business_cats_data = Business_Category.query.all()
        business_cats_list = [(0, '- Pilih Kategori Bisnis -')]
        for business_cat in business_cats_data:
            business_cats_tupple = (business_cat.id, business_cat.business_category)
            business_cats_list.append(business_cats_tupple)
        return business_cats_list

    id_umkm = IntegerField('ID UMKM', widget=HiddenInput(), default=0)
    nik = StringField('NIK Pemilik UMKM*', validators=[DataRequired(), Length(max=255)])
    name = StringField('Nama UMKM*', validators=[DataRequired(), Length(max=255)])
    business_category = SelectField('Kategori Bisnis*', choices=business_cat_choices(), validators=[DataRequired()], coerce=int)
    business_type = StringField('Jenis Bisnis', validators=[Length(max=255)])
    province = SelectField('Provinsi*', choices=province_choices(), validators=[DataRequired()], coerce=int)
    district = SelectField('Kota/Kabupaten*',  validators=[DataRequired()], validate_choice=False, coerce=int)
    sub_district = SelectField('Kecamatan*', validators=[DataRequired()], validate_choice=False, coerce=int)
    ward = SelectField('Desa*', validators=[DataRequired()], validate_choice=False, coerce=int)
    address = StringField('Alamat UMKM*', validators=[DataRequired()], widget=TextArea())
    start_date = DateField('Tanggal Mulai Usaha*', validators=[DataRequired()])
    modal = FloatField('Modal (Rupiah)*', validators=[DataRequired(), NumberRange(min=1)])
    workers = IntegerField('Jumlah Pekerja*', validators=[DataRequired(), NumberRange(min=1)], default=1)
    email = StringField('Email*', validators=[Length(max=255)])
    facebook = StringField('Facebook', validators=[Length(max=255)])
    instagram = StringField('Instagram', validators=[Length(max=255)])
    twitter = StringField('Twitter', validators=[Length(max=255)])
    marketplace = StringField('Marketplace', validators=[Length(max=255)])
    website = StringField('Website', validators=[Length(max=255)])
    legal_entity = StringField('Badan Hukum', validators=[Length(max=1020)], widget=TextArea())   
    problem = StringField('Permasalahan', validators=[Length(max=1020)], widget=TextArea())
    submit = SubmitField('Submit')


# class VillageForm(FlaskForm):
#     name = StringField('Nama Desa', validators=[DataRequired(), Length(max=25)])
#     picture = FileField('Foto Desa', validators=[FileAllowed(['jpg', 'png'])])
#     submit = SubmitField('Submit')

# class MenuForm(FlaskForm):
#     type_data = Type.query.all()
#     type_list = []
    
#     for type in type_data:
#         type_tupple = (type.id, type.type)
#         type_list.append(type_tupple)
    
#     name = StringField('Nama Menu', validators=[DataRequired()])
#     price = FloatField('Harga (Rp.)', validators=[DataRequired()])
#     id_type = SelectField('Tipe', choices=type_list, validators=[DataRequired()])
#     submit = SubmitField('Submit')
