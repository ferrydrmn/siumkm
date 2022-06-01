from script import db, ma, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(id_user):
    return User.query.get(str(id_user))

class User(db.Model, UserMixin): 
    __tablename__ = 'users'

    id = db.Column(db.String(22), primary_key=True)
    email = db.Column(db.String(75), nullable=False, unique=True)
    name = db.Column(db.String(75), nullable=False, unique=True)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable =False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Province(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    district = db.relationship('District', backref='province', lazy=True)

    def __repr__(self):
        return f'{self.id}, {self.name}'

class District(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_province = db.Column(db.Integer, db.ForeignKey('province.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    sub_district = db.relationship('Sub_District', backref='district', lazy=True)

    def __repr__(self):
        return f'{self.id}, {self.name}'

class Sub_District(db.Model):
    __tablename__ = 'sub_district'

    id = db.Column(db.Integer, primary_key=True)
    id_district = db.Column(db.Integer, db.ForeignKey('district.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    ward = db.relationship('Ward', backref='sub_district', lazy=True)

    def __repr__(self):
        return f'{self.id}, {self.name}'

class Ward(db.Model):
    __tablename__ = 'ward'

    id = db.Column(db.Integer, primary_key=True)
    id_sub_district = db.Column(db.Integer, db.ForeignKey('sub_district.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    owner = db.relationship('Owner', backref='ward', lazy=True)
    umkm = db.relationship('Umkm', backref='ward', lazy=True)
    
    def __repr__(self):
        return f'{self.id}, {self.name}'

class Owner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_ward = db.Column(db.Integer, db.ForeignKey('ward.id'), nullable=False)
    nik = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    postal_code = db.Column(db.String(255), nullable=False)
    note = db.Column(db.String(1020))
    npwp = db.Column(db.String(255))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    umkm = db.relationship('Umkm', backref='owner', lazy=True)

    def __repr__(self):
        return f'{self.id}, {self.name}, {self.nik}'

class Umkm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String, nullable=False, unique=True)
    id_owner = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)
    id_ward = db.Column(db.Integer, db.ForeignKey('ward.id'), nullable=False)
    id_business_category = db.Column(db.Integer,db.ForeignKey('business_category.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(510), nullable=False)
    business_type = db.Column(db.String(255))
    start_date = db.Column(db.DateTime, nullable=False)
    workers = db.Column(db.Integer)
    modal = db.Column(db.Float)
    email = db.Column(db.String(255))
    facebook = db.Column(db.String(255))
    instagram = db.Column(db.String(255))
    twitter = db.Column(db.String(255))
    marketplace = db.Column(db.String(255))
    website = db.Column(db.String(255))
    legal_entity = db.Column(db.String(1022))
    problem = db.Column(db.String(4088))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    brand = db.relationship('Brand', backref='umkm', lazy=True)

    def __repr__(self):
        return f'{self.id}, {self.name}'

class Business_Category(db.Model):
    __tablename__ = 'business_category'

    id = db.Column(db.Integer, primary_key=True)
    business_category = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    umkm = db.relationship('Umkm', backref='business_category', lazy=True)

    def __repr__(self):
        return f'{self.id}, {self.business_category}'

class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_umkm = db.Column(db.Integer, db.ForeignKey('umkm.id'), nullable=False)
    brand = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    product = db.relationship('Product', backref='brand', lazy=True)

    def __repr__(self):
        return f'{self.id}, {self.business_category}'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_brand = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False)
    id_type = db.Column(db.Integer, db.ForeignKey('product_type.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    price_reseller = db.Column(db.Float, nullable=False)
    variance = db.Column(db.String(255))
    size = db.Column(db.String(255))
    description = db.Column(db.String(1022))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'{self.id}, {self.name}, {self.price}, {self.id_type}'

class Product_Type(db.Model):
    __tablename__ = 'product_type'

    id = db.Column(db.Integer, primary_key=True)
    product_type = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    product = db.relationship('Product', backref='product_type', lazy=True)

    def __repr__(self):
        return f'{self.id}, {self.product_type}'

class DistrictSchema(ma.SQLAlchemyAutoSchema):
      class Meta:
            fields = ('id', 'name')

class Sub_DistrictSchema(ma.SQLAlchemyAutoSchema):
      class Meta:
            fields = ('id', 'name')

class WardSchema(ma.SQLAlchemyAutoSchema):
      class Meta:
            fields = ('id', 'name')