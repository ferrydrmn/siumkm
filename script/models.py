from enum import unique
from script import db, ma, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(id_user):
    return User.query.get(str(id_user))

class User(db.Model, UserMixin): 
    __tablename__ = 'user'

    id = db.Column(db.String(22), primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable =False)

    excel = db.relationship('Excel', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Province(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.Date)
    updated_at = db.Column(db.Date)
    district = db.relationship('District', backref='province', lazy=True)

    def __repr__(self):
        return f'{self.id}, {self.name}'

    def to_table(self):
        return {
            'name': self.name,
            'district_count': len(self.district),
            'action': f"""<div class="d-flex justify-content-around">
            <a href='/province/{self.id}' class='btn btn-info'><i class='bi bi-info-square'></i></a> 
            <form method='POST' action='/province/{self.id}/delete' onsubmit="return confirm('Apakah Anda yakin?');">
                <button type='submit' class='btn btn-danger'><i class='bi bi-trash'></i></button>
            </form>
            </div>""",
            'updated_at': self.updated_at.strftime('%d/%m/%Y')
        }

class District(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_province = db.Column(db.Integer, db.ForeignKey('province.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.Date)
    updated_at = db.Column(db.Date)
    sub_district = db.relationship('Sub_District', backref='district', lazy=True)

    def __repr__(self):
        return f'{self.id}, {self.name}'

    def to_table(self):
        return {
            'name': self.name,
            'province': self.province.name,
            'sub_district_count': len(self.sub_district),
            'action': f"""<div class="d-flex justify-content-around">
            <a href='/district/{self.id}' class='btn btn-info'><i class='bi bi-info-square'></i></a> 
            <form method='POST' action='/district/{self.id}/delete' onsubmit="return confirm('Apakah Anda yakin?');">
                <button type='submit' class='btn btn-danger'><i class='bi bi-trash'></i></button>
            </form>
            </div>""",
            'updated_at': self.updated_at.strftime('%d/%m/%Y')
        }

class Sub_District(db.Model):
    __tablename__ = 'sub_district'

    id = db.Column(db.Integer, primary_key=True)
    id_district = db.Column(db.Integer, db.ForeignKey('district.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.Date)
    updated_at = db.Column(db.Date)
    ward = db.relationship('Ward', backref='sub_district', lazy=True)

    def __repr__(self):
        return f'{self.id}, {self.name}'
    
    def to_table(self):
        return {
            'name': self.name,
            'district': self.district.name,
            'ward_count': len(self.ward),
            'action': f"""<div class="d-flex justify-content-around">
            <a href='/sub_district/{self.id}' class='btn btn-info'><i class='bi bi-info-square'></i></a> 
            <form method='POST' action='/sub_district/{self.id}/delete' onsubmit="return confirm('Apakah Anda yakin?');">
                <button type='submit' class='btn btn-danger'><i class='bi bi-trash'></i></button>
            </form>
            </div>""",
            'updated_at': self.updated_at.strftime('%d/%m/%Y')
        }

class Ward(db.Model):
    __tablename__ = 'ward'

    id = db.Column(db.Integer, primary_key=True)
    id_sub_district = db.Column(db.Integer, db.ForeignKey('sub_district.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.Date)
    updated_at = db.Column(db.Date)
    owner = db.relationship('Owner', backref='ward', lazy=True)
    umkm = db.relationship('Umkm', backref='ward', lazy=True)
    
    def __repr__(self):
        return f'{self.id}, {self.name}'
    
    def to_table(self):
        return {
            'name': self.name,
            'sub_district': self.sub_district.name,
            'umkm_count': len(self.umkm),
            'action': f"""<div class="d-flex justify-content-around">
            <a href='/ward/{self.id}' class='btn btn-info'><i class='bi bi-info-square'></i></a> 
            <form method='POST' action='/ward/{self.id}/delete' onsubmit="return confirm('Apakah Anda yakin?');">
                <button type='submit' class='btn btn-danger'><i class='bi bi-trash'></i></button>
            </form>
            </div>""",
            'updated_at': self.updated_at.strftime('%d/%m/%Y')
        }

class Owner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_ward = db.Column(db.Integer, db.ForeignKey('ward.id'), nullable=False)
    nik = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    postal_code = db.Column(db.String(255), nullable=False)
    note = db.Column(db.String(1020))
    npwp = db.Column(db.String(255))
    created_at = db.Column(db.Date)
    updated_at = db.Column(db.Date)
    umkm = db.relationship('Umkm', backref='owner', lazy=True)

    def __repr__(self):
        return f'{self.id}, {self.name}, {self.nik}'
    
    def to_table(self):
        return {
            'updated_at': self.updated_at.strftime('%d/%m/%Y'),
            'nik': self.nik,
            'name': self.name,
            'ward': self.ward.name,
            'sub_district': self.ward.sub_district.name,
            'district': self.ward.sub_district.district.name,
            'province': self.ward.sub_district.district.province.name,
            'umkm_count': len(self.umkm),
            'action': f"""<div class="d-flex justify-content-around">
            <a href='/owner/{self.id}' class='btn btn-info'><i class='bi bi-info-square'></i></a> 
            <form method='POST' action='/owner/{self.id}/delete' onsubmit="return confirm('Apakah Anda yakin?');">
                <button type='submit' class='btn btn-danger'><i class='bi bi-trash'></i></button>
            </form>
            </div>"""
        }

class Umkm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_owner = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)
    id_ward = db.Column(db.Integer, db.ForeignKey('ward.id'), nullable=False)
    id_business_category = db.Column(db.Integer,db.ForeignKey('business_category.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False, unique=True)
    address = db.Column(db.String(510), nullable=False)
    business_type = db.Column(db.String(255))
    start_date = db.Column(db.Date, nullable=False)
    workers = db.Column(db.Integer)
    modal = db.Column(db.Float)
    email = db.Column(db.String(255))
    facebook = db.Column(db.String(255))
    instagram = db.Column(db.String(255))
    twitter = db.Column(db.String(255))
    marketplace = db.Column(db.String(255))
    website = db.Column(db.String(255))
    legal_entity = db.Column(db.String(1020))
    problem = db.Column(db.String(4080))
    created_at = db.Column(db.Date)
    updated_at = db.Column(db.Date)
    brand = db.relationship('Brand', backref='umkm', lazy=True)

    def __repr__(self):
        return f'{self.id}, {self.name}'

    def to_table(self):
        return {
            'name': self.name,
            'business_cat': self.business_category.business_category,
            'ward': self.ward.name,
            'sub_district': self.ward.sub_district.name,
            'district': self.ward.sub_district.district.name,
            'province': self.ward.sub_district.district.province.name,
            'brand_count': len(self.brand),
            'action': f"""<div class="d-flex justify-content-around">
            <a href='/umkm/{self.id}' class='btn btn-info'><i class='bi bi-info-square'></i></a> 
            <form method='POST' action='/umkm/{self.id}/delete' onsubmit="return confirm('Apakah Anda yakin?');">
                <button type='submit' class='btn btn-danger'><i class='bi bi-trash'></i></button>
            </form>
            </div>""",
            'updated_at': self.updated_at.strftime('%d/%m/%Y')
        }

class Business_Category(db.Model):
    __tablename__ = 'business_category'

    id = db.Column(db.Integer, primary_key=True)
    business_category = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.Date)
    updated_at = db.Column(db.Date)

    umkm = db.relationship('Umkm', backref='business_category', lazy=True)

    def __repr__(self):
        return f'{self.id}, {self.business_category}'
    
    def to_table(self):
        return {
            'name': self.business_category,
            'umkm_count': len(self.umkm),
            'action': f"""<div class="d-flex justify-content-around">
            <a href='/business_category/{self.id}' class='btn btn-info'><i class='bi bi-info-square'></i></a> 
            <form method='POST' action='/business_category/{self.id}/delete' onsubmit="return confirm('Apakah Anda yakin?');">
                <button type='submit' class='btn btn-danger'><i class='bi bi-trash'></i></button>
            </form>
            </div>""",
            'updated_at': self.updated_at.strftime('%d/%m/%Y')
        }

class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_umkm = db.Column(db.Integer, db.ForeignKey('umkm.id'), nullable=False)
    brand = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.Date)
    updated_at = db.Column(db.Date)

    product = db.relationship('Product', backref='brand', lazy=True)

    def __repr__(self):
        return f'{self.id}, {self.brand}'
    
    def to_table(self):
        return {
            'name': self.brand,
            'umkm': self.umkm.name,
            'product_count': len(self.product),
            'action': f"""<div class="d-flex justify-content-around">
            <a href='/brand/{self.id}' class='btn btn-info'><i class='bi bi-info-square'></i></a> 
            <form method='POST' action='/brand/{self.id}/delete' onsubmit="return confirm('Apakah Anda yakin?');">
                <button type='submit' class='btn btn-danger'><i class='bi bi-trash'></i></button>
            </form>
            </div>""",
            'updated_at': self.updated_at.strftime('%d/%m/%Y')
        }

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_brand = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False)
    id_type = db.Column(db.Integer, db.ForeignKey('product_type.id'), nullable=False)
    id_category = db.Column(db.Integer, db.ForeignKey('product_category.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    price_reseller = db.Column(db.Float, nullable=False)
    variance = db.Column(db.String(255))
    size = db.Column(db.String(255))
    description = db.Column(db.String(1022))
    created_at = db.Column(db.Date)
    updated_at = db.Column(db.Date)

    def __repr__(self):
        return f'{self.id}, {self.name}, {self.price}, {self.id_type}'
    
    def to_table(self):
        return {
            'name': self.name,
            'brand': self.brand.brand,
            'product_type': self.product_type.product_type,
            'product_cat': self.product_category.product_category,
            'price': self.price,
            'action': f"""<div class="d-flex justify-content-around">
            <a href='/product/{self.id}' class='btn btn-info'><i class='bi bi-info-square'></i></a> 
            <form method='POST' action='/product/{self.id}/delete' onsubmit="return confirm('Apakah Anda yakin?');">
                <button type='submit' class='btn btn-danger'><i class='bi bi-trash'></i></button>
            </form>
            </div>""",
            'updated_at': self.updated_at.strftime('%d/%m/%Y')
        }

class Product_Type(db.Model):
    __tablename__ = 'product_type'

    id = db.Column(db.Integer, primary_key=True)
    product_type = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.Date)
    updated_at = db.Column(db.Date)

    product = db.relationship('Product', backref='product_type', lazy=True)

    def __repr__(self):
        return f'{self.id}, {self.product_type}'
    
    def to_table(self):
        return {
            'name': self.product_type,
            'product_count': len(self.product),
            'action': f"""<div class="d-flex justify-content-around">
            <a href='/product_type/{self.id}' class='btn btn-info'><i class='bi bi-info-square'></i></a> 
            <form method='POST' action='/product_type/{self.id}/delete' onsubmit="return confirm('Apakah Anda yakin?');">
                <button type='submit' class='btn btn-danger'><i class='bi bi-trash'></i></button>
            </form>
            </div>""",
            'updated_at': self.updated_at.strftime('%d/%m/%Y')
        }

class Product_Category(db.Model):
    __tablename__ = 'product_category'

    id = db.Column(db.Integer, primary_key=True)
    product_category = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.Date)
    updated_at = db.Column(db.Date)

    product = db.relationship('Product', backref='product_category', lazy=True)

    def __repr__(self):
        return f'{self.id}, {self.product_category}'
    
    def to_table(self):
        return {
            'name': self.product_category,
            'product_count': len(self.product),
            'action': f"""<div class="d-flex justify-content-around">
            <a href='/product_category/{self.id}' class='btn btn-info'><i class='bi bi-info-square'></i></a> 
            <form method='POST' action='/product_category/{self.id}/delete' onsubmit="return confirm('Apakah Anda yakin?');">
                <button type='submit' class='btn btn-danger'><i class='bi bi-trash'></i></button>
            </form>
            </div>""",
            'updated_at': self.updated_at.strftime('%d/%m/%Y')
        }

class Excel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_type = db.Column(db.Integer, db.ForeignKey('excel_type.id'), nullable=False)
    id_user = db.Column(db.String(22), db.ForeignKey('user.id'), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.Date, nullable=True)
    updated_at = db.Column(db.Date, nullable=True)
    deleted_at = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f"User('{self.id}', '{self.path}')"
    
    def to_table(self):
        return {
            'name': self.path,
            'uploader': self.user.name,
            'type': self.excel_type.excel_type.title(),
            'updated_at': self.updated_at.strftime('%d/%m/%Y'),
            'action': f"""<div class="d-flex justify-content-around"> 
            <form method='POST' action='/excel/{self.id}/delete' onsubmit="return confirm('Apakah Anda yakin?');">
                <button type='submit' class='btn btn-danger'><i class='bi bi-trash'></i></button>
            </form>
            </div>""",
        }

class Excel_Type(db.Model):
    __tablename__ = 'excel_type'

    id = db.Column(db.Integer, primary_key=True)
    excel_type = db.Column(db.String(255))

    excel = db.relationship('Excel', backref='excel_type', lazy=True)

    def __repr__(self):
        return f"User('{self.id}', '{self.excel_type}')"

class DistrictSchema(ma.SQLAlchemyAutoSchema):
      class Meta:
            fields = ('id', 'name')

class Sub_DistrictSchema(ma.SQLAlchemyAutoSchema):
      class Meta:
            fields = ('id', 'name')

class WardSchema(ma.SQLAlchemyAutoSchema):
      class Meta:
            fields = ('id', 'name')