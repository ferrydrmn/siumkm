$(document).ready(function () {
    // Cek input NIK dan kategori bisnis ketkika loading halaman telah selesai dilakukan
    // Digunakan untuk menentukan tombol submit disabled atau tidak
    jQuery(window).on('load', function () {
        $("#submit").removeAttr('disabled');
        let nik = $('#nik').val();
        let business_cat = $('#business_category').val();
        let ward = $('#ward').val();
        let address = $('#address').val();
        let start_date = $('#start_date').val();
        let modal = $('#modal').val();
        let workers = $('#workers').val();
        let email = $('#email').val();
        if (!nik || business_cat == 0 || !ward || !address || !modal || !workers || !email || !start_date) {
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $("#submit").removeAttr('disabled'); //enable.
        }
    });

    // Cek NIK (Apakah sudah terdaftar di sistem?)
    $('#nik').change(function () {
        let nik = $('#nik').val();
        let name = $('#name').val();
        let business_cat = $('#business_category').val();
        let ward = $('#ward').val();
        let address = $('#address').val();
        let start_date = $('#start_date').val();
        let modal = $('#modal').val();
        let workers = $('#workers').val();
        let email = $('#email').val();
        $('.nik-errors').empty();
        $('.nik-errors').remove();
        if (!nik) {
            $('#nik').removeClass('is-valid')
            $('#nik').addClass('is-invalid')
            $("<div class='invalid-feedback nik-errors'><span>NIK tidak boleh kosong!</span></div>").insertAfter('#nik');
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $.ajax({
                url: '/check_nik',
                type: 'GET',
                data: {
                    nik: nik,
                }
            }).done(function (data) {
                console.log(data);
                if (data.error) {
                    $('#nik').removeClass('is-valid')
                    $('#nik').addClass('is-invalid')
                    $("<div class='invalid-feedback nik-errors'><span>NIK tidak terdaftar pada sistem!</span></div>").insertAfter('#nik');
                    $("#submit").attr('disabled', 'disabled'); //disable.
                    // console.log(data.districts[0]['id']);
                } else if (data.success) {
                    $('#nik').removeClass('is-invalid')
                    $('#nik').addClass('is-valid')
                    $("<div class='valid-feedback nik-errors'><span>NIK terdaftar pada sistem!</span></div>").insertAfter('#nik');
                    if (business_cat != 0 && name && ward != 0 && address && start_date && modal > 0 && workers > 0 && email) {
                        $("#submit").removeAttr('disabled'); //enable.
                    } else {
                        $("#submit").attr('disabled', 'disabled'); //disable.
                    }
                }
            });
        }
    });

    // Cek Nama UMKM (Apakah unik?)
    $('#name').change(function () {
        let id_umkm = $('#id_umkm').val();
        let nik = $('#nik').val();
        let name = $("#name").val();
        let business_cat = $('#business_category').val();
        let ward = $('#ward').val();
        let address = $('#address').val();
        let start_date = $('#start_date').val();
        let modal = $('#modal').val();
        let workers = $('#workers').val();
        let email = $('#email').val();
        $('.name-errors').empty();
        $('.name-errors').remove();
        if (!name) {
            $('#name').removeClass('is-valid')
            $('#name').addClass('is-invalid')
            $("<div class='invalid-feedback name-errors'><span>Nama UMKM harus diisi!</span></div>").insertAfter('#name');
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $.ajax({
                url: '/check_umkm',
                type: 'GET',
                data: {
                    id_umkm: id_umkm,
                    name: name
                }
            }).done(function (data) {
                console.log(data.error);
                if (data.error) {
                    $('#name').removeClass('is-valid')
                    $('#name').addClass('is-invalid')
                    $("<div class='invalid-feedback name-errors'><span>Nama UMKM telah dimiliki pengguna lain! Gunakan nama UMKM yang lain!</span></div>").insertAfter('#name');
                    $("#submit").attr('disabled', 'disabled'); //disable.
                } else if (data.success) {
                    $('#name').removeClass('is-invalid')
                    $('#name').addClass('is-valid')
                    $("<div class='valid-feedback name-errors'><span>Nama UMKM dapat digunakan!</span></div>").insertAfter('#name');
                    if (business_cat != 0 && nik && ward != 0 && address && start_date && modal > 0 && workers > 0 && email) {
                        $("#submit").removeAttr('disabled'); //enable.
                    } else {
                        $("#submit").attr('disabled', 'disabled'); //disable.
                    }
                    $("#name").removeAttr('disabled'); //enable.
                }
            });
        }

    });

    // Validasi kategori bisnis dan NIK
    $('#business_category').change(function () {
        let nik = $('#nik').val();
        let name = $("#name").val();
        let business_cat = $('#business_category').val();
        let ward = $('#ward').val();
        let address = $('#address').val();
        let start_date = $('#start_date').val();
        let modal = $('#modal').val();
        let workers = $('#workers').val();
        let email = $('#email').val();
        $('.business_cat-errors').empty();
        $('.business_cat-errors').remove();
        if(business_cat == 0) {
            $('#business_cat').addClass('is-invalid')
            $("<div class='invalid-feedback business_cat-errors'><span>Kategori bisnis harus diisi!</span></div>").insertAfter('#business_cat');
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $('#business_cat').removeClass('is-invalid')
            if (!nik || !name || ward == 0 || !address || !start_date || modal < 1 || workers < 1 || !email) {
                $('#submit').attr('disabled', 'disabled');
            } else {
                $('#submit').removeAttr('disabled');
            }
        } 
    });

    // Validasi alamat
    $('#address').change(function () {
        let nik = $('#nik').val();
        let name = $("#name").val();
        let business_cat = $('#business_category').val();
        let ward = $('#ward').val();
        let address = $('#address').val();
        let start_date = $('#start_date').val();
        let modal = $('#modal').val();
        let workers = $('#workers').val();
        let email = $('#email').val();
        $('.address-errors').empty();
        $('.address-errors').remove();
        if(!address) {
            $('#address').addClass('is-invalid')
            $("<div class='invalid-feedback address-errors'><span>Alamat UMKM harus diisi!</span></div>").insertAfter('#address');
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $('#address').removeClass('is-invalid')
            if (business_cat == 0 || !nik || !name || ward == 0 || !start_date || modal < 1 || workers < 1 || !email) {
                $('#submit').attr('disabled', 'disabled');
            } else {
                $('#submit').removeAttr('disabled');
            }
        }
    });

    // Validasi tanggal mulai usaha
    $('#start_date').change(function () {
        let nik = $('#nik').val();
        let name = $("#name").val();
        let business_cat = $('#business_category').val();
        let ward = $('#ward').val();
        let address = $('#address').val();
        let start_date = $('#start_date').val();
        let modal = $('#modal').val();
        let workers = $('#workers').val();
        let email = $('#email').val();
        $('.start_date-errors').empty();
        $('.start_date-errors').remove();
        if(!start_date) {
            $('#start_date').addClass('is-invalid')
            $("<div class='invalid-feedback start_date-errors'><span>Tanggal mulai UMKM harus diisi!</span></div>").insertAfter('#start_date');
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $('#start_date').removeClass('is-invalid')
            if (business_cat == 0 || !nik || !name || ward == 0 || !address || !start_date || modal < 1 || workers < 1 || !email) {
                $('#submit').attr('disabled', 'disabled');
            } else {
                $('#submit').removeAttr('disabled');
            }
        }
    });

    // Validasi modal
    $('#modal').change(function () {
        let nik = $('#nik').val();
        let name = $("#name").val();
        let business_cat = $('#business_category').val();
        let ward = $('#ward').val();
        let address = $('#address').val();
        let start_date = $('#start_date').val();
        let modal = $('#modal').val();
        let workers = $('#workers').val();
        let email = $('#email').val();
        $('.modal-errors').empty();
        $('.modal-errors').remove();
        if(!modal || modal < 1) {
            $('#modal').addClass('is-invalid')
            $("<div class='invalid-feedback modal-errors'><span>Modal UMKM harus diisi dan lebih dari 0 rupiah!</span></div>").insertAfter('#modal');
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $('#modal').removeClass('is-invalid');
            if (business_cat == 0 || !nik || !name || ward == 0 || !address || !start_date || modal < 1 || workers < 1 || !email) {
                $('#submit').attr('disabled', 'disabled');
            } else {
                $('#submit').removeAttr('disabled');
            }
        }
    });

    // Validasi jumlah pekerja
    $('#workers').change(function () {
        let nik = $('#nik').val();
        let name = $("#name").val();
        let business_cat = $('#business_category').val();
        let ward = $('#ward').val();
        let address = $('#address').val();
        let start_date = $('#start_date').val();
        let modal = $('#modal').val();
        let workers = $('#workers').val();
        let email = $('#email').val();
        $('.workers-errors').empty();
        $('.workers-errors').remove();
        if(!workers || workers < 1) {
            $('#workers').addClass('is-invalid')
            $("<div class='invalid-feedback workers-errors'><span>Tenaga kerja harus diisi!</span></div>").insertAfter('#workers');
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $('#workers').removeClass('is-invalid')
            if (business_cat == 0 || !nik || !name || ward == 0 || !address || !start_date || modal < 1 || workers < 1 || !email) {
                $('#submit').attr('disabled', 'disabled');
            } else {
                $('#submit').removeAttr('disabled');
            }
        }
        
    });

    // Validasi email
    $('#email').change(function () {
        let nik = $('#nik').val();
        let name = $("#name").val();
        let business_cat = $('#business_category').val();
        let ward = $('#ward').val();
        let address = $('#address').val();
        let start_date = $('#start_date').val();
        let modal = $('#modal').val();
        let workers = $('#workers').val();
        let email = $('#email').val();
        $('.email-errors').empty();
        $('.email-errors').remove();
        if(!email) {
            $('#email').addClass('is-invalid')
            $("<div class='invalid-feedback email-errors'><span>Email harus diisi!</span></div>").insertAfter('#email');
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $('#email').removeClass('is-invalid');
            if (business_cat == 0 || !nik || !name || ward == 0 || !address || !start_date || modal < 1 || workers < 1 || !email) {
                $('#submit').attr('disabled', 'disabled');
            } else {
                $('#submit').removeAttr('disabled');
            }
        }
    });

    // SelectField dinamis (provinsi)
    $('#province').change(function () {
        let id_province = $('#province option:selected').val();
        $('#submit').attr('disabled', 'disabled');
        if (id_province == 0) {
            // Animasikan fadeOut dan fadeIn
            $('#district').fadeOut(250).fadeIn(250);
            $('#sub_district').fadeOut(250).fadeIn(250);
            $('#ward').fadeOut(250).fadeIn(250);

            // Reset kota/kabupaten
            $('#district').attr('disabled', true);
            $('#district').empty();

            // Reset kecamatan
            $('#sub_district').attr('disabled', true);
            $('#sub_district').empty();

            // Reset desa
            $('#ward').attr('disabled', true);
            $('#ward').empty();

            console.log('Tidak berubah ya!');
        } else {
            // Animasikan fadeOut dan fadeIn
            $('#district').fadeOut(250).fadeIn(250);
            $('#sub_district').fadeOut(250).fadeIn(250);
            $('#ward').fadeOut(250).fadeIn(250);

            // Reset kota/kabupaten
            $('#district').attr('disabled', true);
            $('#district').empty();

            // Reset kecamatan
            $('#sub_district').attr('disabled', true);
            $('#sub_district').empty();

            // Reset desa
            $('#ward').attr('disabled', true);
            $('#ward').empty();

            // Kirim request GET dengan datanya adalah ID provinsi
            // ID provinsi digunakan untuk mengambil data kabupaten
            $.ajax({
                url: '/get_district',
                type: 'GET',
                data: {
                    id_province: id_province
                }
            }).done(function (data) {
                if (data) {
                    $('#district').attr('disabled', false);
                    $('#district').empty();

                    $('#district').append($("<option></option>")
                        .attr('value', 0).text('- Pilih Kota/Kabupaten -'));


                    $.each(data.districts, function (index, element) {

                        $('#district').append($("<option></option>")
                            .attr('value', element.id).text(element.name));

                    });

                    // console.log(data.districts[0]['id']);
                }
            });
        }
    });

    // SelectField dinamis (kota/kabupaten)
    $('#district').change(function () {
        $('#submit').attr('disabled', 'disabled');
        let id_district = $('#district option:selected').val();
        if (id_district == 0) {
            // Animasikan fadeOut dan fadeIn
            $('#sub_district').fadeOut(250).fadeIn(250);

            // Reset kecamatan
            $('#sub_district').attr('disabled', true);
            $('#sub_district').empty();

            // Animasikan fadeOut dan fadeIn dan reset desa
            // jika data desa telah diisi sebelumnya
            if (!$('#ward').attr('disabled')) {
                $('#ward').fadeOut(250).fadeIn(250);
                $('#ward').attr('disabled', true);
                $('#ward').empty();

            }
        } else {
            // Animasikan fadeOut dan fadeIn
            $('#sub_district').fadeOut(250).fadeIn(250);

            // Reset kecamatan
            $('#sub_district').attr('disabled', true);
            $('#sub_district').empty();

            // Animasikan fadeOut dan fadeIn dan reset desa
            // jika data desa telah diisi sebelumnya
            if (!$('#ward').attr('disabled')) {
                $('#ward').fadeOut(250).fadeIn(250);
                $('#ward').attr('disabled', true);
                $('#ward').empty();

            }
            // Kirim request GET dengan datanya adalah ID kota/kabupaten
            // ID kota/kabupaten digunakan untuk mengambil data kecamatan
            $.ajax({
                url: '/get_sub_district',
                type: 'GET',
                data: {
                    id_district: id_district
                }
            }).done(function (data) {
                if (data) {
                    $('#sub_district').attr('disabled', false);
                    $('#sub_district').empty();

                    $('#sub_district').append($("<option></option>")
                        .attr('value', 0).text('- Pilih Kecamatan -'));

                    $.each(data.sub_districts, function (index, element) {

                        $('#sub_district').append($("<option></option>")
                            .attr('value', element.id).text(element.name));

                    });

                }
            });
        }

    });

    // SelectField dinamis (kecamatan)
    $('#sub_district').change(function () {
        let id_sub_district = $('#sub_district option:selected').val();
        let nik = $('#nik').val();
        let name = $("#name").val();
        let business_cat = $('#business_category').val();
        let address = $('#address').val();
        let start_date = $('#start_date').val();
        let modal = $('#modal').val();
        let workers = $('#workers').val();
        let email = $('#email').val();
        if (id_sub_district == 0) {
            $('#submit').attr('disabled', 'disabled');
            $('#ward').fadeOut(250).fadeIn(250);
            $('#ward').empty();
            $('#ward').attr('disabled', true);
        } else {
            // Animasikan fadeOut dan fadeIn
            $('#ward').fadeOut(250).fadeIn(250);

            // Reset kecamatan
            $('#ward').attr('disabled', true);
            $('#ward').empty();

            // Kirim request GET dengan datanya adalah ID kecamatan
            // ID kecamatan digunakan untuk mengambil data kelurahan/desa
            $.ajax({
                url: '/get_ward',
                type: 'GET',
                data: {
                    id_sub_district: id_sub_district
                }
            }).done(function (data) {
                if (data) {
                    $('#ward').attr('disabled', false);
                    $('#ward').empty();

                    $.each(data.wards, function (index, element) {

                        $('#ward').append($("<option></option>")
                            .attr('value', element.id).text(element.name));

                    });

                    if (business_cat == 0 || !nik || !name || ward == 0 || !address || !start_date || modal < 1 || workers < 1 || !email) {
                        $('#submit').attr('disabled', 'disabled');
                    } else {
                        $('#submit').removeAttr('disabled');
                    }
                }
            });
        }
    });
});