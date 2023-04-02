$(document).ready(function () {
    // Cek input UID UMKM dan brand ketkika loading halaman telah selesai dilakukan
    // Digunakan untuk menentukan tombol submit disabled atau tidak
    jQuery(window).on('load', function () {
        $("#submit").removeAttr('disabled');
        let umkm = $('#umkm').val();
        let brand = $('#brand').val();
        if (!umkm || !brand) {
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $("#submit").removeAttr('disabled'); //enable.
        }
    });

    // Cek nama UMKM (Apakah sudah terdaftar di sistem?)
    $('#umkm').change(function () {
        let umkm = $('#umkm').val();
        let brand = $('#brand').val();
        $('.umkm-errors').empty();
        $('.umkm-errors').remove();
        if(umkm) {
            $.ajax({
                url: '/get_umkm',
                type: 'GET',
                data: {
                    umkm: umkm,
                }
            }).done(function (data) {
                console.log(data);
                if (data.error) {
                    $('#umkm').removeClass('is-valid')
                    $('#umkm').addClass('is-invalid')
                    $("<div class='invalid-feedback umkm-errors'><span>Nama UMKM tidak terdaftar pada sistem!</span></div>").insertAfter('#umkm');
                    $("#submit").attr('disabled', 'disabled'); //disable.
                    // console.log(data.districts[0]['id']);
                } else if (data.success) {
                    $('#umkm').removeClass('is-invalid')
                    $('#umkm').addClass('is-valid')
                    $("<div class='valid-feedback umkm-errors'><span>Nama UMKM terdaftar pada sistem!</span></div>").insertAfter('#umkm');
                    if (brand && !$('div').hasClass('invalid-feedback')) {
                        $("#submit").removeAttr('disabled'); //enable.
                    } else {
                        $("#submit").attr('disabled', 'disabled'); //disable.
                    }
                }
            });
        } else {
            $('#umkm').removeClass('is-valid')
            $('#umkm').addClass('is-invalid')
            $("<div class='invalid-feedback umkm-errors'><span>Nama UMKM harus diisi!</span></div>").insertAfter('#umkm');
            $("#submit").attr('disabled', 'disabled'); //disable.
            // console.log(data.districts[0]['id']);
        }
    });

    // Validasi nama brand
    $('#brand').change(function () {
        let umkm = $('#umkm').val();
        let brand = $('#brand').val();
        let id_brand = $('#id_brand').val();
        $('.brand-errors').empty();
        $('.brand-errors').remove();
        if (brand != '') {
            $.ajax({
                url: '/get_brand',
                type: 'GET',
                data: {
                    brand: brand,
                    id_brand: id_brand
                }
            }).done(function (data) {
                console.log(data);
                console.log(id_brand);
                if (data.error) {
                    console.log(data.error);
                    $('#brand').removeClass('is-valid')
                    $('#brand').addClass('is-invalid')
                    $("<div class='invalid-feedback brand-errors'><span>Nama brand telah digunakan!</span></div>").insertAfter('#brand');
                    $("#submit").attr('disabled', 'disabled'); //disable.
                    // console.log(data.districts[0]['id']);
                } else if (data.success) {
                    $('#brand').removeClass('is-invalid')
                    $('#brand').addClass('is-valid')
                    $("<div class='valid-feedback brand-errors'><span>Nama brand dapat digunakan!</span></div>").insertAfter('#brand');
                    if (umkm != '') {
                        $("#submit").removeAttr('disabled'); //enable.
                    } else {
                        $("#submit").attr('disabled', 'disabled'); //disable.
                    }
                }
            });
        } else {
            $('#brand').removeClass('is-valid')
            $('#brand').addClass('is-invalid')
            $("<div class='invalid-feedback brand-errors'><span>Nama brand harus diisi!</span></div>").insertAfter('#brand');
            $("#submit").attr('disabled', 'disabled'); //disable.
        }

    });

});