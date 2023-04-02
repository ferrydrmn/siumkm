$(document).ready(function () {
    // Cek input nama desa ketika loading halaman telah selesai dilakukan
    // Digunakan untuk menentukan tombol submit disabled atau tidak
    jQuery(window).on('load', function () {
        $("#submit").removeAttr('disabled');
        let name = $('#name').val();
        if (!name) {
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $("#submit").removeAttr('disabled'); //enable.
        }
    });

    // Cek ID kecamatan (Apakah sudah terdaftar di sistem?)
    $('#id_sub_district').change(function () {
        let name = $('#name').val();
        let id_sub_district = $('#id_sub_district').val();
        $('.id_sub_district-errors').empty();
        $('.id_sub_district-errors').remove();
        if(id_sub_district && $.isNumeric(id_sub_district) && id_sub_district > 0) {
            $.ajax({
                url: '/check_id_sub_district',
                type: 'GET',
                data: {
                    id_sub_district: id_sub_district
                }
            }).done(function (data) {
                console.log(data);
                if (data.error) {
                    $('#id_sub_district').removeClass('is-valid')
                    $('#id_sub_district').addClass('is-invalid')
                    $("<div class='invalid-feedback id_sub_district-errors'><span>ID kecamatan tidak terdaftar dalam sistem!</span></div>").insertAfter('#id_sub_district');
                    $("#submit").attr('disabled', 'disabled'); //disable.
                } else if (data.success) {
                    $('#id_sub_district').removeClass('is-invalid')
                    $('#id_sub_district').addClass('is-valid')
                    $("<div class='valid-feedback id_sub_district-errors'><span>ID kecamatan dapat digunakan!</span></div>").insertAfter('#id_sub_district');
                    if(!name) {
                        $("#submit").attr('disabled', 'disabled'); //disable.
                    } else {
                        $("#submit").removeAttr('disabled'); //enable.
                    }
                }
            });
        } else {
            $('#id_sub_district').removeClass('is-valid')
            $('#id_sub_district').addClass('is-invalid')
            $("<div class='invalid-feedback id_sub_district-errors'><span>ID kecamatan harus diisi!</span></div>").insertAfter('#id_sub_district');
            $("#submit").attr('disabled', 'disabled'); //disable.
        }
    });

    // Cek nama kota/kabupaten (Apakah sudah terdaftar di sistem?)
    $('#name').change(function () {
        let name = $('#name').val();
        let id_sub_district = $('#id_sub_district').val();
        $('.name-errors').empty();
        $('.name-errors').remove();
        if(!name) {
            $('#name').removeClass('is-valid')
            $('#name').addClass('is-invalid')
            $("<div class='invalid-feedback name-errors'><span>Nama provinsi harus diisi!</span></div>").insertAfter('#name');
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $('#name').removeClass('is-invalid')
            if(id_sub_district && id_sub_district > 0) {
                $("#submit").removeAttr('disabled'); //enable.
            } else {
                $("#submit").attr('disabled', 'disabled'); //disable.
            }
        }
    });

});