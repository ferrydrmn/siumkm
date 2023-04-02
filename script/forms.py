from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField, FloatField, IntegerField
from wtforms.fields.html5 import DateField # TimeField
from wtforms.validators import DataRequired, Length, Email, NumberRange 
from wtforms.widgets import TextArea, HiddenInput

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class PasswordForm(FlaskForm):
    old_password = PasswordField('Password Lama*', validators=[DataRequired()])
    new_password = PasswordField('Password Baru*', validators=[DataRequired()])
    confirm_password = PasswordField('Konfirmasi Password Baru*', validators=[DataRequired()])
    submit = SubmitField('Submit')

class OwnerForm(FlaskForm):
    id_owner = IntegerField(widget=HiddenInput(), default=0)
    nik = StringField('NIK*', validators=[DataRequired(), Length(max=255)])
    name = StringField('Nama Lengkap*', validators=[DataRequired(), Length(max=255)])
    province = SelectField('Provinsi*',  validators=[DataRequired()], validate_choice=False, coerce=int) 
    district = SelectField('Kota/Kabupaten*',  validators=[DataRequired()], validate_choice=False, coerce=int)
    sub_district = SelectField('Kecamatan*', validators=[DataRequired()], validate_choice=False, coerce=int)
    ward = SelectField('Desa*', validators=[DataRequired()], validate_choice=False, coerce=int)
    address = StringField('Alamat Domisili KTP*', validators=[DataRequired()], widget=TextArea())
    postal_code = StringField('Kode Pos*', validators=[DataRequired(), Length(max=255)])
    note = StringField('Catatan Keanggotaan', validators=[Length(max=1020)], widget=TextArea())
    npwp = StringField('NPWP', validators=[Length(max=255)])
    submit = SubmitField('Submit')

class UmkmForm(FlaskForm):
    id_umkm = IntegerField('ID UMKM', widget=HiddenInput(), default=0)
    nik = StringField('NIK Pemilik UMKM*', validators=[DataRequired(), Length(max=255)])
    name = StringField('Nama UMKM*', validators=[DataRequired(), Length(max=255)])
    business_category = SelectField('Kategori Bisnis*', validate_choice=False, validators=[DataRequired()], coerce=int) 
    business_type = StringField('Jenis Bisnis', validators=[Length(max=255)])
    province = SelectField('Provinsi*', validators=[DataRequired()], validate_choice=False, coerce=int) 
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

class BrandForm(FlaskForm):
    id_brand = StringField('ID Brand*', widget=HiddenInput(), validators=[DataRequired(), Length(max=255)], default=0)
    umkm = StringField('Nama UMKM*', validators=[DataRequired(), Length(max=255)])
    brand = StringField('Nama Brand*', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Submit')

class ProductForm(FlaskForm):
    id_product = IntegerField('ID Produk*', widget=HiddenInput(), default=0)
    brand = StringField('Nama Brand*', validators=[DataRequired(), Length(max=22)])
    name = StringField('Nama Produk*', validators=[DataRequired(), Length(max=255)])
    product_type = SelectField('Tipe Produk*', validators=[DataRequired()], validate_choice=False, coerce=int)
    product_category = SelectField('Kategori Produk*', validators=[DataRequired()], validate_choice=False, coerce=int) 
    price = FloatField('Harga (Rp)*', validators=[DataRequired(), NumberRange(min=0)], default=0)
    price_reseller = FloatField('Harga Reseller (Rp)', validators=[NumberRange(min=0)], default=0)
    variance = StringField('Variansi', widget=TextArea(), validators=[Length(max=255)])
    size = StringField('Ukuran', validators=[Length(max=255)])
    description = StringField('Deskripsi', widget=TextArea(), validators=[Length(max=255)])
    submit = SubmitField('Submit')

class ExcelForm(FlaskForm):
    excel = FileField('File XLSX/XLS*', validators=[DataRequired(), FileAllowed(['xlsx', 'xls'])])
    update = BooleanField('Update Data', default=0)
    submit = SubmitField('Submit')

class ProvinceForm(FlaskForm):
    id_province = IntegerField('ID Provinsi*', widget=HiddenInput(), default=0)
    name = StringField('Nama Provinsi*', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Submit')

class DistrictForm(FlaskForm):
    id_district = IntegerField('ID Kota/Kabupaten*', widget=HiddenInput(), default=0)
    id_province = IntegerField('ID Provinsi*', validators=[DataRequired(), NumberRange(min=1)])
    name = StringField('Nama Kota/Kabpuaten*', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Submit')

class SubDistrictForm(FlaskForm):
    id_sub_district = IntegerField('ID Kecamatan*', widget=HiddenInput(), default=0)
    id_district = IntegerField('ID Kota/Kabpuaten*', validators=[DataRequired(), NumberRange(min=1)])
    name = StringField('Nama Kecamatan*', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Submit')

class WardForm(FlaskForm):
    id_ward = IntegerField('ID Desa*', widget=HiddenInput(), default=0)
    id_sub_district = IntegerField('ID Kecamatan*', validators=[DataRequired(), NumberRange(min=1)])
    name = StringField('Nama Desa*', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Submit')

class BusinessCategoryForm(FlaskForm):
    id_business_category = IntegerField('ID Kategori Bisnis*', widget=HiddenInput(), default=0)
    business_category = StringField('Kategori Bisnis*', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Submit')

class ProductTypeForm(FlaskForm):
    id_product_type = IntegerField('ID Tipe Produk*', widget=HiddenInput(), default=0)
    product_type = StringField('Tipe Produk*', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Submit')

class ProductCategoryForm(FlaskForm):
    id_product_category = IntegerField('ID Tipe Produk*', widget=HiddenInput(), default=0)
    product_category= StringField('Kategori Produk*', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Submit')
    
