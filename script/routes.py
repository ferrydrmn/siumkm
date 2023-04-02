import os
import glob
import shortuuid
import pyexcel as pe
from datetime import datetime
from sqlalchemy import func
from script import app, db, bcrypt
from script.models import Business_Category, Excel, Product_Category, Province, District, Sub_District, Ward, DistrictSchema, Sub_DistrictSchema, WardSchema, User, Owner, Umkm, Brand, Product, Product_Type
from script.forms import BusinessCategoryForm, DistrictForm, ExcelForm, OwnerForm, PasswordForm, ProductCategoryForm, ProductTypeForm, SubDistrictForm, UmkmForm, BrandForm, ProductForm, LoginForm, ProvinceForm, WardForm
from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, url_for, redirect, flash, request, jsonify, send_file

# Route Home
@app.route('/')
@login_required
def home():
    owner_count = db.session.query(Owner).count()
    umkm_count = db.session.query(Umkm).count()
    brand_count = db.session.query(Brand).count()
    product_count = db.session.query(Product).count()
    return render_template('index.html', title='Dashboard', active='home', owner_count=owner_count, umkm_count=umkm_count, brand_count=brand_count, product_count=product_count)

# Route 404
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

# ======================================== #
#          ROUTE UNTUK PENGGUNA            #
# ======================================== #

@app.route('/login', methods=['GET', 'POST'])
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

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordForm()
    if form.validate_on_submit():
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data
        old_password = form.old_password.data
        if new_password != confirm_password:
            flash('Password baru dengan konfirmasi password tidak sama!', 'danger')
            return render_template('change_password.html', title='Ganti Password', active='home', form=form)
        else:
            new_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            user = User.query.get_or_404(current_user.id)
            if bcrypt.check_password_hash(user.password, old_password):
                user.password = new_password
                db.session.commit()
                flash('Ganti password berhasil dilakukan!', 'success')
                return redirect(url_for('change_password'))
            else:
                flash('Password lama salah!', 'danger')
                return render_template('change_password.html', title='Ganti Password', active='home', form=form)
   
    elif request.method == 'GET':
        return render_template('change_password.html', title='Ganti Password', active='home', form=form)

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

# Route cek nama UMKM, apakah nama UMKM dengan NIK yang dikirim sudah terdaftar atau belum
@app.route('/check_umkm', methods=['GET'])
@login_required
def check_umkm():
    id_umkm = request.args.get('id_umkm')
    name = request.args.get('name')
    umkm = Umkm.query.filter(Umkm.name.like(name)).first()
    if umkm and int(id_umkm) != umkm.id:
        return jsonify({'error': f'Nama UMKM telah dimiliki pengguna lain! Gunakan nama UMKM yang lain!'})
    return jsonify({'success': 'Nama UMKM dapat digunakan!'})

# Route cek nama UMKM, apakah sudah terdaftar di sistem
@app.route('/get_umkm', methods=['GET'])
@login_required
def get_umkm():
    umkm = Umkm.query.filter(Umkm.name.like(request.args.get('umkm'))).first()
    if not umkm:
        return jsonify({'error': 'Nama UMKM tidak terdaftar pada sistem!'})
    return jsonify({'success': 'Nama UMKM terdaftar pada sistem'})

# Route untuk cek nama brand, apakah unik atau tidak
@app.route('/get_brand', methods=['GET'])
@login_required
def get_brand():
    id_brand = int(request.args.get('id_brand'))
    brand = Brand.query.filter(Brand.brand.like(request.args.get('brand'))).first()
    if not brand:
        return jsonify({'success': 'Nama brand dapat digunakan!'})
    elif brand.id == id_brand: 
        return jsonify({'success': 'Nama brand dapat digunakan!'})
    else:
        return jsonify({'error': f'Nama brand tidak dapat digunakan!'})

# Route untuk cek nama brand, apakah terdaftar dalam sistem atau tidak
@app.route('/check_brand', methods=['GET'])
@login_required
def check_brand():
    brand = Brand.query.filter_by(brand=request.args.get('brand')).first()
    if not brand:
        return jsonify({'error': 'Nama brand tidak terdaftar dalam sistem!'})
    return jsonify({'success': 'Nama brand terdaftar dalam sistem!'})

# Route untuk cek nama provinsi, apakah terdaftar dalam sistem atau tidak
@app.route('/check_province', methods=['GET'])
@login_required
def check_province(): # AGENDA BESOK: SELESAIKAN ROUTE CEK ID PROVINSI
    id_province = request.args.get('id_province')
    province = Province.query.filter(Province.name.like(request.args.get('name'))).first()
    if not province or province.id == id_province:
        return jsonify({'success': 'Nama provinsi dapat digunakan!'})
    else:
        return jsonify({'error': 'Nama provinsi sudah digunakan! Gunakan nama yang lain!'})

# Route untuk cek ID provinsi, apakah terdaftar dalam sistem atau tidak
@app.route('/check_id_province', methods=['GET'])
@login_required
def check_id_province():
    id_province = request.args.get('id_province')
    province = Province.query.get(id_province)
    if not province:
        return jsonify({'error': 'ID provinsi tidak terdaftar dalam sistem!'})
    return jsonify({'success': 'ID provinsi dapat digunakan!'})

# Route untuk cek ID kota/kabupaten, apakah terdaftar dalam sistem atau tidak
@app.route('/check_id_district', methods=['GET'])
@login_required
def check_id_district():
    id_district = request.args.get('id_district')
    district = District.query.get(id_district)
    if not district:
        return jsonify({'error': 'ID kota/kabupaten tidak terdaftar dalam sistem!'})
    return jsonify({'success': 'ID kota/kabupaten dapat digunakan!'})

# Route untuk cek ID kecamatan, apakah terdaftar dalam sistem atau tidak
@app.route('/check_id_sub_district', methods=['GET'])
@login_required
def check_id_sub_district():
    id_sub_district = request.args.get('id_sub_district')
    sub_district = Sub_District.query.get(id_sub_district)
    if not sub_district:
        return jsonify({'error': 'ID kecamatan tidak terdaftar dalam sistem!'})
    return jsonify({'success': 'ID kecamatan dapat digunakan!'})

# Route untuk cek nama kategori bisnis, apakah sudah terdaftar dalam sistem atau belum
@app.route('/get_business_category', methods=['GET'])
@login_required
def get_business_category():
    id_business_category = request.args.get('id_business_category')
    name = request.args.get('business_category')
    business_category = Business_Category.query.filter(Business_Category.business_category.like(name)).first()
    if not business_category or business_category.id == int(id_business_category):
        return jsonify({'success': 'Nama kategori bisnis dapat digunakan!'})
    else :
        return jsonify({'error': 'Nama kategori bisnis tidak dapat digunakan!'})

# Route untuk cek nama tipe produk, apakah sudah terdaftar dalam sistem atau belum
@app.route('/get_product_type', methods=['GET'])
@login_required
def get_product_type():
    id_product_type = request.args.get('id_product_type')
    name = request.args.get('product_type')
    product_type = Product_Type.query.filter(Product_Type.product_type.like(name)).first()
    if not product_type or product_type.id == int(id_product_type):
        return jsonify({'success': 'Nama tipe produk dapat digunakan!'})
    else :
        return jsonify({'error': 'Nama tipe produk tidak dapat digunakan!'})

# Route untuk cek nama kategori produk, apakah sudah terdaftar dalam sistem atau belum
@app.route('/get_product_category', methods=['GET'])
@login_required
def get_product_category():
    id_product_category = request.args.get('id_product_category')
    name = request.args.get('product_category')
    product_category = Product_Category.query.filter(Product_Category.product_category.like(name)).first()
    if not product_category or product_category.id == int(id_product_category):
        return jsonify({'success': 'Nama kategori produk dapat digunakan!'})
    else :
        return jsonify({'error': 'Nama kategori produk tidak dapat digunakan!'})

# Route untuk mengambil frekuensi unggah excel berdasarkan tahun
@app.route('/get_excel_frequency', methods=['GET'])
@login_required
def get_excel_frequency():
    year = int(request.args.get('year'))
    if year:
        excel_freqs_data = db.session.query(func.month(Excel.updated_at), 
        func.count(Excel.path)).group_by(func.month(Excel.updated_at)).filter(func.year(Excel.updated_at) == year).all()
        excel_freqs = list()
        for i in range(12):
            excel_freqs.append(0)
            for excel_freq_data in excel_freqs_data:
                if excel_freq_data[0] - 1 == i:
                    excel_freqs[i] = excel_freq_data[1]
                    break    
        return jsonify({'frequencies': excel_freqs})

@app.route('/get_business_cat_frequency', methods=['GET'])
@login_required
def get_business_cat_frequency():
    businessc_freqs_data = db.session.query(Business_Category.business_category, func.count(Umkm.id_business_category)).select_from(Umkm).join(Business_Category, 
    Umkm.id_business_category == Business_Category.id).group_by(Umkm.id_business_category).all()
    if businessc_freqs_data:
        businessc_label = list()
        businessc_freqs = list()
        for b in businessc_freqs_data:
            businessc_label.append(b[0])
            businessc_freqs.append(b[1])
        return jsonify({'labels': businessc_label, 'frequencies': businessc_freqs})
    else:
        return jsonify({'labels': 'Kosong', 'frequencies': 1})

# ================================== #
#       ROUTE UNTUK CRUD OWNER       #
# ================================== #

# Route untuk menampilkan data pemilik UMKM (Datatable)
@app.route('/owner')
@login_required
def owner_home():
    return render_template('owner/home_owner.html', title='Data Pemilik UMKM', active='owner')

# Route untuk mengambil data untuk ditampilkan pada tabel (DataTable)
@app.route('/owner/data', methods=['GET'])
@login_required
def owner_data():   
    query = Owner.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(
            Owner.name.like(f'%{search}%')
        )
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['name', 'updated_at']:
            col_name = 'name'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Owner, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [owner.to_table() for owner in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': query.count(),
        'draw': request.args.get('draw', type=int),
    }

# Route untuk menambahkan data pemilik UMKM 
@app.route('/owner/create', methods=['GET', 'POST'])
@login_required
def owner_create():
    form = OwnerForm()

    # Ambil data provinsi untuk mengisi opsi provinsi
    provinces_list = [(0,'- Pilih Provinsi -')]
    for province in Province.query.all():
        provinces_list.append((province.id, province.name))
    form.province.choices = provinces_list
    
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
    return render_template('owner/create_owner.html', title='Tambah Data Pemilik UMKM', previous_page='/owner', form=form, active='owner')

# Route untuk menampilkan detil data pemilik UMKM 
@app.route('/owner/<int:id>', methods=['GET'])
@login_required
def owner_detail(id):
    owner = Owner.query.get_or_404(id)
    form = OwnerForm()

    # Ambil pilihan provinsi
    provinces_list = [(0,'- Pilih Provinsi -')]
    for province in Province.query.all():
        provinces_list.append((province.id, province.name))
    form.province.choices = provinces_list

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
    return render_template('owner/update_owner.html', title='Detil Data Pemilik UMKM', previous_page='/owner', form=form, active='owner', id=id)

# Route untuk mengubah data pemilik UMKM
@app.route('/owner/update', methods=['POST'])
@login_required
def owner_update():
    form = OwnerForm()
    if request.method == 'POST' and form.validate_on_submit():
        owner = Owner.query.get_or_404(form.id_owner.data)
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
        return redirect(request.referrer)
    
# Route untuk menghapus data pemilik UMKM
@app.route('/owner/<int:id>/delete', methods=['POST'])
@login_required
def owner_delete(id):
    owner = Owner.query.get(id)

    # Ambil data UMKM, brand, dan produk yang terhubung dengan pemilik UMKM untuk ikut dihapus
    umkms = Umkm.query.filter_by(id_owner=owner.id).all()
    for umkm in umkms:
        brands = Brand.query.filter_by(id_umkm=umkm.id).all()
        for brand in brands:
            products = Product.query.filter_by(id_brand=brand.id).all()
            for product in products:
                db.session.delete(product)
                db.session.commit()
            db.session.delete(brand)
            db.session.commit()
        db.session.delete(umkm)
        db.session.commit()

    db.session.delete(owner)
    db.session.commit()

    flash('Data pemilik UMKM berhasil dihapus!', 'danger')
    return redirect(url_for('owner_home'))

# ================================== #
#       ROUTE UNTUK CRUD UMKM        #
# ================================== #

# Route untuk menampilkan data UMKM (Datatable)
@app.route('/umkm')
@login_required
def umkm_home():
    return render_template('umkm/home_umkm.html', title='Data UMKM', active='umkm')

# Route untuk mengambil data untuk ditampilkan pada tabel (DataTable)
@app.route('/umkm/data', methods=['GET'])
@login_required
def umkm_data():
    id_owner = request.args.get('id_owner', 0, type=int)
    if id_owner == 0:
        query = Umkm.query

        # search filter
        search = request.args.get('search[value]')
        if search:
            query = query.filter(
                Umkm.name.like(f'%{search}%')
            )
        total_filtered = query.count()

        # sorting
        order = []
        i = 0
        while True:
            col_index = request.args.get(f'order[{i}][column]')
            if col_index is None:
                break
            col_name = request.args.get(f'columns[{col_index}][data]')
            if col_name not in ['name', 'updated_at']:
                col_name = 'name'
            descending = request.args.get(f'order[{i}][dir]') == 'desc'
            col = getattr(District, col_name)
            if descending:
                col = col.desc()
            order.append(col)
            i += 1
        if order:
            query = query.order_by(*order)

        # pagination
        start = request.args.get('start', type=int)
        length = request.args.get('length', type=int)
        query = query.offset(start).limit(length)

        # response
        return {
            'data': [umkm.to_table() for umkm in query],
            'recordsFiltered': total_filtered,
            'recordsTotal': query.count(),
            'draw': request.args.get('draw', type=int),
        }

    query = db.session.query(Umkm).join(Owner, Owner.id == Umkm.id_owner).filter(Umkm.id_owner == id_owner)

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(
            Umkm.name.like(f'%{search}%')
        )
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['name', 'updated_at']:
            col_name = 'name'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Umkm, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [umkm.to_table() for umkm in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': query.count(),
        'draw': request.args.get('draw', type=int),
    }

# Route untuk menambahkan data pemilik UMKM 
@app.route('/umkm/create', methods=['GET', 'POST'])
@login_required
def umkm_create():
    form = UmkmForm()
    
    # Ambil data provinsi untuk mengisi opsi provinsi
    provinces_list = [(0,'- Pilih Provinsi -')]
    for province in Province.query.all():
        provinces_list.append((province.id, province.name))
    form.province.choices = provinces_list
    
    # Ambil data kategori bisnis untuk mengisi opsi kategori bisnis
    business_cats_list = [(0,'- Pilih Kategori Bisnis -')]
    for business_cat in Business_Category.query.all():
        business_cats_list.append((business_cat.id, business_cat.business_category))
    form.business_category.choices = business_cats_list
    
    title = 'Tambah Data UMKM'
    if form.validate_on_submit():
        id_owner = Owner.query.filter_by(nik=form.nik.data).first().id
        umkm = Umkm(
            id_owner = id_owner,
            id_ward = form.ward.data,
            id_business_category = form.business_category.data,
            business_type = form.business_type.data,
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
    return render_template('umkm/create_umkm.html', title=title, form=form, previous_page='/umkm', active='umkm')

# Route untuk menampilkan detil data UMKM
@app.route('/umkm/<int:id>', methods=['GET'])
@login_required
def umkm_detail(id):
    umkm = Umkm.query.get_or_404(id)
    form = UmkmForm()
    
    id_owner = umkm.owner.id

    districts_list = [(i.id, i.name) for i in District.query.filter_by(id_province=umkm.ward.sub_district.district.province.id).all()]
    sub_districts_list = [(i.id, i.name) for i in Sub_District.query.filter_by(id_district=umkm.ward.sub_district.district.id).all()]
    wards_list = [(i.id, i.name) for i in Ward.query.filter_by(id_sub_district=umkm.ward.sub_district.id).all()]
    form.id_umkm.data = umkm.id

    # Ambil pilihan provinsi
    provinces_list = [(0,'- Pilih Provinsi -')]
    for province in Province.query.all():
        provinces_list.append((province.id, province.name))
    form.province.choices = provinces_list
    
    # Ambil data kategori bisnis untuk mengisi opsi kategori bisnis
    business_cats_list = [(0,'- Pilih Kategori Bisnis -')]
    for business_cat in Business_Category.query.all():
        business_cats_list.append((business_cat.id, business_cat.business_category))
    form.business_category.choices = business_cats_list
    
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
    return render_template('umkm/update_umkm.html', title='Detil Data UMKM', previous_page='/umkm',form=form, active='umkm', id_owner=id_owner)

# Route untuk mengubah data UMKM
@app.route('/umkm/update', methods=['POST'])
@login_required
def umkm_update():
    form = UmkmForm()
    if form.validate_on_submit():
        id_owner = Owner.query.filter_by(nik=form.nik.data).first().id
        umkm = Umkm.query.get_or_404(form.id_umkm.data)
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
        return redirect(request.referrer)

# Route untuk menghapus data UMKM
@app.route('/umkm/<int:id>/delete', methods=['POST'])
@login_required
def umkm_delete(id):
    umkm = Umkm.query.get(id)

    # Ambil data brand dan produk yang dimiliki UMKM untuk ikut dihapus
    brands = Brand.query.filter_by(id_umkm=umkm.id).all()
    for brand in brands:
        products = Product.query.filter_by(id_brand=brand.id).all()
        for product in products:
            db.session.delete(product)
            db.session.commit()
        db.session.delete(brand)
        db.session.commit()

    db.session.delete(umkm)
    db.session.commit()
    flash('Data UMKM berhasil dihapus!', 'danger')
    return redirect(request.referrer)

# ================================== #
#       ROUTE UNTUK CRUD BRAND       #
# ================================== #

# Route untuk menampilkan data brand (Datatable)
@app.route('/brand')
@login_required
def brand_home():
    return render_template('/brand/home_brand.html', title='Data Brand', active='brand')

# Route untuk mengambil data brand untuk ditampilkan pada tabel (DataTable)
@app.route('/brand/data', methods=['GET'])
@login_required
def brand_data():
    id_umkm = request.args.get('id_umkm', 0, type=int)
    if id_umkm == 0:
        query = Brand.query

        # search filter
        search = request.args.get('search[value]')
        if search:
            query = query.filter(
                Brand.brand.like(f'%{search}%')
            )
        total_filtered = query.count()

        # sorting
        order = []
        i = 0
        while True:
            col_index = request.args.get(f'order[{i}][column]')
            if col_index is None:
                break
            col_name = request.args.get(f'columns[{col_index}][data]')
            if col_name not in ['name', 'updated_at']:
                col_name = 'name'
            descending = request.args.get(f'order[{i}][dir]') == 'desc'
            col = getattr(Brand, col_name)
            if descending:
                col = col.desc()
            order.append(col)
            i += 1
        if order:
            query = query.order_by(*order)

        # pagination
        start = request.args.get('start', type=int)
        length = request.args.get('length', type=int)
        query = query.offset(start).limit(length)

        # response
        return {
            'data': [brand.to_table() for brand in query],
            'recordsFiltered': total_filtered,
            'recordsTotal': query.count(),
            'draw': request.args.get('draw', type=int),
        }

    query = db.session.query(Brand).join(Umkm, Umkm.id == Brand.id_umkm).filter(Brand.id_umkm == id_umkm)

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(
            Brand.brand.like(f'%{search}%')
        )
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['name', 'updated_at']:
            col_name = 'name'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Brand, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [brand.to_table() for brand in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': query.count(),
        'draw': request.args.get('draw', type=int),
    }

# Route untuk menambahkan data pemilik brand 
@app.route('/brand/create', methods=['GET', 'POST'])
@login_required
def brand_create():
    form = BrandForm()
    title = 'Tambah Data Brand'
    if form.validate_on_submit():
        umkm = Umkm.query.filter(Umkm.name.like(form.umkm.data)).first()
        brand = Brand(
            id_umkm = umkm.id,
            brand = form.brand.data,
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        db.session.add(brand)
        db.session.commit()
        flash('Data brand berhasil ditambahkan!', 'success')
        return redirect(url_for('brand_home'))
    return render_template('brand/create_brand.html', title=title, form=form, previous_page='/brand', active='brand')

# Route untuk menampilkan detil data brand 
@app.route('/brand/<int:id>', methods=['GET', 'POST'])
@login_required
def brand_detail(id):
    brand = Brand.query.get_or_404(id)
    form = BrandForm()

    id_umkm = brand.umkm.id

    form.id_brand.data = brand.id
    form.brand.data = brand.brand
    form.umkm.data = brand.umkm.name
    return render_template('brand/update_brand.html', title='Detil Data Brand', form=form, previous_page='/brand', active='brand', id_umkm=id_umkm)

# Route untuk mengubah data brand
@app.route('/brand/update', methods=['POST'])
@login_required
def brand_update():
    form = BrandForm()
    if form.validate_on_submit():
        brand = Brand.query.get_or_404(form.id_brand.data)
        id_umkm = Umkm.query.filter(Umkm.name.like(form.umkm.data)).first().id
        brand.id_umkm = id_umkm
        brand.brand = form.brand.data
        brand.updated_at = datetime.now()
        db.session.commit()
        flash('Data brand berhasil diubah!', 'success')
        return redirect(request.referrer)
        

# Route untuk menghapus data brand
@app.route('/brand/<int:id>/delete', methods=['POST'])
@login_required
def brand_delete(id):
    brand = Brand.query.get(id)

    # Ambil data produk yang dimiliki brand untuk ikut dihapus
    products = Product.query.filter_by(id_brand=brand.id).all()
    for product in products:
        db.session.delete(product)
        db.session.commit()

    db.session.delete(brand)
    db.session.commit()
    flash('Data brand berhasil dihapus!', 'danger')
    return redirect(request.referrer)

# ================================== #
#       ROUTE UNTUK CRUD PRODUK      #
# ================================== #

# Route untuk menampilkan data product (Datatable)
@app.route('/product')
@login_required
def product_home():
    return render_template('/product/home_product.html', title='Data Produk', active='product')

# Route untuk mengambil data produk untuk ditampilkan pada tabel (DataTable)
@app.route('/product/data', methods=['GET'])
@login_required
def product_data():
    id_brand = request.args.get('id_brand', 0, type=int)
    if id_brand == 0:
        query = Product.query

        # search filter
        search = request.args.get('search[value]')
        if search:
            query = query.filter(
                Product.name.like(f'%{search}%')
            )
        total_filtered = query.count()

        # sorting
        order = []
        i = 0
        while True:
            col_index = request.args.get(f'order[{i}][column]')
            if col_index is None:
                break
            col_name = request.args.get(f'columns[{col_index}][data]')
            if col_name not in ['name', 'updated_at']:
                col_name = 'name'
            descending = request.args.get(f'order[{i}][dir]') == 'desc'
            col = getattr(Product, col_name)
            if descending:
                col = col.desc()
            order.append(col)
            i += 1
        if order:
            query = query.order_by(*order)

        # pagination
        start = request.args.get('start', type=int)
        length = request.args.get('length', type=int)
        query = query.offset(start).limit(length)

        # response
        return {
            'data': [product.to_table() for product in query],
            'recordsFiltered': total_filtered,
            'recordsTotal': query.count(),
            'draw': request.args.get('draw', type=int),
        }

    query = db.session.query(Product).join(Brand, Brand.id == Product.id_brand).filter(Product.id_brand == id_brand)

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(
            Product.name.like(f'%{search}%')
        )
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['name', 'updated_at']:
            col_name = 'name'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Brand, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [brand.to_table() for brand in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': query.count(),
        'draw': request.args.get('draw', type=int),
    }

# Route untuk menambahkan data produk
@app.route('/product/create', methods=['GET', 'POST'])
@login_required
def product_create():
    form = ProductForm()

    # Ambil data tipe produk untuk mengisi opsi tipe produk
    product_types_list = [(0,'- Pilih Tipe Produk -')]
    for product_type in Product_Type.query.all():
        product_types_list.append((product_type.id, product_type.product_type))
    form.product_type.choices = product_types_list

    # Ambil data kategori produk untuk mengisi kategori produk
    product_cats_list = [(0, '- Pilih Kategori Produk -')]
    for product_cat in Product_Category.query.all():
        product_cats_list.append((product_cat.id, product_cat.product_category))
    form.product_category.choices = product_cats_list

    title = 'Tambah Data Produk'
    if form.validate_on_submit():
        id_brand = Brand.query.filter_by(brand=form.brand.data).first().id
        product = Product(
            id_brand = id_brand,
            id_type = form.product_type.data,
            id_category = form.product_category.data,
            name = form.name.data,
            price = form.price.data, 
            price_reseller = form.price_reseller.data,
            variance = form.variance.data,
            size = form.size.data, 
            description = form.description.data,
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        db.session.add(product)
        db.session.commit()
        flash('Data produk berhasil ditambahkan!', 'success')
        return redirect(url_for('product_home'))
    return render_template('product/create_product.html', title=title, form=form, previous_page='/product', active='product')

# Route untuk menampilkan detil data produk 
@app.route('/product/<int:id>', methods=['GET'])
@login_required
def product_detail(id):
    product = Product.query.get_or_404(id)
    form = ProductForm()
    id_brand = product.id_brand

    # Ambil data tipe dan kategori produk
    product_type_list = [(i.id, i.product_type) for i in Product_Type.query.all()]
    product_category_list = [(i.id, i.product_category) for i in Product_Category.query.all()]

    # Masukan data yang telah diambil ke dalam pilihan (select form)
    form.product_type.choices = product_type_list
    form.product_category.choices = product_category_list

    form.id_product.data = product.id
    form.brand.data = product.brand.brand
    form.product_type.data = product.id_type
    form.product_category.data = product.id_category
    form.name.data = product.name
    form.price.data = product.price
    form.price_reseller.data = product.price_reseller
    form.variance.data = product.variance
    form.size.data = product.size
    form.description.data = product.description
    return render_template('product/update_product.html', title='Detil Data Product', form=form, previous_page='/product', active='product', id_brand=id_brand)

# Route untuk mengubah data produk
@app.route('/product/update', methods=['POST'])
@login_required
def product_update():
    form = ProductForm()
    if request.method == 'POST' and form.validate_on_submit():
        product = Product.query.get_or_404(form.id_product.data)
        id_brand = Brand.query.filter_by(brand=form.brand.data).first().id
        product.id_brand = id_brand
        product.id_type = form.product_type.data
        product.id_category = form.product_category.data
        product.name = product.name
        product.price = form.price.data
        product.price_reseller = form.price_reseller.data
        product.variance = form.variance.data
        product.size = form.size.data
        product.description = form.description.data
        product.updated_at = datetime.now()
        db.session.commit()
        flash('Data produk berhasil diubah!', 'success')
        return redirect(request.referrer)

# Route untuk menghapus data produk
@app.route('/product/<int:id>/delete', methods=['POST'])
@login_required
def product_delete(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    flash('Data produk berhasil dihapus!', 'danger')
    return redirect(request.referrer)

# ===================================================== #
#       ROUTE UNTUK UNGGAH DAN UNDUH DATA EXCEL         #
# ===================================================== #

# Fungsi untuk menyimpan data excel
def save_excel(form_excel, path):
    random_name = shortuuid.ShortUUID().random(length=10)
    _, f_ext = os.path.splitext(form_excel.filename)
    excel_fn = random_name + f_ext

    if path == 'all':
        excel_path = os.path.join(app.root_path, 'static/excel/all/', excel_fn)
    elif path == 'owner':
        excel_path = os.path.join(app.root_path, 'static/excel/owner/', excel_fn)
    elif path == 'umkm':
        excel_path = os.path.join(app.root_path, 'static/excel/umkm/', excel_fn)
    elif path == 'brand':
        excel_path = os.path.join(app.root_path, 'static/excel/brand/', excel_fn)
    elif path == 'product':
        excel_path = os.path.join(app.root_path, 'static/excel/product/', excel_fn)

    form_excel.save(excel_path)

    return excel_path

# def is_date(string, fuzzy=False):
#     try: 
#         parser.parse(string, fuzzy=fuzzy)
#         return True

#     except ValueError:
#         return False

@app.route('/excel')
@login_required
def excel_home():
    return render_template('excel/excel_home.html', title='Kelola Data Excel', active='excel_management')

@app.route('/excel/data')
@login_required
def excel_data():
    query = Excel.query.filter(Excel.deleted_at == None)

    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['path', 'updated_at']:
            col_name = 'path'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Excel, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [excel.to_table() for excel in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': query.count(),
        'draw': request.args.get('draw', type=int),
    }

@app.route('/excel/download/delete', methods=['POST'])
@login_required
def excel_delete_download():
    excel_path = os.path.join(app.root_path, 'static/excel/download/*.xlsx')
    files = glob.glob(excel_path)
    for f in files:
        try:
            os.remove(f)
        except OSError as e:
            print("Error: %s : %s" % (f, e.strerror))
    flash(f'Seluruh data unduh excel berhasil dihapus!', 'danger')
    return redirect(url_for('excel_home'))

@app.route('/excel/<int:id>/delete', methods=['POST'])
@login_required
def excel_delete(id):
    excel = Excel.query.get_or_404(id)
    os.remove(excel.path)
    excel.deleted_at = datetime.now()
    db.session.commit()
    flash('Data excel berhasil dihapus!', 'danger')
    return redirect(url_for('excel_home'))

@app.route('/excel/upload/delete', methods=['POST'])
@login_required
def excel_delete_all():
    excels = Excel.query.all()
    for excel in excels:
        os.remove(excel.path)    
        excel.deleted_at = datetime.now()
        db.session.commit()
    flash('Seluruh data excel unggah berhasil dihapus!', 'danger')
    return redirect(url_for('excel_home'))

@app.route('/excel/upload/home', methods=['GET'])
@login_required
def excel_upload_home():
    form = ExcelForm()
    return render_template('excel/excel_upload.html', form=form, title='Unggah Data Excel', active='excel_upload')

# Route untuk unduh format excel
@app.route('/excel/format/<string:format>', methods=['GET'])
@login_required
def excel_format(format):
    excel_path_save = os.path.join(app.root_path, 'static/excel/format/', f'format_{format}.xlsx')
    return send_file(excel_path_save, as_attachment=True)

@app.route('/excel/all', methods=['POST'])
@login_required
def excel_all():
    form = ExcelForm()
    if form.validate_on_submit:
        excel_path = save_excel(form.excel.data, 'all')
        excel_data_full = pe.get_book(file_name=excel_path)
        update = form.update.data
        excel_data = None
        check = None
        if len(excel_data_full) < 4:
            check = 'format column all'
        else:
            for sheet in excel_data_full:
                if sheet.name.upper() not in ['OWNER', 'UMKM', 'BRAND', 'PRODUCT']:
                    check = 'format column all'
                    break

        # Validasi data owner
        if check == None:
            for sheet in excel_data_full:
                if sheet.name.upper() == 'OWNER':
                    sheet_name = sheet.name.upper()
                    excel_data = excel_data_full[sheet.name]
                    break
            column_list = ['NIK', 'Nama', 'Alamat Domisili (KTP)', 'Provinsi', 'Kota/Kabupaten', 
            'Kecamatan', 'Desa', 'Kode Pos', 'Catatan Keanggotaan', 'NPWP']
            if excel_data[0] == column_list and len(excel_data) > 1:
                i = 0
                required_columns = [i for i in range(0, 8)]
                while i < len(column_list) and check == None:
                    j = 1
                    while j < len(excel_data):
                        if i in required_columns and (excel_data[j, i] == None or excel_data[j, i] == ''):
                            check = 'format data'
                            break
                        else:
                            if i == 0:
                                if Owner.query.filter(Owner.nik.like(excel_data[j, i])).first() and not update:
                                    check = 'registered'
                                    break
                                else:
                                    k = 1
                                    while k < len(excel_data):
                                        if k != j and excel_data[k, i] == excel_data[j, i]: 
                                            check = 'duplicate'
                                            break
                                        k += 1
                                    if check != None:
                                        break
                            if i == 3:
                                address_check = False
                                province = Province.query.filter_by(name=excel_data[j, i].upper()).first()
                                if province:
                                    for district in province.district:
                                        if district.name == excel_data[j, i + 1].upper():
                                            address_check = True
                                            district = district
                                            break
                                    if address_check:
                                        address_check = False
                                        for sub_district in district.sub_district:
                                            if sub_district.name == excel_data[j, i + 2].upper():
                                                address_check = True
                                                sub_district = sub_district
                                                break
                                        if address_check:
                                            address_check = False
                                            for ward in sub_district.ward:
                                                if ward.name == excel_data[j, i + 3].upper():
                                                    address_check = True
                                                    break
                                            if not address_check:
                                                i += 3
                                                check = 'unregistered'
                                                break
                                        else:
                                            i += 2
                                            check = 'unregistered'
                                            break
                                    else:
                                        check = 'unregistered'
                                        i += 1
                                        break
                                else:
                                    check = 'unregistered'
                                    break
                        j += 1
                    if check != None:
                        break
                    i += 1
            else:
                if excel_data[0] != column_list:
                    check = 'format column'
                elif len(excel_data) < 2:
                    check = 'format'

            # Validasi data UMKM
            if check == None:
                for sheet in excel_data_full:
                    if sheet.name.upper() == 'UMKM':
                        sheet_name = sheet.name.upper()
                        excel_data = excel_data_full[sheet.name]
                        break
                column_list = ['NIK', 'UMKM', 'Kategori Bisnis', 'Provinsi', 'Kota/Kabupaten', 'Kecamatan', 'Desa', 'Alamat UMKM', 
                'Tanggal Mulai Usaha', 'Modal', 'Jumlah Pekerja', 'Email', 'Facebook', 'Instagram', 'Twitter', 'Marketplace', 'Website', 'Badan Hukum', 'Jenis Bisnis', 'Permasalahan']
                if excel_data[0] == column_list and len(excel_data) > 1:
                    i = 0
                    required_columns = [i for i in range(0, 12)]
                    while i < len(column_list) and check == None:
                        j = 1
                        while j < len(excel_data):
                            if i in required_columns and (excel_data[j, i] == None or excel_data[j, i] == ''):
                                check = 'format data'
                                break
                            else:
                                if i == 0 and not Owner.query.filter_by(nik=excel_data[j, i]).first():
                                    for sheet in excel_data_full:
                                        if sheet.name.upper() == 'OWNER':
                                            excel_check = excel_data_full[sheet.name]
                                            break
                                    k = 1
                                    while k < len(excel_check):
                                        if excel_check[k, 0] == excel_data[j, i]:
                                            break
                                        k += 1
                                    if k == len(excel_check):
                                        check = 'unregistered excel'
                                        break
                                elif i == 1:
                                    if Umkm.query.filter(Umkm.name.like(excel_data[j, i])).first() and not update:
                                        check = 'registered'
                                        break 
                                    else:
                                        k = 1
                                        while k < len(excel_data):
                                            if k != j and excel_data[k, i] == excel_data[j, i]: 
                                                check = 'duplicate'
                                                break
                                            k += 1
                                        if check != None:
                                            break                                    
                                elif i == 2 and not Business_Category.query.filter(Business_Category.business_category.like(excel_data[j, i])).first():
                                    check = 'unregistered'
                                    break
                                elif i == 3:
                                    address_check = False
                                    province = Province.query.filter_by(name=excel_data[j, i].upper()).first()
                                    if province:
                                        for district in province.district:
                                            if district.name == excel_data[j, i + 1].upper():
                                                address_check = True
                                                district = district
                                                break
                                        if address_check:
                                            address_check = False
                                            for sub_district in district.sub_district:
                                                if sub_district.name == excel_data[j, i + 2].upper():
                                                    address_check = True
                                                    sub_district = sub_district
                                                    break
                                            if address_check:
                                                address_check = False
                                                for ward in sub_district.ward:
                                                    if ward.name == excel_data[j, i + 3].upper():
                                                        address_check = True
                                                        break
                                                if not address_check:
                                                    i += 3
                                                    check = 'unregistered'
                                                    break
                                            else:
                                                i += 2
                                                check = 'unregistered'
                                                break
                                        else:
                                            check = 'unregistered'
                                            i += 1
                                            break
                                    else:
                                        check = 'unregistered'
                                        break
                                elif i == 8 and not isinstance((excel_data[j, i]), datetime):
                                    check = 'format data'
                                    break
                                elif i == 9 and (excel_data[j, i] == None or isinstance(excel_data[j, i], str) or not isinstance(float(excel_data[j, i]), float)):
                                    check = 'format data'
                                    break
                                elif i == 10:
                                    if excel_data[j, i] == None or not isinstance(excel_data[j, i], int):
                                        check = 'format data'
                                        break
                                    elif excel_data[j, i] < 1:
                                        check = 'under zero'
                                        break            
                            j += 1
                        if check != None:
                            break
                        i += 1
                else:
                    if excel_data[0] != column_list:
                        check = 'format column'
                    elif len(excel_data) < 2:
                        check = 'format'

            # Validasi data BRAND
            if check == None:
                for sheet in excel_data_full:
                    if sheet.name.upper() == 'BRAND':
                        sheet_name = sheet.name.upper()
                        excel_data = excel_data_full[sheet.name.upper()]
                        break
                column_list = ['UMKM', 'Brand/Merek']
                if excel_data[0] == column_list and len(excel_data) > 1:
                    check = None
                    i = 0
                    required_columns = [i for i in range(0, 2)]
                    while i < len(column_list) and check == None:
                        j = 1
                        while j < len(excel_data):
                            if i in required_columns and (excel_data[j, i] == None or excel_data[j, i] == ''):
                                check = 'format data'
                                break
                            else:
                                if i == 0 and not Umkm.query.filter(Umkm.name.like(excel_data[j, i])).first():
                                    for sheet in excel_data_full:
                                        if sheet.name.upper() == 'UMKM':
                                            sheet_name = sheet.name.upper()
                                            excel_check = excel_data_full[sheet.name.upper()]
                                            break
                                    k = 1
                                    while k < len(excel_check):
                                        if excel_check[k, 1] == excel_data[j, 0]:
                                            break
                                        k += 1
                                    if k == len(excel_check):
                                        check = 'unregistered excel'
                                        break 
                                if i == 1:
                                    if Brand.query.filter(Brand.brand.like(excel_data[j, i])).first() and not update:
                                        check = 'registered'
                                        break
                                    else:  
                                        k = 1
                                        while k < len(excel_data):
                                            if k != j and excel_data[k, i] == excel_data[j, i]: 
                                                check = 'duplicate'
                                                break
                                            k += 1
                                        if check != None:
                                            break                                    
                            j += 1
                        if check != None:
                            break
                        i += 1
                else:
                    if excel_data[0] != column_list:
                        check = 'format column'
                    elif len(excel_data) < 2:
                        check = 'format'

            # Validasi data PRODUK
            if check == None:
                for sheet in excel_data_full:
                    if sheet.name.upper() == 'PRODUCT':
                        excel_data = excel_data_full[sheet.name]
                        sheet_name = sheet.name.upper()
                        break
                column_list = ['Merk/Brand', 'Produk', 'Tipe Produk', 'Kategori Produk', 
                'Harga Jual', 'Harga Reseller', 'Varian', 'Ukuran', 'Keterangan']
                if excel_data[0] == column_list and len(excel_data) > 1:
                    check = None
                    i = 0
                    required_columns = [i for i in range(0, 5)]
                    while i < len(column_list) and check == None:
                        j = 1
                        while j < len(excel_data):
                            if i in required_columns and (excel_data[j, i] == None or excel_data[j, i] == ''):
                                check = 'format data'
                                break
                            else:
                                if i == 0 and not Brand.query.filter_by(brand=excel_data[j, i]).first():
                                    for sheet in excel_data_full:
                                        if sheet.name.upper() == 'BRAND':
                                            excel_check = excel_data_full[sheet.name]
                                            break
                                    k = 1
                                    while k < len(excel_check):
                                        if excel_check[k, 1] == excel_data[j, i]:
                                            break
                                        k += 1
                                    if k == len(excel_check):
                                        check = 'unregistered excel'
                                        break
                                elif i == 2 and not Product_Type.query.filter(Product_Type.product_type.like(excel_data[j, i])).first().id: 
                                    check = 'unregistered'
                                    break
                                elif i == 3 and not Product_Category.query.filter(Product_Category.product_category.like(excel_data[j, i])).first().id: 
                                    check = 'unregistered'
                                    break
                            if i == 4:
                                if excel_data[j, i] == None or not isinstance(excel_data[j, i], int):
                                    check = 'format data'
                                    break
                                elif excel_data[j, i] < 1:
                                    check = 'under zero'
                                    break
                            if i == 5 and excel_data[j, i] != '' and not isinstance(excel_data[j, i], int):
                                check = 'format data'
                                break
                            j += 1
                        if check != None:
                            break
                        i += 1
                else:
                    if excel_data[0] != column_list:
                        check = 'format column'
                    elif len(excel_data) < 2:
                        check = 'format'

            # Input data OWNER ke dalam database
            if check == None:
                for sheet in excel_data_full:
                    if sheet.name.upper() == 'OWNER':
                        excel_data = excel_data_full[sheet.name]
                        break
                updated_owner = list()
                i = 1
                while i < len(excel_data):
                    owner = Owner.query.filter_by(nik=excel_data[i, 0]).first()
                    if owner and update:
                        updated_owner.append(i)
                        id_ward = Ward.query.filter_by(name = excel_data[i, 6].upper()).first().id
                        owner.name = excel_data[i, 1]
                        owner.address = excel_data[i, 2]
                        owner.id_ward = id_ward
                        owner.postal_code = excel_data[i, 7]
                        owner.note = excel_data[i, 8]
                        owner.npwp = excel_data[i, 9]
                        owner.updated_at = datetime.now()
                        db.session.commit()
                    else:    
                        province = Province.query.filter_by(name=excel_data[i, 3].upper()).first()
                        for district in province.district:
                            if district.name == excel_data[i, 4].upper():
                                district = district
                                break
                        for sub_district in district.sub_district:
                            if sub_district.name == excel_data[i, 5].upper():
                                sub_district = sub_district
                                break
                        for ward in sub_district.ward:
                            if ward.name == excel_data[i, 6].upper():
                                id_ward = ward.id
                        owner = Owner(
                            id_ward = id_ward,
                            nik = excel_data[i, 0],
                            name = excel_data[i, 1],
                            address = excel_data[i, 2],
                            postal_code = excel_data[i, 7],
                            note = excel_data[i, 8],
                            npwp = excel_data[i, 9],
                            created_at = datetime.now(),
                            updated_at = datetime.now()
                        )
                        db.session.add(owner)
                        db.session.commit()
                    i += 1
            
            # Input data UMKM ke dalam database
                for sheet in excel_data_full:
                    if sheet.name.upper() == 'UMKM':
                        excel_data = excel_data_full[sheet.name]
                        break
                i = 1
                while i < len(excel_data):
                    id_owner = Owner.query.filter_by(nik=excel_data[i, 0]).first().id
                    id_business_category = Business_Category.query.filter(Business_Category.business_category.like(excel_data[i, 2])).first().id
                    province = Province.query.filter_by(name=excel_data[i, 3].upper()).first()
                    for district in province.district:
                        if district.name == excel_data[i, 4].upper():
                            district = district
                            break
                    for sub_district in district.sub_district:
                        if sub_district.name == excel_data[i, 5].upper():
                            sub_district = sub_district
                            break
                    for ward in sub_district.ward:
                        if ward.name == excel_data[i, 6].upper():
                            id_ward = ward.id
                    umkm = Umkm.query.filter(Umkm.name.like(excel_data[i, 1])).first()
                    if umkm and update:
                        umkm.id_owner = id_owner
                        umkm.id_ward = id_ward
                        umkm.id_business_category = id_business_category
                        umkm.name = excel_data[i, 1],
                        umkm.address = excel_data[i, 6]
                        umkm.start_date = excel_data[i, 8]
                        umkm.modal = excel_data[i, 9]
                        umkm.workers = excel_data[i, 10]
                        umkm.email = excel_data[i, 11]
                        umkm.facebook = excel_data[i, 12]
                        umkm.instagram = excel_data[i, 13]
                        umkm.twitter = excel_data[i, 14]
                        umkm.marketplace = excel_data[i, 15]
                        umkm.website = excel_data[i, 16]
                        umkm.legal_entity = excel_data[i, 17]
                        umkm.business_type = excel_data[i, 18]
                        umkm.problem = excel_data[i, 19]
                        umkm.updated_at = datetime.now()
                    else:
                        umkm = Umkm(
                            id_owner = id_owner,
                            id_ward = id_ward,
                            id_business_category = id_business_category,
                            name = excel_data[i, 1],
                            address = excel_data[i, 6],
                            start_date = excel_data[i, 8],
                            modal = excel_data[i, 9],
                            workers = excel_data[i, 10],
                            email = excel_data[i, 11],
                            facebook = excel_data[i, 12],
                            instagram = excel_data[i, 13],
                            twitter = excel_data[i, 14],
                            marketplace = excel_data[i, 15],
                            website = excel_data[i, 16],
                            legal_entity = excel_data[i, 17],
                            business_type = excel_data[i, 18],
                            problem = excel_data[i, 19],
                            created_at = datetime.now(),
                            updated_at = datetime.now()
                        )
                        db.session.add(umkm)
                    db.session.commit()
                    i += 1            
            
            # Input data BRAND ke dalam database
                for sheet in excel_data_full:
                    if sheet.name.upper() == 'BRAND':
                        excel_data = excel_data_full[sheet.name]
                        break
                i = 1
                while i < len(excel_data):
                    id_umkm = Umkm.query.filter(Umkm.name.like(excel_data[i, 0])).first().id
                    brand = Brand.query.filter(Brand.brand.like(excel_data[i, 1])).first()
                    if brand and update:
                        brand.id_umkm = id_umkm
                        brand.brand = excel_data[i, 1]
                        brand.updated_at = datetime.now()
                    else:
                        brand = Brand(
                            id_umkm = id_umkm,
                            brand = excel_data[i, 1],
                            created_at = datetime.now(),
                            updated_at = datetime.now()
                        )
                        db.session.add(brand)
                    db.session.commit()
                    i += 1
            
            # Input data PRODUCT ke dalam database
                for sheet in excel_data_full:
                    if sheet.name.upper() == 'PRODUCT':
                        excel_data = excel_data_full[sheet.name]
                        break
                i = 1
                while i < len(excel_data):
                    id_brand =  Brand.query.filter(Brand.brand.like(excel_data[i, 0])).first().id
                    id_type = Product_Type.query.filter(Product_Type.product_type.like(excel_data[i, 2])).first().id
                    id_category = Product_Category.query.filter(Product_Category.product_category.like(excel_data[i, 3])).first().id
                    product = Product(
                        id_brand = id_brand,
                        id_type = id_type,
                        id_category = id_category,
                        name = excel_data[i, 1],
                        price = excel_data[i, 4], 
                        price_reseller = excel_data[i, 5],
                        variance = excel_data[i, 6],
                        size = excel_data[i, 7], 
                        description = excel_data[i, 8],
                        created_at = datetime.now(),
                        updated_at = datetime.now()
                    )
                    db.session.add(product)
                    db.session.commit()
                    i += 1            

            # Input data excel
                excel = Excel(
                    id_type = 1,
                    id_user = current_user.id,
                    path = excel_path.replace('\\', '/'),
                    created_at = datetime.now(),
                    updated_at = datetime.now()
                )
                db.session.add(excel)
                db.session.commit()            

        if check != None:
            os.remove(excel_path)
            if check == 'format column all':
                flash(f'Data excel tidak dapat diekstrak! Format kolom file excel tidak sesuai format!', 'danger')
            elif check == 'format column':
                flash(f'Data excel tidak dapat diekstrak! Format kolom file excel (nama atau jumlah) pada sheet {sheet_name} tidak sesuai format!', 'danger')                
            elif check == 'format':
                flash(f'Data excel tidak dapat diekstrak! Tidak terdapat data pada sheet {sheet_name}!', 'danger')
            elif check == 'format data':
                flash(f'Data excel tidak dapat diekstrak! Data pada baris ke-{j} kolom {column_list[i]} sheet {sheet_name} tidak sesuai dengan format pengisian atau masih kosong!', 'danger')
            elif check == 'unregistered':
                flash(f'Data excel tidak dapat diekstrak! Data pada baris ke-{j} kolom {column_list[i]} sheet {sheet_name} tidak terdaftar pada sistem!', 'danger')
            elif check == 'registered':
                flash(f'Data excel tidak dapat diekstrak! Data pada baris ke-{j} kolom {column_list[i]} sheet {sheet_name} telah terdaftar pada sistem!', 'danger')
            elif check == 'registered umkm':
                flash(f'Data excel tidak dapat diekstrak! Data pada baris ke-{j} sheet {sheet_name} dengan NIK {excel_data[j, 0]} dan nama UMKM {excel_data[j, 1]} telah terdaftar pada sistem!', 'danger')
            elif check == 'duplicate':
                flash(f'Data excel tidak dapat diekstrak! Terdapat duplikasi data pada baris ke-{j} dan baris ke-{k} kolom {column_list[i]} sheet {sheet_name}!', 'danger')
            elif check == 'unregistered excel':
                flash(f'Data excel tidak dapat diekstrak! Data pada baris ke-{j} kolom {column_list[i]} sheet {sheet_name} tidak terdaftar pada sistem maupun tertulis pada excel!', 'danger')
            elif check == 'under zero':
                flash(f"Data excel tidak dapat diekstrak! Data pada baris {j} kolom {column_list[i]} harus diisi lebih dari 0!", 'danger')

        else:
            if len(updated_owner) > 0:
                flash(f'Data berhasil diekstrak ke dalam sistem! Dilakukan pembaruan data pada sistem karena adanya kesamaan data pada excel dan sistem!', 'success')             
            else:
                flash('Data excel berhasil diekstrak!', 'success')
    return redirect(url_for('excel_upload_home'))

# Aturan penambahan data owner lewat excel:
# 1. Format file excel (kolom, nama sheet) harus sesuai dengan yang telah ditentukan.
# 2. Kolom NIK, nama, alamat domisili KTP, provinsi, kota/kabupaten, kecamatan, desa, 
#   kode pos harus diisi.
# 3. Data provinsi, kota/kabupaten, kecamatan, desa harus terdaftar pada sistem!
# 4. Tidak boleh ada duplikasi NIK dalam satu file excel (kecuali dinyalakan opsi update data).
# 5. Kesamaan NIK pada excel dengan NIK dalam sistem, maka akan dilakukan pembaruan data yang ada pada sistem
#   sesuai dengan yang ada di excel.
@app.route('/excel/owner', methods=['POST'])
@login_required
def excel_owner():
    form = ExcelForm()
    if form.validate_on_submit:
        excel_path = save_excel(form.excel.data, 'umkm')
        excel_data = pe.get_book(file_name=excel_path)
        update = form.update.data
        sheet_name = None
        for sheet in excel_data:
            if sheet.name.upper() == 'OWNER':
                sheet_name = sheet.name
                break
        if sheet_name != None:
            column_list = ['NIK', 'Nama', 'Alamat Domisili (KTP)', 'Provinsi', 'Kota/Kabupaten', 
            'Kecamatan', 'Desa', 'Kode Pos', 'Catatan Keanggotaan', 'NPWP']
            excel_data = excel_data[sheet_name]
            if excel_data[0] == column_list and len(excel_data) > 1:
                check = None
                i = 0
                required_columns = [i for i in range(0, 8)]
                while i < len(column_list) and check == None:
                    j = 1
                    while j < len(excel_data):
                        if i in required_columns and (excel_data[j, i] == None or excel_data[j, i] == ''):
                            check = 'format'
                            break
                        else:
                            if i == 0:
                                k = 1
                                while k < len(excel_data):
                                    if k != j and excel_data[k, i] == excel_data[j, i]: 
                                        check = 'duplicate'
                                        break
                                    k += 1
                                if check != None:
                                    break
                                elif Owner.query.filter(Owner.nik.like(excel_data[j, i])).first() and not update:
                                    check = 'registered'
                                    break
                            if i == 3:
                                address_check = False
                                province = Province.query.filter_by(name=excel_data[j, i].upper()).first()
                                if province:
                                    for district in province.district:
                                        if district.name == excel_data[j, i + 1].upper():
                                            address_check = True
                                            district = district
                                            break
                                    if address_check:
                                        address_check = False
                                        for sub_district in district.sub_district:
                                            if sub_district.name == excel_data[j, i + 2].upper():
                                                address_check = True
                                                sub_district = sub_district
                                                break
                                        if address_check:
                                            address_check = False
                                            for ward in sub_district.ward:
                                                if ward.name == excel_data[j, i + 3].upper():
                                                    address_check = True
                                                    break
                                            if not address_check:
                                                i += 3
                                                check = 'unregistered'
                                                break
                                        else:
                                            i += 2
                                            check = 'unregistered'
                                            break
                                    else:
                                        check = 'unregistered'
                                        i += 1
                                        break
                                else:
                                    check = 'unregistered'
                                    break
                        j += 1
                    if check != None:
                        break
                    i += 1
                
                if check == None:
                    updated_owner = list()
                    i = 1
                    while i < len(excel_data):
                        owner = Owner.query.filter_by(nik=excel_data[i, 0]).first()
                        if owner and update:
                            id_ward = Ward.query.filter_by(name = excel_data[i, 6].upper()).first().id
                            owner.name = excel_data[i, 1]
                            owner.address = excel_data[i, 2]
                            owner.id_ward = id_ward
                            owner.postal_code = excel_data[i, 7]
                            owner.note = excel_data[i, 8]
                            owner.npwp = excel_data[i, 9]
                            owner.updated_at = datetime.now()
                            updated_owner.append(i)
                            db.session.commit()
                        else:    
                            province = Province.query.filter_by(name=excel_data[i, 3].upper()).first()
                            for district in province.district:
                                if district.name == excel_data[i, 4].upper():
                                    district = district
                                    break
                            for sub_district in district.sub_district:
                                if sub_district.name == excel_data[i, 5].upper():
                                    sub_district = sub_district
                                    break
                            for ward in sub_district.ward:
                                if ward.name == excel_data[i, 6].upper():
                                    id_ward = ward.id
                            owner = Owner(
                                id_ward = id_ward,
                                nik = excel_data[i, 0],
                                name = excel_data[i, 1],
                                address = excel_data[i, 2],
                                postal_code = excel_data[i, 7],
                                note = excel_data[i, 8],
                                npwp = excel_data[i, 9],
                                created_at = datetime.now(),
                                updated_at = datetime.now()
                            )
                            db.session.add(owner)
                            db.session.commit()
                        i += 1
                    excel = Excel(
                        id_type = 2,
                        id_user = current_user.id,
                        path = excel_path.replace('\\', '/'),
                        created_at = datetime.now(),
                        updated_at = datetime.now()
                    )
                    db.session.add(excel)
                    db.session.commit()
                    if update:            
                        flash(f'Data berhasil diekstrak ke dalam sistem! Dilakukan pembaruan data pada sistem karena adanya kesamaan data pada excel dan sistem!', 'success')             
                    else:
                        flash(f'Data excel berhasil di ekstrak!', 'success')
                else:
                    os.remove(excel_path)
                    if check == 'format':
                        flash(f"Data excel  tidak dapat diekstrak! Terdapat data kosong pada baris ke-{j} kolom '{column_list[i]}' atau pengisian tidak sesuai format!", 'danger')
                    elif check == 'unregistered':
                        flash(f"Data excel tidak dapat diekstrak! Data pada baris {j} kolom '{column_list[i]}' tidak terdaftar pada sistem atau masih kosong!", 'danger')
                    elif check == 'registered':
                        flash(f"Data excel tidak dapat diekstrak! Data pada baris {j} kolom '{column_list[i]}' telah terdaftar dalam sistem (NIK harus unik)!", 'danger')
                    elif check == 'duplicate':
                        flash(f'Data excel tidak dapat diekstrak! Terdapat data NIK yang sama pada baris ke-{j} dengan baris ke-{k}', 'danger')
                    else:
                        flash('Data excel tidak dapat diekstrak! Format file excel (kolom) tidak sesuai ketentuan!')
                        # flash(f'Cek! {i} {j} {excel_data[j, i]}', 'success')
            else:
                os.remove(excel_path)
                flash(f'Data excel tidak dapat diekstrak! Format file excel (kolom) tidak sesuai ketentuan atau tidak terdapat satu pun data di bawah kolom!', 'danger')
        else:
            os.remove(excel_path.replace('\\', '/'))
            flash(f'Data excel tidak dapat diekstrak! Nama sheet tidak sesuai ketentuan!', 'danger')
    return redirect(url_for('excel_upload_home'))


# Aturan penambahan data UMKM lewat excel:
# 1. Format file excel (kolom, nama sheet) harus sesuai dengan yang telah ditentukan.
# 2. Kolom NIK, UMKM, kategori bisnis, provinsi, kota/kabupaten, kecamatan, desa, alamat UMKM, tanggal mulai usaha,
#   modal, jumlah pekerja, email harus diisi.
# 3. Data NIK, provinsi, kota/kabupaten, kecamatan, desa, kategori bisnis,  harus terdaftar pada sistem!
# 4. Kesamaan NIK dan nama UMKM pada excel dengan NIK dan nama UMKM dalam sistem, maka akan menggagalkan ekstraksi data
# 5. Format tanggal (tanggal mulai usaha) dan angka (jumlah pekerja -> bilangan bulat, modal -> angka bebas) 
#   harus ditulis dengan benar.
@app.route('/excel/umkm', methods=['POST'])
@login_required
def excel_umkm():
    form = ExcelForm()
    if form.validate_on_submit:
        excel_path = save_excel(form.excel.data, 'umkm')
        excel_data = pe.get_book(file_name=excel_path)
        sheet_name = None
        update = form.update.data
        for sheet in excel_data:
            if sheet.name.upper() == 'UMKM':
                sheet_name = sheet.name
                break
        if sheet_name != None:
            column_list = ['NIK', 'UMKM', 'Kategori Bisnis', 'Provinsi', 'Kota/Kabupaten', 'Kecamatan', 'Desa', 'Alamat UMKM', 
            'Tanggal Mulai Usaha', 'Modal', 'Jumlah Pekerja', 'Email', 'Facebook', 'Instagram', 'Twitter', 'Marketplace', 'Website', 'Badan Hukum', 'Jenis Bisnis', 'Permasalahan']
            excel_data = excel_data[sheet_name]
            if excel_data[0] == column_list and len(excel_data) > 1:
                check = None
                i = 0
                required_columns = [i for i in range(0, 12)]
                while i < len(column_list) and check == None:
                    j = 1
                    while j < len(excel_data):
                        if i in required_columns and (excel_data[j, i] == None or excel_data[j, i] == ''):
                            check = 'format'
                            break
                        else:
                            if i == 0 and not Owner.query.filter_by(nik=excel_data[j, i]).first():
                                check = 'unregistered'
                                break
                            elif i == 1:
                                k = 1
                                while k < len(excel_data):
                                    if k != j and excel_data[k, i] == excel_data[j, i]: 
                                        check = 'duplicate'
                                        break
                                    k += 1
                                if check != None:
                                    break                                    
                                elif Umkm.query.filter(Umkm.name.like(excel_data[j, i])).first() and not update:
                                    check = 'registered'
                                    break 
                            elif i == 2 and not Business_Category.query.filter(Business_Category.business_category.like(excel_data[j, i])).first():
                                check = 'unregistered'
                                break
                            elif i == 3:
                                address_check = False
                                province = Province.query.filter_by(name=excel_data[j, i].upper()).first()
                                if province:
                                    for district in province.district:
                                        if district.name == excel_data[j, i + 1].upper():
                                            address_check = True
                                            district = district
                                            break
                                    if address_check:
                                        address_check = False
                                        for sub_district in district.sub_district:
                                            if sub_district.name == excel_data[j, i + 2].upper():
                                                address_check = True
                                                sub_district = sub_district
                                                break
                                        if address_check:
                                            address_check = False
                                            for ward in sub_district.ward:
                                                if ward.name == excel_data[j, i + 3].upper():
                                                    address_check = True
                                                    break
                                            if not address_check:
                                                i += 3
                                                check = 'unregistered'
                                                break
                                        else:
                                            i += 2
                                            check = 'unregistered'
                                            break
                                    else:
                                        check = 'unregistered'
                                        i += 1
                                        break
                                else:
                                    check = 'unregistered'
                                    break
                            elif i == 8 and not isinstance((excel_data[j, i]), datetime):
                                check = 'format'
                                break
                            elif i == 9:
                                if excel_data[j, i] == None or isinstance(excel_data[j, i], str) or not isinstance(float(excel_data[j, i]), float):
                                    check = 'format'
                                    break
                                elif excel_data[j, i] < 1:
                                    check = 'under zero'
                                    break
                            elif i == 10:
                                if excel_data[j, i] == None or not isinstance(excel_data[j, i], int):
                                    check = 'format'
                                    break
                                elif excel_data[j, i] < 1:
                                    check = 'under zero'
                                    break  
                        j += 1
                    if check != None:
                        break
                    i += 1

                if check == None:
                    i = 1
                    updated_umkm = list()
                    while i < len(excel_data):
                        id_owner = Owner.query.filter_by(nik=excel_data[i, 0]).first().id
                        id_business_category = Business_Category.query.filter_by(business_category=excel_data[i, 2].capitalize()).first().id
                        province = Province.query.filter_by(name=excel_data[i, 3].upper()).first()
                        for district in province.district:
                            if district.name == excel_data[i, 4].upper():
                                district = district
                                break
                        for sub_district in district.sub_district:
                            if sub_district.name == excel_data[i, 5].upper():
                                sub_district = sub_district
                                break
                        for ward in sub_district.ward:
                            if ward.name == excel_data[i, 6].upper():
                                id_ward = ward.id

                        if update and Umkm.query.filter(Umkm.name.like(excel_data[i, 1])).first():
                            umkm = Umkm.query.filter(Umkm.name.like(excel_data[i, 1])).first()
                            umkm.id_owner = id_owner
                            umkm.id_ward = id_ward
                            umkm.id_business_category = id_business_category
                            umkm.name = excel_data[i, 0]
                            umkm.address = excel_data[i, 6]
                            umkm.start_date = excel_data[i, 8]
                            umkm.modal = excel_data[i, 9]
                            umkm.workers = excel_data[i, 10]
                            umkm.email = excel_data[i, 11]
                            umkm.facebook = excel_data[i, 12]
                            umkm.instagram = excel_data[i, 13]
                            umkm.twitter = excel_data[i, 14]
                            umkm.marketplace = excel_data[i, 15]
                            umkm.website = excel_data[i, 16]
                            umkm.legal_entity = excel_data[i, 17]
                            umkm.business_type = excel_data[i, 18]
                            umkm.problem = excel_data[i, 19]
                            umkm.updated_at = datetime.now()
                            updated_umkm.append(i)
                        else:
                            umkm = Umkm(
                                id_owner = id_owner,
                                id_ward = id_ward,
                                id_business_category = id_business_category,
                                name = excel_data[i, 1],
                                address = excel_data[i, 6],
                                start_date = excel_data[i, 8],
                                modal = excel_data[i, 9],
                                workers = excel_data[i, 10],
                                email = excel_data[i, 11],
                                facebook = excel_data[i, 12],
                                instagram = excel_data[i, 13],
                                twitter = excel_data[i, 14],
                                marketplace = excel_data[i, 15],
                                website = excel_data[i, 16],
                                legal_entity = excel_data[i, 17],
                                business_type = excel_data[i, 18],
                                problem = excel_data[i, 19],
                                created_at = datetime.now(),
                                updated_at = datetime.now()
                            )
                            db.session.add(umkm)
                        db.session.commit()
                        i += 1
                    excel = Excel(
                        id_type = 3,
                        id_user = current_user.id,
                        path = excel_path.replace('\\', '/'),
                        created_at = datetime.now(),
                        updated_at = datetime.now()
                    )
                    db.session.add(excel)
                    db.session.commit()
                    if update:
                        flash(f'Data berhasil diekstrak ke dalam sistem! Dilakukan pembaruan data pada sistem karena adanya kesamaan data pada excel dan sistem!', 'success')             
                    else:            
                        flash(f'Data excel berhasil di ekstrak', 'success')
                else:
                    os.remove(excel_path)
                    if check == 'format':
                        flash(f"Data excel tidak dapat diekstrak! Terdapat data kosong pada baris ke-{j} kolom '{column_list[i]}' atau pengisian tidak sesuai format!", 'danger')
                    elif check == 'unregistered':
                        flash(f"Data excel tidak dapat diekstrak! Data pada baris {j} kolom '{column_list[i]}' tidak terdaftar pada sistem atau masih kosong!", 'danger')
                    elif check == 'registered':
                        flash(f"Data excel tidak dapat diekstrak! Data pada baris {j} kolom '{column_list[i]}' telah terdaftar dalam sistem (nama brand harus unik)!", 'danger')
                    elif check == 'duplicate':
                        flash(f'Data excel tidak dapat diekstrak! Terdapat data nama UMKM yang sama pada baris ke-{j} dengan baris ke-{k}', 'danger')                    
                    elif check == 'under zero':
                        flash(f"Data excel tidak dapat diekstrak! Data pada baris {j} kolom '{column_list[i]}' harus diisi lebih dari 0!")
                    else:
                        flash('Data excel tidak dapat diekstrak!')
            else:
                os.remove(excel_path)
                flash(f'Data excel tidak dapat diekstrak! Format file excel (nama kolom) tidak sesuai ketentuan atau tidak terdapat satu pun data di bawah kolom!', 'danger')
        else:
            os.remove(excel_path.replace('\\', '/'))
            flash(f'Data excel tidak dapat diekstrak! Nama sheet tidak sesuai ketentuan!', 'danger')
    return redirect(url_for('excel_upload_home'))

# Aturan penambahan data brand lewat excel:
# 1. Format file excel (kolom, nama sheet) harus sesuai dengan yang telah ditentukan.
# 2. Kolom NIK, nama UMKM, brand/merek tidak boleh kosong.
# 3. Data NIK dan nama UMKM harus terdaftar pada sistem!
# 4. Kesamaan nama brand/merek pada excel dengan nama brand/merek dalam sistem, 
#   maka akan menggagalkan ekstraksi data
# 5. Kesamaan nama brand/merek antara baris satu dengan yang lain dalam satu excel akan
#   menggagalkan ekstraksi data.
@app.route('/excel/brand', methods=['POST'])
@login_required
def excel_brand():
    form = ExcelForm()
    if form.validate_on_submit:
        excel_path = save_excel(form.excel.data, 'brand')
        excel_data = pe.get_book(file_name=excel_path)
        sheet_name = None
        update = form.update.data
        for sheet in excel_data:
            if sheet.name.upper() == 'BRAND':
                sheet_name = sheet.name
                break
        if sheet_name != None:
            column_list = ['UMKM', 'Brand/Merek']
            excel_data = excel_data[sheet_name]
            if excel_data[0] == column_list and len(excel_data) > 1:
                check = None
                i = 0
                required_columns = [i for i in range(0, 2)]
                while i < len(column_list) and check == None:
                    j = 1
                    while j < len(excel_data):
                        if i in required_columns and (excel_data[j, i] == None or excel_data[j, i] == ''):
                            check = 'format'
                            break
                        else:
                            if i == 0 and not Umkm.query.filter(Umkm.name.like(excel_data[j, i])).first():
                                check = 'unregistered'
                                break
                            elif i == 1: 
                                if Brand.query.filter(Brand.brand.like(excel_data[j, i])).first() and not update:
                                    check = 'registered'
                                    break
                                else:
                                    k = 1
                                    while k < len(excel_data):
                                        if k != j and excel_data[k, i] == excel_data[j, i]: 
                                            check = 'duplicate'
                                            break
                                        k += 1
                                    if check != None:
                                        break
                        j += 1
                    if check != None:
                        break
                    i += 1

                if check == None:
                    i = 1
                    updated_brand = list()
                    while i < len(excel_data):
                        if update and Brand.query.filter(Brand.brand.like(excel_data[i, 1])).first():
                            brand = Brand.query.filter(Brand.brand.like(excel_data[i, 1])).first()
                            brand.id_umkm = Umkm.query.filter(Umkm.name.like(excel_data[i, 0])).first().id
                            brand.updated_at = datetime.now()
                            updated_brand.append(i)
                            db.session.commit()
                        else:
                            brand = Brand(
                                id_umkm = Umkm.query.filter(Umkm.name.like(excel_data[i, 0])).first().id,
                                brand = excel_data[i, 1],
                                created_at = datetime.now(),
                                updated_at = datetime.now()
                            )
                        db.session.add(brand)
                        db.session.commit()
                        i += 1
                    excel = Excel(
                        id_type = 4,
                        id_user = current_user.id,
                        path = excel_path.replace('\\', '/'),
                        created_at = datetime.now(),
                        updated_at = datetime.now()
                    )   
                    db.session.add(excel)
                    db.session.commit()
                    if update:         
                        flash(f'Data berhasil diekstrak! Terdapat pembaruan data brand pada sistem karena kesamaan nama brand, baris di excel: {updated_brand}', 'success')
                    else:
                        flash('Data berhasil diekstrak!', 'success')
                else:
                    os.remove(excel_path)
                    if check == 'format':
                        flash(f"File tidak dapat diekstrak! Terdapat data kosong pada baris ke-{j} kolom '{column_list[i]}' atau pengisian tidak sesuai format!", 'danger')
                    elif check == 'unregistered':
                        flash(f"File tidak dapat diekstrak! Data pada baris {j} kolom '{column_list[i]}' tidak terdaftar pada sistem!", 'danger')
                    elif check == 'registered':
                        flash(f"File tidak dapat diekstrak! Data pada baris {j} kolom '{column_list[i]}' telah terdaftar dalam sistem (nama brand harus unik)!", 'danger')
                    elif check == 'duplicate':
                        flash(f'Data excel tidak dapat diekstrak! Terdapat data nama brand yang sama pada baris ke-{j} dengan baris ke-{k}!', 'danger')                    
                    else:
                        flash('File tidak dapat diekstrak! Format file (kolom) tidak sesuai ketentuan!', 'danger')
                        # flash(f'Cek! {i} {j} {excel_data[j, i]}', 'success')
            else:
                os.remove(excel_path)
                flash(f'Format file excel (kolom) tidak sesuai ketentuan!', 'danger')
        else:
            os.remove(excel_path.replace('\\', '/'))
            flash(f'Format file excel (sheet) tidak sesuai ketentuan!', 'danger')
    return redirect(url_for('excel_upload_home'))

# Aturan penambahan data produk lewat excel:
# 1. Format file excel (kolom, nama sheet) harus sesuai dengan yang telah ditentukan.
# 2. Kolom Merk/Brand, Produk, Tipe Produk, Kategori Produk, Harga Jual tidak boleh kosong.
# 3. Data Merk/Brand, Tipe Produk, dan Kategori Produk harus terdaftar pada sistem!
# 4. Kesamaan nama produk pada excel dengan nama produk pada sistem maupun dengan baris lain di excel
#   tidak akan menggagalkan proses ekstraksi data (data produk diperbolehkan redundant/tidak unik).
@app.route('/excel/product', methods=['POST'])
@login_required
def excel_product():
    form = ExcelForm()
    if form.validate_on_submit:
        excel_path = save_excel(form.excel.data, 'product')
        excel_data = pe.get_book(file_name=excel_path)
        sheet_name = None
        for sheet in excel_data:
            if sheet.name.upper() == 'PRODUCT':
                sheet_name = sheet.name
                break
        if sheet_name != None:
            column_list = ['Merk/Brand', 'Produk', 'Tipe Produk', 'Kategori Produk', 
            'Harga Jual', 'Harga Reseller', 'Varian', 'Ukuran', 'Keterangan']
            excel_data = excel_data[sheet_name]
            if excel_data[0] == column_list and len(excel_data) > 1:
                    excel_data = excel_data = pe.get_book(file_name=excel_path)[sheet_name]
                    check = None
                    i = 0
                    required_columns = [i for i in range(0, 5)]
                    while i < len(column_list) and check == None:
                        j = 1
                        while j < len(excel_data):
                            if i in required_columns and (excel_data[j, i] == None or excel_data[j, i] == ''):
                                check = 'format'
                                break
                            else:
                                if i == 0 and not Brand.query.filter(Brand.brand.like(excel_data[j, i])).first():
                                    check = 'unregistered'
                                    break
                                elif i == 2 and not Product_Type.query.filter(Product_Type.product_type.like(excel_data[j, i])).first():
                                    check = 'unregistered'
                                    break
                                elif i == 3 and not Product_Category.query.filter(Product_Category.product_category.like(excel_data[j, i])).first():
                                    check = 'unregistered'
                                    break
                            if i == 4 and (excel_data[j, i] == None or not isinstance(excel_data[j, i], int)):
                                check = 'format'
                                break
                            if i == 5 and excel_data[j, i] != '' and not isinstance(excel_data[j, i], int):
                                check = 'format'
                                break
                            j += 1
                        if check != None:
                            break
                        i += 1

                    if check == None:
                        i = 1
                        while i < len(excel_data):
                            id_brand =  Brand.query.filter(Brand.brand.like(excel_data[i, 0])).first().id
                            id_type = Product_Type.query.filter(Product_Type.product_type.like(excel_data[i, 2])).first().id
                            id_category = Product_Category.query.filter(Product_Category.product_category.like(excel_data[i, 3])).first().id
                            product = Product(
                                id_brand = id_brand,
                                id_type = id_type,
                                id_category = id_category,
                                name = excel_data[i, 1],
                                price = excel_data[i, 4], 
                                price_reseller = excel_data[i, 5],
                                variance = excel_data[i, 6],
                                size = excel_data[i, 7], 
                                description = excel_data[i, 8],
                                created_at = datetime.now(),
                                updated_at = datetime.now()
                            )
                            excel = Excel(
                                id_type = 5,
                                id_user = current_user.id,
                                path = excel_path.replace('\\', '/'),
                                created_at = datetime.now(),
                                updated_at = datetime.now()
                            )
                            db.session.add(product)
                            db.session.add(excel)
                            db.session.commit()
                            i += 1            
                        flash('Data excel berhasil diekstrak!', 'success')
                        
                    else:
                        os.remove(excel_path.replace('\\', '/'))
                        if check == 'format':
                            flash(f"Data excel tidak dapat diekstrak! Terdapat data kosong pada baris ke-{j} kolom '{column_list[i]}' atau pengisian tidak sesuai format!", 'danger')
                        elif check == 'unregistered':
                            flash(f"Data excel tidak dapat diekstrak! Data pada baris {j} kolom '{column_list[i]}' tidak terdaftar pada sistem!", 'danger')
                        else:
                            flash('Data excel tidak dapat diekstrak!')
            else:
                os.remove(excel_path.replace('\\', '/'))
                flash(f'Data excel tidak dapat diekstrak! Format file excel (nama kolom) tidak sesuai ketentuan atau tidak terdapat satu pun data di bawah kolom!', 'danger')
        else:
            os.remove(excel_path.replace('\\', '/'))
            flash(f'Data excel tidak dapat diekstrak! Nama sheet tidak sesuai ketentuan!', 'danger')
    return redirect(url_for('excel_upload_home'))

# Route untuk membuka halaman download excel
@app.route('/excel/download/home')
@login_required
def excel_download_home():
    return render_template('excel/excel_download.html', title='Unduh Excel', active='excel_download')

# Route untuk unduh seluruh data dari sistem dengan format excel
@app.route('/excel/download', methods=['GET'])
@login_required
def excel_download():
    id_download = request.args.get('id_download', 0, type=int)

    if id_download == 0:
        owners = Owner.query.all()
        umkms = Umkm.query.all()
        brands = Brand.query.all()
        products = Product.query.all()

        # Membuat sheet owner
        owner_list = list()
        owner_column = ['NIK', 'Nama', 'Alamat Domisili (KTP)', 'Provinsi', 'Kota/Kabupaten', 
        'Kecamatan', 'Desa', 'Kode Pos', 'Catatan Keanggotaan', 'NPWP']
        owner_list.append(owner_column)
        for owner in owners:
            owner_list.append([
                owner.nik, 
                owner.name, 
                owner.address, 
                owner.ward.sub_district.district.province.name,
                owner.ward.sub_district.district.name,
                owner.ward.sub_district.name,
                owner.ward.name,
                owner.postal_code,
                owner.note,
                owner.npwp
            ])
        
        # Membuat sheet UMKM
        umkm_list = list()
        umkm_column = ['NIK', 'UMKM', 'Kategori Bisnis', 'Provinsi', 'Kota/Kabupaten', 'Kecamatan', 'Desa', 'Alamat UMKM', 'Tanggal Mulai Usaha', 'Modal', 
        'Jumlah Pekerja', 'Email', 'Facebook', 'Instagram', 'Twitter', 'Marketplace', 'Website', 'Badan Hukum', 'Jenis Bisnis', 'Permasalahan']
        umkm_list.append(umkm_column)
        for umkm in umkms:
            umkm_list.append([
            umkm.owner.nik,
            umkm.name,
            umkm.business_category.business_category,
            umkm.ward.sub_district.district.province.name,
            umkm.ward.sub_district.district.name,
            umkm.ward.sub_district.name,
            umkm.ward.name,
            umkm.address,
            umkm.start_date.strftime('%m-%d-%Y'),
            umkm.modal,
            umkm.workers,
            umkm.email,
            umkm.facebook,
            umkm.instagram,
            umkm.twitter,
            umkm.marketplace,
            umkm.website,
            umkm.legal_entity,
            umkm.business_type,
            umkm.problem
            ])
        
        # Membuat sheet brand
        brand_list = list()
        brand_column = ['NIK', 'UMKM', 'Brand/Merek']
        brand_list.append(brand_column)
        for brand in brands:
            brand_list.append([
                brand.umkm.owner.nik,
                brand.umkm.name,
                brand.brand
            ])
        
        # Membuat sheet produk
        product_list = list()
        product_column = ['Merk/Brand', 'Produk', 'Tipe Produk', 'Kategori Produk', 'Harga Jual', 
        'Harga Reseller', 'Varian', 'Ukuran', 'Keterangan']
        product_list.append(product_column)
        for product in products:
            product_list.append([
                product.brand.brand,
                product.name,
                product.product_type.product_type,
                product.product_category.product_category,
                product.price,
                product.price_reseller,
                product.variance,
                product.size,
                product.description
            ])

        # Menggabungkan semua sheet
        content = {
        'PRODUCT': product_list,
        'BRAND': brand_list,
        'UMKM': umkm_list,
        'OWNER': owner_list
        }
        
        book = pe.get_book(bookdict=content)
        book_name = f"DATA_SEMUA_UMKM_{datetime.now().strftime('%d-%m-%Y')}.xlsx"
        excel_path_save = os.path.join(app.root_path, 'static/excel/download/', book_name)
        book.save_as(excel_path_save)

        return send_file(excel_path_save, as_attachment=True)

    elif id_download == 1:
        owners = Owner.query.all()

        # Membuat sheet owner
        owner_list = list()
        owner_column = ['NIK', 'Nama', 'Alamat Domisili (KTP)', 'Provinsi', 'Kota/Kabupaten', 
        'Kecamatan', 'Desa', 'Kode Pos', 'Catatan Keanggotaan', 'NPWP']
        owner_list.append(owner_column)
        for owner in owners:
            owner_list.append([
                owner.nik, 
                owner.name, 
                owner.address, 
                owner.ward.sub_district.district.province.name,
                owner.ward.sub_district.district.name,
                owner.ward.sub_district.name,
                owner.ward.name,
                owner.postal_code,
                owner.note,
                owner.npwp
            ])
        
        content = {'OWNER': owner_list}

        book = pe.get_book(bookdict=content)
        book_name = f"DATA_OWNER_{datetime.now().strftime('%d-%m-%Y')}.xlsx"
        excel_path_save = os.path.join(app.root_path, 'static/excel/download/', book_name)
        book.save_as(excel_path_save)

        return send_file(excel_path_save, as_attachment=True)
    
    elif id_download == 2:
        umkms = Umkm.query.all()

        # Membuat sheet UMKM
        umkm_list = list()
        umkm_column = ['NIK', 'UMKM', 'Kategori Bisnis', 'Provinsi', 'Kota/Kabupaten', 'Kecamatan', 'Desa', 'Alamat UMKM', 'Tanggal Mulai Usaha', 'Modal', 
        'Jumlah Pekerja', 'Email', 'Facebook', 'Instagram', 'Twitter', 'Marketplace', 'Website', 'Badan Hukum', 'Jenis Bisnis', 'Permasalahan']
        umkm_list.append(umkm_column)
        for umkm in umkms:
            umkm_list.append([
            umkm.owner.nik,
            umkm.name,
            umkm.business_category.business_category,
            umkm.ward.sub_district.district.province.name,
            umkm.ward.sub_district.district.name,
            umkm.ward.sub_district.name,
            umkm.ward.name,
            umkm.address,
            umkm.start_date.strftime('%m-%d-%Y'),
            umkm.modal,
            umkm.workers,
            umkm.email,
            umkm.facebook,
            umkm.instagram,
            umkm.twitter,
            umkm.marketplace,
            umkm.website,
            umkm.legal_entity,
            umkm.business_type,
            umkm.problem
            ])

        content = {'UMKM': umkm_list}

        book = pe.get_book(bookdict=content)
        book_name = f"DATA_UMKM_{datetime.now().strftime('%d-%m-%Y')}.xlsx"
        excel_path_save = os.path.join(app.root_path, 'static/excel/download/', book_name)
        book.save_as(excel_path_save)

        return send_file(excel_path_save, as_attachment=True)
    
    elif id_download == 3:
        brands = Brand.query.all()

         # Membuat sheet brand
        brand_list = list()
        brand_column = ['UMKM', 'Brand/Merek']
        brand_list.append(brand_column)
        for brand in brands:
            brand_list.append([
                brand.umkm.name,
                brand.brand
            ])

        content = {'BRAND': brand_list}

        book = pe.get_book(bookdict=content)
        book_name = f"DATA_BRAND_{datetime.now().strftime('%d-%m-%Y')}.xlsx"
        excel_path_save = os.path.join(app.root_path, 'static/excel/download/', book_name)
        book.save_as(excel_path_save)

        return send_file(excel_path_save, as_attachment=True)
    
    elif id_download == 4:
        products = Product.query.all()

        # Membuat sheet produk
        product_list = list()
        product_column = ['Merk/Brand', 'Produk', 'Tipe Produk', 'Kategori Produk', 'Harga Jual', 
        'Harga Reseller', 'Varian', 'Ukuran', 'Keterangan']
        product_list.append(product_column)
        for product in products:
            product_list.append([
                product.brand.brand,
                product.name,
                product.product_type.product_type,
                product.product_category.product_category,
                product.price,
                product.price_reseller,
                product.variance,
                product.size,
                product.description
            ])
        
        content = {'PRODUCT': product_list}

        book = pe.get_book(bookdict=content)
        book_name = f"DATA_PRODUCT_{datetime.now().strftime('%d-%m-%Y')}.xlsx"
        excel_path_save = os.path.join(app.root_path, 'static/excel/download/', book_name)
        book.save_as(excel_path_save)

        return send_file(excel_path_save, as_attachment=True)

# =================================== #
#       ROUTE SETTING PROVINSI        #
# =================================== #

# Route untuk menampilkan data provinsi(Datatable)
@app.route('/province')
@login_required
def province_home():
    return render_template('settings/province/home_province.html', title='Data Provinsi', active='location')

# Route untuk mengambil data provinsi untuk ditampilkan pada tabel (DataTable)
@app.route('/province/data', methods=['GET'])
@login_required
def province_data():
    query = Province.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(
            Province.name.like(f'%{search}%')
        )
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['name', 'updated_at']:
            col_name = 'name'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Province, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [province.to_table() for province in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': query.count(),
        'draw': request.args.get('draw', type=int),
    }

# Route untuk menambahkan data provinsi
@app.route('/province/create', methods=['GET', 'POST'])
@login_required
def province_create():
    form = ProvinceForm()
    title = 'Tambah Data Provinsi'
    if form.validate_on_submit():
        province = Province(
            name = form.name.data.upper(),
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        db.session.add(province)
        db.session.commit()
        flash('Data provinsi berhasil ditambahkan!', 'success')
        return redirect(url_for('province_home'))
    return render_template('/settings/province/create_province.html', title=title, form=form, active='location')

# Route untuk menampilkan detil data provinsi
@app.route('/province/<int:id>', methods=['GET'])
@login_required
def province_detail(id):
    form = ProvinceForm()
    province = Province.query.get_or_404(id)
    form.id_province.data = province.id
    form.name.data = province.name
    return render_template('settings/province/update_province.html', title='Detil Data Provinsi', form=form, previous_page='/province', active='location')

# Route untuk mengubah data provinsi
@app.route('/province/update', methods=['POST'])
@login_required
def province_update():
    form = ProvinceForm()
    if form.validate_on_submit():
        province = Province.query.get_or_404(form.id_province.data)
        province.name = form.name.data.upper()
        province.updated_at = datetime.now()
        db.session.commit()
        flash('Data provinsi berhasil diubah!', 'success')
        return redirect(request.referrer)

# Route untuk menghapus data provinsi
@app.route('/province/<int:id>/delete', methods=['POST'])
@login_required
def province_delete(id):
    province = Province.query.get(id)

    # Ambil data kota/kabupaten, kecamatan, desa, pemilik UMKM, dan UMKM untuk dihapus
    districts = District.query.filter_by(id_province=province.id).all()
    for district in districts:
        sub_districts = Sub_District.query.filter_by(id_district=district.id).all()
        for sub_district in sub_districts:
            wards = Ward.query.filter_by(id_sub_district=sub_district.id).all()
            for ward in wards:
                # Hapus data pemilik UMKM secara terpisah
                owners = Owner.query.filter_by(id_ward=ward.id).all()
                for owner in owners:
                    umkms = Umkm.query.filter_by(id_owner=owner.id).all()
                    for umkm in umkms:
                        brands = Brand.query.filter_by(id_umkm=umkm.id).all()
                        for brand in brands:
                            products = Product.query.filter_by(id_brand=brand.id).all()
                            for product in products:
                                db.session.delete(product)
                                db.session.commit()
                            db.session.delete(brand)
                            db.session.commit()
                        db.session.delete(umkm)
                        db.session.commit()
                    db.session.delete(owner)
                    db.session.commit()
                # Hapus data UMKM secara terpisah
                umkms = Umkm.query.filter_by(id_ward=ward.id).all()
                for umkm in umkms:
                    brands = Brand.query.filter_by(id_umkm=umkm.id).all()
                    for brand in brands:
                        products = Product.query.filter_by(id_brand=brand.id).all()
                        for product in products:
                            db.session.delete(product)
                            db.session.commit()
                        db.session.delete(brand)
                        db.session.commit()
                    db.session.delete(umkm)
                    db.session.commit()
                db.session.delete(ward)
                db.session.commit()
            db.session.delete(sub_district)
            db.session.commit()
        db.session.delete(district)
        db.session.commit()

    db.session.delete(province)
    db.session.commit()

    flash('Data provinsi berhasil dihapus!', 'danger')
    return redirect(url_for('province_home'))

# ========================================= #
#       ROUTE SETTING KOTA/KABUPATEN        #
# ========================================= #

# Route untuk menampilkan data kota/kabupaten (Datatable)
@app.route('/district')
@login_required
def district_home():
    return render_template('settings/district/home_district.html', title='Data Kota/Kabupaten', active='location')

# Route untuk mengambil data kota/kabupaten untuk ditampilkan pada tabel (DataTable)
@app.route('/district/data', methods=['GET'])
@login_required
def district_data():
    query = District.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(
            District.name.like(f'%{search}%')
        )
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['name', 'updated_at']:
            col_name = 'name'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(District, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [district.to_table() for district in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': query.count(),
        'draw': request.args.get('draw', type=int),
    }

# Route untuk menambahkan data kota/kabupaten
@app.route('/district/create', methods=['GET', 'POST'])
@login_required
def district_create():
    form = DistrictForm()
    title = 'Tambah Data Kota/Kabupaten'
    if form.validate_on_submit():
        id_province = Province.query.get_or_404(form.id_province.data).id
        district = District(
            id_province = id_province,
            name = form.name.data.upper(),
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        db.session.add(district)
        db.session.commit()
        flash('Data kota/kabupaten berhasil ditambahkan!', 'success')
        return redirect(url_for('district_home'))
    return render_template('/settings/district/create_district.html', title=title, previous_page='/district', form=form, active='location')

# Route untuk menampilkan detil data kota/kabupaten
@app.route('/district/<int:id>', methods=['GET'])
@login_required
def district_detail(id):
    form = DistrictForm()
    district = District.query.get_or_404(id)
    form.id_district.data = district.id
    form.id_province.data = district.province.id
    form.name.data = district.name
    return render_template('settings/district/update_district.html', title='Detil Data Kota/Kabupaten', form=form, previous_page='/district', id_district=district.id, active='location')

# Route untuk mengubah data kota/kabupaten
@app.route('/district/update', methods=['POST'])
@login_required
def district_update():
    form = DistrictForm()
    if form.validate_on_submit():
        district = District.query.get_or_404(form.id_district.data)
        district.id_province = form.id_province.data
        district.name = form.name.data.upper()
        district.updated_at = datetime.now()
        db.session.commit()
        flash('Data kota/kabupaten berhasil diubah!', 'success')
        return redirect(request.referrer)

# Route untuk menghapus data kota/kabupaten
@app.route('/district/<int:id>/delete', methods=['POST'])
@login_required
def district_delete(id):
    district = District.query.get_or_404(id)

    # Ambil data kota/kabupaten, kecamatan, desa, pemilik UMKM, dan UMKM untuk dihapus
    sub_districts = Sub_District.query.filter_by(id_district=district.id).all()
    for sub_district in sub_districts:
        wards = Ward.query.filter_by(id_sub_district=sub_district.id).all()
        for ward in wards:
            # Hapus data pemilik UMKM secara terpisah
            owners = Owner.query.filter_by(id_ward=ward.id).all()
            for owner in owners:
                umkms = Umkm.query.filter_by(id_owner=owner.id).all()
                for umkm in umkms:
                    brands = Brand.query.filter_by(id_umkm=umkm.id).all()
                    for brand in brands:
                        products = Product.query.filter_by(id_brand=brand.id).all()
                        for product in products:
                            db.session.delete(product)
                            db.session.commit()
                        db.session.delete(brand)
                        db.session.commit()
                    db.session.delete(umkm)
                    db.session.commit()
                db.session.delete(owner)
                db.session.commit()
            # Hapus data UMKM secara terpisah
            umkms = Umkm.query.filter_by(id_ward=ward.id).all()
            for umkm in umkms:
                brands = Brand.query.filter_by(id_umkm=umkm.id).all()
                for brand in brands:
                    products = Product.query.filter_by(id_brand=brand.id).all()
                    for product in products:
                        db.session.delete(product)
                        db.session.commit()
                    db.session.delete(brand)
                    db.session.commit()
                db.session.delete(umkm)
                db.session.commit()
            db.session.delete(ward)
            db.session.commit()
        db.session.delete(sub_district)
        db.session.commit()

    db.session.delete(district)
    db.session.commit()

    flash('Data kota/kabupaten berhasil dihapus!', 'danger')
    return redirect(url_for('district_home'))

# ==================================== #
#       ROUTE SETTING KECAMATAN        #
# ==================================== #

# Route untuk menampilkan data kecamatan (Datatable)
@app.route('/sub_district')
@login_required
def sub_district_home():
    return render_template('settings/sub_district/home_sub_district.html', title='Data Kecamatan', active='location')

# Route untuk mengambil data kecamatan untuk ditampilkan pada tabel (DataTable)
@app.route('/sub_district/data', methods=['GET'])
@login_required
def sub_district_data():
    query = Sub_District.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(
            Sub_District.name.like(f'%{search}%')
        )
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['name', 'updated_at']:
            col_name = 'name'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Sub_District, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [sub_district.to_table() for sub_district in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': query.count(),
        'draw': request.args.get('draw', type=int),
    }

# Route untuk menambahkan data kecamatan
@app.route('/sub_district/create', methods=['GET', 'POST'])
@login_required
def sub_district_create():
    form = SubDistrictForm()
    title = 'Tambah Data Kecamatan'
    if form.validate_on_submit():
        id_district = District.query.get_or_404(form.id_district.data).id
        sub_district = Sub_District(
            id_district = id_district,
            name = form.name.data.upper(),
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        db.session.add(sub_district)
        db.session.commit()
        flash('Data kecamatan berhasil ditambahkan!', 'success')
        return redirect(url_for('sub_district_home'))
    return render_template('/settings/sub_district/create_sub_district.html', title=title, previous_page='/sub_district', form=form, active='location')

# Route untuk menampilkan detil data kecamatan
@app.route('/sub_district/<int:id>', methods=['GET'])
@login_required
def sub_district_detail(id):
    form = SubDistrictForm()
    sub_district = Sub_District.query.get_or_404(id)
    form.id_district.data = sub_district.district.id
    form.id_sub_district.data = sub_district.id
    form.name.data = sub_district.name
    return render_template('settings/sub_district/update_sub_district.html', title='Detil Data Kecamatan', form=form, previous_page='/sub_district', active='location')

# Route untuk mengubah data kecamatan
@app.route('/sub_district/update', methods=['POST'])
@login_required
def sub_district_update():
    form = SubDistrictForm()
    if form.validate_on_submit():
        sub_district = Sub_District.query.get_or_404(form.id_sub_district.data)
        sub_district.id_district = form.id_district.data
        sub_district.name = form.name.data.upper()
        sub_district.updated_at = datetime.now()
        db.session.commit()
        flash('Data kecamatan berhasil diubah!', 'success')
        return redirect(request.referrer)

# Route untuk menghapus data kecamatan
@app.route('/sub_district/<int:id>/delete', methods=['POST'])
@login_required
def sub_district_delete(id):
    sub_district = Sub_District.query.get_or_404(id)

    # Ambil data desa, pemilik UMKM, dan UMKM untuk ikut dihapus
    wards = Ward.query.filter_by(id_sub_district=sub_district.id).all()
    for ward in wards:
        # Hapus data pemilik UMKM secara terpisah
        owners = Owner.query.filter_by(id_ward=ward.id).all()
        for owner in owners:
            umkms = Umkm.query.filter_by(id_owner=owner.id).all()
            for umkm in umkms:
                brands = Brand.query.filter_by(id_umkm=umkm.id).all()
                for brand in brands:
                    products = Product.query.filter_by(id_brand=brand.id).all()
                    for product in products:
                        db.session.delete(product)
                        db.session.commit()
                    db.session.delete(brand)
                    db.session.commit()
                db.session.delete(umkm)
                db.session.commit()
            db.session.delete(owner)
            db.session.commit()
        # Hapus data UMKM secara terpisah
        umkms = Umkm.query.filter_by(id_ward=ward.id).all()
        for umkm in umkms:
            brands = Brand.query.filter_by(id_umkm=umkm.id).all()
            for brand in brands:
                products = Product.query.filter_by(id_brand=brand.id).all()
                for product in products:
                    db.session.delete(product)
                    db.session.commit()
                db.session.delete(brand)
                db.session.commit()
            db.session.delete(umkm)
            db.session.commit()
        db.session.delete(ward)
        db.session.commit()
    db.session.delete(sub_district)
    db.session.commit()
    flash('Data kecamatan berhasil dihapus!', 'danger')
    return redirect(url_for('sub_district_home'))

# ================================= #
#       ROUTE SETTING DESA          #
# ================================= #

# Route untuk menampilkan data desa (Datatable)
@app.route('/ward')
@login_required
def ward_home():
    return render_template('settings/ward/home_ward.html', title='Data Desa', active='location')

# Route untuk mengambil data desa untuk ditampilkan pada tabel (DataTable)
@app.route('/ward/data', methods=['GET'])
@login_required
def ward_data():
    query = Ward.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(
            Ward.name.like(f'%{search}%')
        )
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['name', 'updated_at']:
            col_name = 'name'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Ward, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [ward.to_table() for ward in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': query.count(),
        'draw': request.args.get('draw', type=int),
    }

# Route untuk menambahkan data desa
@app.route('/ward/create', methods=['GET', 'POST'])
@login_required
def ward_create():
    form = WardForm()
    title = 'Tambah Data Desa'
    if form.validate_on_submit():
        id_sub_district = Sub_District.query.get_or_404(form.id_sub_district.data).id
        ward = Ward(
            id_sub_district = id_sub_district,
            name = form.name.data.upper(),
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        db.session.add(ward)
        db.session.commit()
        flash('Data desa berhasil ditambahkan!', 'success')
        return redirect(url_for('ward_home'))
    return render_template('/settings/ward/create_ward.html', title=title, previous_page='/ward', form=form, active='location')

# Route untuk menampilkan detil data desa
@app.route('/ward/<int:id>', methods=['GET'])
@login_required
def ward_detail(id):
    form = WardForm()
    ward = Ward.query.get_or_404(id)
    form.id_sub_district.data = ward.sub_district.id
    form.id_ward.data = ward.id
    form.name.data = ward.name
    return render_template('settings/ward/update_ward.html', title='Detil Data Desa', form=form, previous_page='/ward', active='location')

# Route untuk mengubah data desa
@app.route('/ward/update', methods=['POST'])
@login_required
def ward_update():
    form = WardForm()
    if form.validate_on_submit():
        ward = Ward.query.get_or_404(form.id_ward.data)
        ward.id_sub_district = form.id_sub_district.data
        ward.name = form.name.data.upper()
        ward.updated_at = datetime.now()
        db.session.commit()
        flash('Data desa berhasil diubah!', 'success')
        return redirect(request.referrer)

# Route untuk menghapus data desa
@app.route('/ward/<int:id>/delete', methods=['POST'])
@login_required
def ward_delete(id):
    ward = Ward.query.get_or_404(id)

    # Hapus data pemilik UMKM secara terpisah
    owners = Owner.query.filter_by(id_ward=ward.id).all()
    for owner in owners:
        umkms = Umkm.query.filter_by(id_owner=owner.id).all()
        for umkm in umkms:
            brands = Brand.query.filter_by(id_umkm=umkm.id).all()
            for brand in brands:
                products = Product.query.filter_by(id_brand=brand.id).all()
                for product in products:
                    db.session.delete(product)
                    db.session.commit()
                db.session.delete(brand)
                db.session.commit()
            db.session.delete(umkm)
            db.session.commit()
        db.session.delete(owner)
        db.session.commit()
    # Hapus data UMKM secara terpisah
    umkms = Umkm.query.filter_by(id_ward=ward.id).all()
    for umkm in umkms:
        brands = Brand.query.filter_by(id_umkm=umkm.id).all()
        for brand in brands:
            products = Product.query.filter_by(id_brand=brand.id).all()
            for product in products:
                db.session.delete(product)
                db.session.commit()
            db.session.delete(brand)
            db.session.commit()
        db.session.delete(umkm)
        db.session.commit()
    db.session.delete(ward)
    db.session.commit()

    flash('Data desa berhasil dihapus!', 'danger')
    return redirect(url_for('ward_home'))

# ======================================= #
#       ROUTE SETTING KATEGORI BISNIS     #
# ======================================= #

# Route untuk menampilkan data kategori bisnis (Datatable)
@app.route('/business_category')
@login_required
def business_category_home():
    return render_template('settings/business_category/home_business_category.html', title='Data Kategori Bisnis', active='business_category')

# Route untuk mengambil data kategori bisnis untuk ditampilkan pada tabel (DataTable)
@app.route('/business_category/data', methods=['GET'])
@login_required
def business_category_data():
    query = Business_Category.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(
            Business_Category.business_category.like(f'%{search}%')
        )
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['business_category', 'updated_at']:
            col_name = 'business_category'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Business_Category, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [business_cat.to_table() for business_cat in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': query.count(),
        'draw': request.args.get('draw', type=int),
    }

# Route untuk menambahkan data kategori bisnis
@app.route('/business_category/create', methods=['GET', 'POST'])
@login_required
def business_category_create():
    form = BusinessCategoryForm()
    title = 'Tambah Data Kategori Bisnis'
    if form.validate_on_submit():
        business_category = Business_Category(
            business_category = form.business_category.data.upper(),
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        db.session.add(business_category)
        db.session.commit()
        flash('Data kategori bisnis berhasil ditambahkan!', 'success')
        return redirect(url_for('business_category_home'))
    return render_template('/settings/business_category/create_business_category.html', title=title, previous_page='/business_category', form=form, active='business_category')

# Route untuk menampilkan detil data kategori bisnis
@app.route('/business_category/<int:id>', methods=['GET'])
@login_required
def business_category_detail(id):
    form = BusinessCategoryForm()
    business_category = Business_Category.query.get_or_404(id)
    form.id_business_category.data = business_category.id
    form.business_category.data = business_category.business_category
    return render_template('settings/business_category/update_business_category.html', title='Detil Data Kategori Bisnis', form=form, previous_page='/business_category', active='business_category')

# Route untuk mengubah data kategori bisnis
@app.route('/business_category/update', methods=['POST'])
@login_required
def business_category_update():
    form = BusinessCategoryForm()
    if form.validate_on_submit():
        business_category = Business_Category.query.get_or_404(form.id_business_category.data)
        business_category.business_category = form.business_category.data.upper()
        business_category.updated_at = datetime.now()
        db.session.commit()
        flash('Data kategori bisnis berhasil diubah!', 'success')
        return redirect(request.referrer)

# Route untuk menghapus data kategori bisnis
@app.route('/business_category/<int:id>/delete', methods=['POST'])
@login_required
def business_category_delete(id):
    business_category = Business_Category.query.get_or_404(id)

    # Ambil data UMKM untuk ikut dihapus
    umkms = Umkm.query.filter_by(id_business_category=business_category.id).all()
    for umkm in umkms:
        brands = Brand.query.filter_by(id_umkm=umkm.id).all()
        for brand in brands:
            products = Product.query.filter_by(id_brand=brand.id).all()
            for product in products:
                db.session.delete(product)
                db.session.commit()
            db.session.delete(brand)
            db.session.commit()
        db.session.delete(umkm)
        db.session.commit()

    db.session.delete(business_category)
    db.session.commit()
    flash('Data kategori bisnis berhasil dihapus!', 'danger')
    return redirect(url_for('business_category_home'))

# ======================================= #
#       ROUTE SETTING TIPE PRODUK         #
# ======================================= #

# Route untuk menampilkan data tipe produk (Datatable)
@app.route('/product_type')
@login_required
def product_type_home():
    return render_template('settings/product_type/home_product_type.html', title='Data Tipe Produk', active='product_input')

# Route untuk mengambil data tipe produk untuk ditampilkan pada tabel (DataTable)
@app.route('/product_type/data', methods=['GET'])
@login_required
def product_type_data():
    query = Product_Type.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(
            Product_Type.product_type.like(f'%{search}%')
        )
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['product_type', 'updated_at']:
            col_name = 'product_type'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Product_Type, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [product_type.to_table() for product_type in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': query.count(),
        'draw': request.args.get('draw', type=int),
    }

# Route untuk menambahkan data tipe produk
@app.route('/product_type/create', methods=['GET', 'POST'])
@login_required
def product_type_create():
    form = ProductTypeForm()
    title = 'Tambah Data Tipe Produk'
    if form.validate_on_submit():
        product_type = Product_Type(
            product_type = form.product_type.data.upper(),
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        db.session.add(product_type)
        db.session.commit()
        flash('Data tipe produk berhasil ditambahkan!', 'success')
        return redirect(url_for('product_type_home'))
    return render_template('/settings/product_type/create_product_type.html', title=title, previous_page='/product_type', form=form, active='product_input')

# Route untuk menampilkan detil data kategori bisnis
@app.route('/product_type/<int:id>', methods=['GET'])
@login_required
def product_type_detail(id):
    form = ProductTypeForm()
    product_type = Product_Type.query.get_or_404(id)
    form.id_product_type.data = product_type.id
    form.product_type.data = product_type.product_type
    return render_template('settings/product_type/update_product_type.html', title='Detil Data Tipe Produk', form=form, previous_page='/product_type', active='product_input')

# Route untuk mengubah data tipe produk
@app.route('/product_type/<int:id>/update', methods=['POST'])
@login_required
def product_type_update(id):
    form = ProductTypeForm()
    if form.validate_on_submit:
        product_type = Product_Type.query.get_or_404(id)
        product_type.product_type = form.product_type.data.upper()
        product_type.updated_at = datetime.now()
        db.session.commit()
        flash('Data tipe produk berhasil diubah!', 'success')
        return redirect(request.referrer)

# Route untuk menghapus tipe produk
@app.route('/product_type/<int:id>/delete', methods=['POST'])
@login_required
def product_type_delete(id):
    product_type = Product_Type.query.get_or_404(id)

    # Ambil data produk untuk ikut dihapus
    products = Product.query.filter_by(id_type=product_type.id).all()
    for product in products:
        db.session.delete(product)
        db.session.commit()

    db.session.delete(product_type)
    db.session.commit()
    flash('Data kategori tipe produk berhasil dihapus!', 'danger')
    return redirect(url_for('product_type_home'))

# =========================================== #
#       ROUTE SETTING KATEGORI PRODUK         #
# =========================================== #

# Route untuk menampilkan data kategori produk (Datatable)
@app.route('/product_category')
@login_required
def product_category_home():
    return render_template('settings/product_category/home_product_category.html', title='Data Kategori Produk', active='product_input')

# Route untuk mengambil data tipe produk untuk ditampilkan pada tabel (DataTable)
@app.route('/product_category/data', methods=['GET'])
@login_required
def product_category_data():
    query = Product_Category.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(
            Product_Category.product_category.like(f'%{search}%')
        )
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['product_category', 'updated_at']:
            col_name = 'product_category'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Product_Category, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [product_type.to_table() for product_type in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': query.count(),
        'draw': request.args.get('draw', type=int),
    }

# Route untuk menambahkan data kategori produk
@app.route('/product_category/create', methods=['GET', 'POST'])
@login_required
def product_category_create():
    form = ProductCategoryForm()
    title = 'Tambah Data Kategori Produk'
    if form.validate_on_submit():
        product_category = Product_Category(
            product_category = form.product_category.data.upper(),
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        db.session.add(product_category)
        db.session.commit()
        flash('Data kategori produk berhasil ditambahkan!', 'success')
        return redirect(url_for('product_category_home'))
    return render_template('/settings/product_category/create_product_category.html', title=title, previous_page='/product_category', form=form, active='product_input')

# Route untuk menampilkan detil data kategori bisnis
@app.route('/product_category/<int:id>', methods=['GET'])
@login_required
def product_category_detail(id):
    form = ProductCategoryForm()
    product_category = Product_Category.query.get_or_404(id)
    form.id_product_category.data = product_category.id
    form.product_category.data = product_category.product_category
    return render_template('settings/product_category/update_product_category.html', title='Detil Data Kategori Produk', form=form, previous_page='/product_category', active='product_input')

# Route untuk mengubah data kategori produk
@app.route('/product_category/<int:id>/update', methods=['POST'])
@login_required
def product_category_update(id):
    form = ProductCategoryForm()
    if form.validate_on_submit:
        product_category = Product_Category.query.get_or_404(id)
        product_category.product_category = form.product_category.data.upper()
        product_category.updated_at = datetime.now()
        db.session.commit()
        flash('Data kategori produk berhasil diubah!', 'success')
        return redirect(request.referrer)
    
# Route untuk menghapus kategori produk
@app.route('/product_category/<int:id>/delete', methods=['POST'])
@login_required
def product_category_delete(id):
    product_category = Product_Category.query.get_or_404(id)

    # Ambil data produk untuk ikut dihapus
    products = Product.query.filter_by(id_category=product_category.id).all()
    for product in products:
        db.session.delete(product)
        db.session.commit()

    db.session.delete(product_category)
    db.session.commit()
    flash('Data kategori produk berhasil dihapus!', 'danger')
    return redirect(url_for('product_category_home'))

