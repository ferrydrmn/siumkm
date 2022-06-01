# import os
import shortuuid
# from PIL import Image
from datetime import datetime
from sqlalchemy import or_, cast, Date #func
from script import app, db, bcrypt
from script.models import Province, District, Sub_District, Ward, DistrictSchema, Sub_DistrictSchema, WardSchema, User, Owner, Umkm
from script.forms import OwnerForm, UmkmForm, LoginForm # SellerForm, VillageForm, MenuForm
from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, url_for, redirect, flash, request, abort, jsonify


# ======================================== #
#       ROUTE UNTUK PENGUNJUNG BIASA       #
# ======================================== #

# # Fungsi thousand separator
# def place_value(number):
#     return ("{:,}".format(number))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Selamat datang, {user.name}.', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login gagal. Isi data email dan password dengan benar.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    owner_count = db.session.query(Owner).count()
    umkm_count = db.session.query(Umkm).count()
    # owner_last_update = db.session.query(cast(Owner.updated_at, Date)).distinct().order_by(Owner.updated_at.desc()).first()
    # umkm_last_update = db.session.query(cast(Umkm.updated_at, Date)).distinct().order_by(Umkm.updated_at.desc()).first()
    owner_last_update = Owner.query.order_by(Owner.updated_at.desc()).first()
    if owner_last_update is not None:
        owner_last_update = datetime.date(owner_last_update.updated_at).strftime('%d-%m-%Y')
    else:
        owner_last_update = 'Belum pernah dilakukan update!'
    umkm_last_update = Umkm.query.order_by(Umkm.updated_at.desc()).first()
    if umkm_last_update is not None:
        umkm_last_update = datetime.date(umkm_last_update.updated_at).strftime('%d-%m-%Y')
    else:
        umkm_last_update = 'Belum pernah dilakukan update!'
    return render_template('index.html', title='Home', active='home', owner_count=owner_count, umkm_count=umkm_count, 
    owner_last_update=owner_last_update, umkm_last_update=umkm_last_update)

# ======================================================== #
#       ROUTE UNTUK KEBUTUHAN ATAU VALIDASI FORM           #
# ======================================================== #

# Route ambil kota/kabupaten, dikirim ke form
@app.route('/get_district', methods=['GET'])
@login_required
def get_district():
    districts = District.query.filter_by(id_province=request.args.get('id_province')).all()
    district_schema = DistrictSchema(many=True)
    return jsonify({'districts': district_schema.dump(districts)})

# Route ambil kecamatan, dikirim ke form
@app.route('/get_sub_district', methods=['GET'])
@login_required
def get_sub_district():
    sub_districts = Sub_District.query.filter_by(id_district=request.args.get('id_district')).all()
    sub_district_schema = Sub_DistrictSchema(many=True)
    return jsonify({'sub_districts': sub_district_schema.dump(sub_districts)})

# Route ambil desa, dikirim ke form
@app.route('/get_ward', methods=['GET'])
@login_required
def get_ward():
    wards = Ward.query.filter_by(id_sub_district=request.args.get('id_sub_district')).all()
    ward_schema = WardSchema(many=True)
    return jsonify({'wards': ward_schema.dump(wards)})

# Route ambil data NIK untuk validasi unik, hasil pemeriksaan dikirim ke form
@app.route('/get_nik', methods=['GET'])
@login_required
def get_nik():
    if request.args.get('id') == 0:
        owner = Owner.query.filter_by(nik=request.args.get('nik')).first()
        if owner:
            return jsonify({'error': 'NIK sudah digunakan!'})
        return jsonify({'success': 'NIK bisa digunakan!'})
    owner = Owner.query.filter_by(nik=request.args.get('nik')).first()
    if owner:
        if owner.id == int(request.args.get('id')):
            return jsonify({'success': 'NIK bisa digunakan!'})
        return jsonify({'error': 'NIK sudah digunakan!'})
    return jsonify({'success': 'NIK bisa digunakan!'})

# Route cek NIK, apakah sudah terdaftar atau belum
@app.route('/check_nik', methods=['GET'])
@login_required
def check_nik():
    owner = Owner.query.filter_by(nik=request.args.get('nik')).first()
    if not owner:
        return jsonify({'error': 'NIK tidak terdaftar pada sistem!'})
    return jsonify({'success': 'NIK terdaftar pada sistem!'})


# ================================== #
#       ROUTE UNTUK CRUD OWNER       #
# ================================== #

# Route untuk menampilkan data pemilik UMKM 
@app.route('/owner', methods=['GET', 'POST'])
@login_required
def owner_home():
    page = request.args.get('page', 1, type=int)
    owners = Owner.query.order_by(Owner.updated_at.desc()).paginate(page=page, per_page=10)
    return render_template('owner/home_owner.html', title='Data Pemilik UMKM', owners=owners, page=page, active='owner', len=len)

# Route untuk mencari data pemilik UMKM 
@app.route('/owner/search', methods=['GET', 'POST'])
@login_required
def owner_search():
    search = f"%{request.args.get('search_owner')}%"
    page = request.args.get('page', 1, type=int)
    owners = Owner.query.filter(or_(Owner.nik.like(search), Owner.name.like(search))).paginate(page=page, per_page=10)
    return render_template('owner/search_owner.html', title='Cari Data Pemilik UMKM', owners=owners, page=page, active='owner', len=len)

# Route untuk menambahkan data pemilik UMKM 
@app.route('/owner/create', methods=['GET', 'POST'])
@login_required
def owner_create():
    form = OwnerForm()
    if form.validate_on_submit():
        owner = Owner(
            nik = form.nik.data,
            name = form.name.data,
            id_ward = form.ward.data,
            address = form.address.data,
            postal_code = form.postal_code.data,
            note = form.note.data,
            npwp = form.npwp.data,
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        db.session.add(owner)
        db.session.commit()
        flash('Data pemilik UMKM berhasil ditambahkan!', 'success')
        return redirect(url_for('owner_home'))
    return render_template('owner/create_owner.html', title='Tambah Data Pemilik UMKM', form=form, active='owner')

# Route untuk mengubah data pemilik UMKM 
@app.route('/owner/<int:id>/update', methods=['GET', 'POST'])
@login_required
def owner_update(id):
    owner = Owner.query.get_or_404(id)
    form = OwnerForm()
    form.submit.data = 'Edit'
    if form.validate_on_submit():
        owner = Owner.query.get(form.id_owner.data)
        owner.nik = form.nik.data
        owner.name = form.name.data
        owner.id_ward = form.ward.data
        owner.address = form.address.data
        owner.postal_code = form.postal_code.data
        owner.note = form.note.data
        owner.npwp = form.npwp.data
        owner.updated_at = datetime.now()
        db.session.commit()
        flash('Data pemilik UMKM berhasil diubah!', 'success')
        return redirect(url_for('owner_home'))
    else:
        districts_list = [(i.id, i.name) for i in District.query.filter_by(id_province=owner.ward.sub_district.district.province.id).all()]
        sub_districts_list = [(i.id, i.name) for i in Sub_District.query.filter_by(id_district=owner.ward.sub_district.district.id).all()]
        wards_list = [(i.id, i.name) for i in Ward.query.filter_by(id_sub_district=owner.ward.sub_district.id).all()]
        form.id_owner.data = owner.id
        form.district.choices = districts_list
        form.sub_district.choices = sub_districts_list
        form.ward.choices = wards_list
        form.province.data = owner.ward.sub_district.district.province.id
        form.district.data = owner.ward.sub_district.district.id
        form.sub_district.data = owner.ward.sub_district.id
        form.ward.data = owner.id_ward
        form.nik.data = owner.nik
        form.name.data = owner.name
        form.address.data = owner.address
        form.postal_code.data = owner.postal_code
    return render_template('owner/update_owner.html', title='Detil Data Pemilik UMKM', form=form, active='owner')

# Route untuk menghapus  data pemilik UMKM
@app.route('/owner/<int:id>/delete', methods=['POST'])
@login_required
def owner_delete(id):
    owner = Owner.query.get(id)
    db.session.delete(owner)
    db.session.commit()
    flash('Data pemilik UMKM berhasil dihapus!', 'danger')
    return redirect(url_for('owner_home'))

# ================================== #
#       ROUTE UNTUK CRUD UMKM        #
# ================================== #

# Route untuk menampilkan data UMKM 
@app.route('/umkm', methods=['GET', 'POST'])
@login_required
def umkm_home():
    page = request.args.get('page', 1, type=int)
    umkms = Umkm.query.order_by(Umkm.updated_at.desc()).paginate(page=page, per_page=10)
    return render_template('umkm/home_umkm.html', title='Data UMKM', umkms=umkms, page=page, active='umkm', len=len)

@app.route('/umkm/search/', methods=['GET'])
@login_required
def umkm_search():
    search = f"%{request.args.get('search_umkm')}%"
    page = request.args.get('page', 1, type=int)
    umkms = Umkm.query.filter(or_(Umkm.name.like(search), Umkm.uid.like(search))).paginate(page=page, per_page=10)
    return render_template('umkm/search_umkm.html', title='Cari Data UMKM', umkms=umkms, page=page, active='umkm', len=len)


# Route untuk menambahkan data pemilik UMKM 
@app.route('/umkm/create', methods=['GET', 'POST'])
@login_required
def umkm_create():
    form = UmkmForm()
    title = 'Tambah Data UMKM'
    if form.validate_on_submit():
        jsonify(form.errors)
        id_owner = Owner.query.filter_by(nik=form.nik.data).first().id
        umkm = Umkm(
            id_owner = id_owner,
            id_ward = form.ward.data,
            id_business_category = form.business_category.data,
            business_type = form.business_type.data,
            uid = shortuuid.uuid(),
            name = form.name.data,
            address = form.address.data,
            modal = form.modal.data,
            workers = form.workers.data,
            email = form.email.data,
            facebook = form.facebook.data,
            instagram = form.instagram.data,
            twitter = form.twitter.data,
            marketplace = form.marketplace.data,
            website = form.website.data,
            start_date = form.start_date.data,
            legal_entity = form.legal_entity.data,
            problem = form.problem.data,
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        db.session.add(umkm)
        db.session.commit()
        flash('Data UMKM berhasil ditambahkan!', 'success')
        return redirect(url_for('umkm_home'))
    return render_template('umkm/create_umkm.html', title=title, form=form, active='umkm')

# Route untuk mengubah data pemilik UMKM 
@app.route('/umkm/<int:id>/update', methods=['GET', 'POST'])
@login_required
def umkm_update(id):
    umkm = Umkm.query.get_or_404(id)
    form = UmkmForm()
    form.submit.data = 'Edit'
    if form.validate_on_submit():
        id_owner = Owner.query.filter_by(nik=form.nik.data).first().id
        umkm.id_owner = id_owner
        umkm.id_ward = form.ward.data
        umkm.id_business_category = form.business_category.data
        umkm.business_type = form.business_type.data
        umkm.name = form.name.data
        umkm.address = form.address.data
        umkm.modal = form.modal.data
        umkm.workers = form.workers.data
        umkm.email = form.email.data
        umkm.facebook = form.facebook.data
        umkm.instagram = form.instagram.data
        umkm.twitter = form.twitter.data
        umkm.marketplace = form.marketplace.data
        umkm.website = form.website.data
        umkm.start_date = form.start_date.data
        umkm.legal_entity = form.legal_entity.data
        umkm.problem = form.problem.data
        umkm.updated_at = datetime.now()
        db.session.commit()
        flash('Data UMKM berhasil diubah!', 'success')
        return redirect(url_for('umkm_home'))
    else:
        id_owner = umkm.owner.id
        districts_list = [(i.id, i.name) for i in District.query.filter_by(id_province=umkm.ward.sub_district.district.province.id).all()]
        sub_districts_list = [(i.id, i.name) for i in Sub_District.query.filter_by(id_district=umkm.ward.sub_district.district.id).all()]
        wards_list = [(i.id, i.name) for i in Ward.query.filter_by(id_sub_district=umkm.ward.sub_district.id).all()]
        form.id_umkm.data = umkm.id
        form.district.choices = districts_list
        form.sub_district.choices = sub_districts_list
        form.ward.choices = wards_list
        form.province.data = umkm.ward.sub_district.district.province.id
        form.district.data = umkm.ward.sub_district.district.id
        form.sub_district.data = umkm.ward.sub_district.id
        form.ward.data = umkm.id_ward
        form.nik.data = umkm.owner.nik
        form.name.data = umkm.name
        form.address.data = umkm.address
        form.business_category.data = umkm.business_category.id
        form.business_type.data = umkm.business_type
        form.modal.data = umkm.modal
        form.workers.data = umkm.workers
        form.email.data = umkm.email
        form.facebook.data = umkm.facebook
        form.instagram.data = umkm.instagram
        form.twitter.data = umkm.twitter
        form.marketplace.data = umkm.marketplace
        form.website.data = umkm.website
        form.start_date.data = umkm.start_date
        form.legal_entity.data = umkm.legal_entity
        form.problem.data = umkm.problem
    return render_template('umkm/update_umkm.html', title='Detil Data Pemilik', form=form, id_owner=id_owner, active='umkm')

# Route untuk menghapus data UMKM
@app.route('/umkm/<int:id>/delete', methods=['POST'])
@login_required
def umkm_delete(id):
    umkm = Umkm.query.get(id)
    db.session.delete(umkm)
    db.session.commit()
    flash('Data pemilik UMKM berhasil dihapus!', 'danger')
    return redirect(url_for('umkm_home'))

# @app.route('/location/<string:village_name>', methods=['GET'])
# def location(village_name):
#     village = Village.query.filter_by(name=village_name).first_or_404()
#     umkms = Umkm.query.filter_by(id_village=village.id, status=True).all()
#     return render_template('location.html', village=village, umkms=umkms, len=len)

# @app.route('/detail/<int:umkm_id>')
# def detail(umkm_id):
#     umkm = Umkm.query.filter_by(status=True, id=umkm_id).first_or_404()
#     menus = Menu.query.filter_by(id_umkm=umkm.id, status=True)
#     return render_template('detail.html', title=umkm.name, umkm=umkm, menus=menus, place_value=place_value)


# # ============================== #
# #       ROUTE UNTUK ADMIN        #
# # ============================== #

# # Fungsi untuk mengambil informasi gambar
# def save_picture(form_picture, path):
#     random_name = shortuuid.ShortUUID().random(length=10)
#     _, f_ext = os.path.splitext(form_picture.filename)
#     picture_fn = random_name + f_ext

#     if path == 'umkm':
#         picture_path = os.path.join(app.root_path, 'static/src/images/umkm', picture_fn)
#     else:
#         picture_path = os.path.join(app.root_path, 'static/src/images/villages', picture_fn)

#     output_size = (320, 180)
#     i = Image.open(form_picture)
#     i.thumbnail(output_size)
#     i.save(picture_path)

#     return picture_fn

# @app.route('/admin/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect('umkm')
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = Users.query.filter_by(email=form.email.data).first()
#         if user and bcrypt.check_password_hash(user.password, form.password.data):
#             login_user(user)
#             next_page = request.args.get('next')
#             return redirect(next_page) if next_page else redirect(url_for('admin_umkm'))
#         else:
#             flash('Login Unsuccessful. Please check email and password', 'danger')
#     return render_template('admin/login.html', title='Login', form=form)

# @app.route('/admin/test', methods=['GET', 'POST'])
# def test():
#     return render_template('admin/dashboard.html')

# @app.route('/admin/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('login'))

# # ========== HOME =============

# @app.route('/admin/umkm')
# @login_required
# def admin_umkm():
#     page = request.args.get('page', 1, type=int)
#     umkms = Umkm.query.filter_by(status=True).order_by(Umkm.id.asc()).paginate(per_page=20, page=page)
#     return render_template('admin/umkm.html', umkms=umkms)

# @app.route('/admin/seller')
# @login_required
# def admin_seller():
#     page = request.args.get('page', 1, type=int)
#     sellers = Seller.query.filter_by(status=True).order_by(Seller.id.asc()).paginate(per_page=20, page=page)
#     return render_template('admin/seller.html', sellers=sellers)

# @app.route('/admin/village')
# @login_required
# def admin_village():
#     page = request.args.get('page', 1, type=int)
#     villages = Village.query.filter_by(status=True).order_by(Village.id.asc()).paginate(per_page=20, page=page)
#     return render_template('admin/village.html', villages=villages)

# # ========== CRUD UMKM =============

# @app.route('/admin/umkm/new', methods=['POST', 'GET'])
# @login_required
# def add_umkm():
#     form = UmkmForm()
#     if form.validate_on_submit():
#         seller = Seller.query.filter_by(phone_number=form.phone_number.data).first()
#         if seller:
#             if form.shipping_free.data == True:
#                 form.shipping_price.data = 0
#             if form.picture.data:
#                 picture = save_picture(form.picture.data, 'umkm')
#             else:
#                 picture = 'default.jpg'
#             umkm = Umkm(
#                 name = form.name.data,
#                 open = form.open.data,
#                 close = form.close.data,
#                 shipping_free = form.shipping_free.data,
#                 description = form.description.data,
#                 location_link = form.location_link.data,
#                 location_desc = form.location_desc.data,
#                 picture = picture,
#                 status = True,
#                 id_village = form.id_village.data,
#                 id_seller = seller.id,
#                 id_user = current_user.id,
#             )
#             db.session.add(umkm)
#             db.session.commit()
#             return redirect(url_for('admin_umkm'))
#         else:
#             flash('Nomor pemilik belum terdaftar. Tambahkan data pemilik baru!')
#             return redirect(url_for('add_seller', phone_number = form.phone_number.data))
#     return render_template('/admin/add_umkm.html', form=form, legend='Tambah Data UMKM')

# @app.route('/admin/umkm/<int:umkm_id>/update', methods=['GET', 'POST'])
# @login_required
# def update_umkm(umkm_id):
#     umkm = Umkm.query.get_or_404(umkm_id)
#     form = UmkmForm()
#     if form.validate_on_submit():
#         umkm_check = Umkm.query.filter_by(name=form.name.data, status=True).first()
#         seller_check = Seller.query.filter_by(phone_number = form.phone_number.data).first()
#         if umkm_check:
#             if umkm_check.id == umkm.id:
#                 if seller_check:
#                     umkm.name = form.name.data
#                     umkm.open = form.open.data
#                     umkm.close = form.close.data
#                     umkm.shipping_free = form.shipping_free.data
#                     if form.shipping_free.data == True:
#                         umkm.shipping_price = 0
#                     else:
#                         umkm.shipping_price = form.shipping_price.data
#                     umkm.location_link = form.location_link.data
#                     umkm.location_desc = form.location_desc.data
#                     umkm.picture = form.picture.data
#                     umkm.description = form.description.data
#                     umkm.id_seller = seller_check.id
#                     umkm.id_village = form.id_village.data
#                     if form.picture.data:
#                         umkm.picture = save_picture(form.picture.data, 'umkm')
#                     db.session.commit()
#                     flash('Data UMKM berhasil diubah!')
#                     return redirect(url_for('admin_umkm'))
#                 else:
#                     flash('Nomor HP penjual tidak terdaftar pada sistem!')
#             else:
#                 flash('Nama UMKM telah digunakan. Gunakan nama yang lain!')
#         else:
#             if seller_check:
#                 umkm.id_seller = seller_check.id
#                 umkm.name = form.name.data
#                 umkm.open = form.open.data
#                 umkm.close = form.close.data
#                 umkm.shipping_free = form.shipping_free.data
#                 if form.shipping_free.data == True:
#                     umkm.shipping_price = 0
#                 else:
#                     umkm.shipping_price = form.shipping_price.data
#                 umkm.location_link = form.location_link.data
#                 umkm.location_desc = form.location_desc.data
#                 umkm.picture = form.picture.data
#                 umkm.description = form.description.data
#                 umkm.id_seller = seller_check.id
#                 umkm.id_village = form.id_village.data
#                 if form.picture.data:
#                     umkm.picture = save_picture(form.picture.data, 'umkm')
#                 db.session.commit()
#                 flash('Data UMKM berhasil diubah!')
#                 return redirect(url_for('admin_umkm'))
#             else:
#                 flash('Nomor HP penjual tidak terdaftar pada sistem!')
#     elif request.method == 'GET':
#         form.id_village.default = umkm.id_village
#         form.process()
#         form.phone_number.data = umkm.seller.phone_number
#         form.name.data = umkm.name
#         form.open.data = umkm.open
#         form.close.data = umkm.close
#         form.description.data = umkm.description
#         form.shipping_free.data = umkm.shipping_free
#         form.shipping_price.data = umkm.shipping_price
#         form.location_link.data = umkm.location_link
#         form.location_desc.data = umkm.location_desc
#     return render_template('/admin/add_umkm.html', umkm=umkm, form=form, title=umkm.name, legend='Edit Data UMKM')

# @app.route('/admin/umkm/<int:umkm_id>/delete', methods=['POST'])
# @login_required
# def delete_umkm(umkm_id):
#     umkm = Umkm.query.get_or_404(umkm_id)
#     umkm.status = False
#     for menu in umkm.menu:
#         menu.status = False
#     db.session.commit()
#     flash('Data UMKM berhasil dihapus!')
#     return redirect(url_for('admin_umkm'))

# # ========== CRUD SELLER =============

# @app.route('/admin/seller/new', methods=['GET', 'POST'])
# @login_required
# def add_seller():
#     form = SellerForm()
#     if form.validate_on_submit():
#         seller = Seller.query.filter_by(phone_number=form.phone_number.data).first()
#         if seller:
#             flash('Nomor HP telah digunakan. Gunakan nomor HP yang lain!')
#         else:
#             seller = Seller(
#                 name = form.name.data,
#                 phone_number = form.phone_number.data,
#                 status = True
#             )
#             db.session.add(seller)
#             db.session.commit()
#             flash('Data pemilik berhasil ditambahkan!')
#             return redirect(url_for('admin_seller'))
#     return render_template('/admin/add_seller.html', form=form, legend='Tambah Data Pemilik')

# @app.route('/admin/seller/<int:seller_id>/update', methods=['GET', 'POST'])
# @login_required
# def update_seller(seller_id):
#     seller = Seller.query.get_or_404(seller_id)
#     form = SellerForm()
#     if form.validate_on_submit():
#         seller_check = Seller.query.filter_by(phone_number=form.phone_number.data).first()
#         if seller_check:
#             if seller_check.id == seller_id:
#                 seller.name = form.name.data
#                 seller.phone_number = form.phone_number.data
#                 db.session.commit()
#                 flash('Data pemilik berhasil diubah!')
#                 return redirect(url_for('admin_seller'))
#             else:
#                 flash('Nomor HP telah digunakan. Gunakan nomor HP yang lain!')
#         else:
#             seller.name = form.name.data
#             seller.phone_number = form.phone_number.data
#             db.session.commit()
#             flash('Data pemilik berhasil diubah!')
#             return redirect(url_for('admin_seller'))
#     elif request.method == 'GET':
#         form.name.data = seller.name
#         form.phone_number.data = seller.phone_number
#     return render_template('/admin/add_seller.html', seller=seller, form=form, title=seller.name, legend='Edit Data UMKM')

# @app.route('/admin/seller/<int:seller_id>/delete', methods=['POST'])
# @login_required
# def delete_seller(seller_id):
#     seller = Seller.query.get_or_404(seller_id)
#     seller.status = False
#     for umkm in seller.umkm:
#         umkm.status = False
#         for menu in umkm.menu:
#             menu.status = False
#     db.session.commit()
#     flash('Data penjual berhasil dihapus!')
#     return redirect(url_for('admin_seller'))

# # ========== CRUD VILLAGE =============

# @app.route('/admin/village/new', methods=['GET', 'POST'])
# @login_required
# def add_village():
#     form = VillageForm()
#     if form.validate_on_submit():
#         village = Village.query.filter_by(name=form.name.data).first()
#         if village:
#             flash('Nama desa telah digunakan. Gunakan nama yang lain!')
#         else:
#             if form.picture.data:
#                 picture = save_picture(form.picture.data, 'village')
#             else:
#                 picture = 'default.jpg'
#             village = Village(
#                 name = form.name.data,
#                 picture = picture
#             )
#             db.session.add(village)
#             db.session.commit()
#             flash('Data desa berhasil ditambahkan!')
#             return redirect(url_for('admin_village'))
#     return render_template('/admin/add_village.html', form=form, legend='Tambah Data Desa')

# @app.route('/admin/village/<int:village_id>/update', methods=['GET', 'POST'])
# @login_required
# def update_village(village_id):
#     village = Village.query.get_or_404(village_id)
#     form = VillageForm()
#     if form.validate_on_submit():
#         village_check = Village.query.filter_by(name=form.name.data).first()
#         if village_check:
#             if village_check.id == village.id:
#                 village.name = form.name.data
#                 if form.picture.data:
#                     village.picture = save_picture(form.picture.data, 'village')
#                 db.session.commit()
#                 flash('Data desa berhasil diubah!')
#                 return redirect(url_for('admin_seller'))
#             else:
#                 flash('Nama desa telah digunakan. Gunakan nama yang lain!')
#         else:
#             village.name = form.name.data
#             if form.picture.data:
#                 village.picture = save_picture(form.picture.data, 'village')
#             db.session.commit()
#             flash('Data desa berhasil ditambahkan')
#             return redirect(url_for('admin_village'))
#     elif request.method == 'GET':
#         form.name.data = village.name
#     return render_template('/admin/add_village.html', village=village, form=form, title=village.name, legend='Edit Data Desa')

# @app.route('/admin/village/<int:village_id>/delete', methods=['POST'])
# @login_required
# def delete_village(village_id):
#     village = Village.query.get_or_404(village_id)
#     village.status = False
#     for umkm in village.umkm:
#         umkm.status = False
#         for menu in umkm.menu:
#             menu.status = False
#     db.session.commit()
#     flash('Data desa berhasil dihapus!')  
#     return redirect(url_for('admin_village'))

# # ========== CRUD MENU =============

# @app.route('/admin/umkm/<int:umkm_id>/menu', methods=['GET', 'POST'])
# @login_required
# def umkm_menu(umkm_id):
#     page = request.args.get('page', 1, type=int)
#     menus = Menu.query.filter_by(id_umkm=umkm_id, status=True).order_by(Menu.id.asc()).paginate(page=page, per_page=10)
#     return render_template('/admin/menu.html', menus=menus, umkm_id=umkm_id)

# @app.route('/admin/umkm/<int:umkm_id>/menu/new', methods=['GET', 'POST'])
# @login_required
# def add_menu(umkm_id):
#     form = MenuForm()
#     umkm = Umkm.query.get_or_404(umkm_id)
#     if form.validate_on_submit():
#         menu = Menu(
#             name = form.name.data,
#             price = form.price.data,
#             id_umkm = umkm_id,
#             id_type = form.id_type.data,
#             status = True
#         )
#         db.session.add(menu)
#         db.session.commit()
#         flash('Data menu berhasil ditambahkan!')
#         return redirect(url_for('umkm_menu', umkm_id=umkm_id))
#     return render_template('/admin/add_menu.html', form=form, id_umkm=umkm_id, legend="Tambah menu " + umkm.name)

# @app.route('/umkm/<int:umkm_id>/menu/<int:menu_id>/update', methods=['GET', 'POST'])
# @login_required
# def update_menu(menu_id, umkm_id):
#     menu = Menu.query.filter_by(status=True, id=menu_id).first()
#     if menu:
#         form = MenuForm()
#         if form.validate_on_submit(): 
#             menu.name = form.name.data
#             menu.price = form.price.data
#             menu.id_type = form.id_type.data
#             db.session.commit()
#             flash('Data menu berhasil diubah!')
#             return redirect(url_for('umkm_menu', umkm_id=umkm_id))    
#         elif request.method == 'GET':
#             form.name.data = menu.name
#             form.price.data = menu.price
#             form.id_type.data = menu.id_type
#         return render_template('/admin/add_menu.html', menu=menu, form=form, legend='Edit Data Menu')
#     else:
#         return redirect(url_for('umkm_menu', umkm_id=umkm_id))

# @app.route('/admin/umkm/<int:umkm_id>/menu/<int:menu_id>/delete', methods=['POST'])
# @login_required
# def delete_menu(menu_id, umkm_id):
#     menu = Menu.query.get(menu_id)
#     menu.status = False
#     db.session.commit()
#     flash('Data menu berhasil dihapus!')  
#     return redirect(url_for('umkm_menu', umkm_id=umkm_id))