$(document).ready(function () {
    // Cek input nama kecamatan ketika loading halaman telah selesai dilakukan
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

    // Cek ID kota/kabupaten (Apakah sudah terdaftar di sistem?)
    $('#id_district').change(function () {
        let name = $('#name').val();
        let id_district = $('#id_district').val();
        $('.id_district-errors').empty();
        $('.id_district-errors').remove();
        if(id_district && $.isNumeric(id_district) && id_district > 0) {
            $.ajax({
                url: '/check_id_district',
                type: 'GET',
                data: {
                    id_district: id_district
                }
            }).done(function (data) {
                console.log(data);
                if (data.error) {
                    $('#id_district').removeClass('is-valid')
                    $('#id_district').addClass('is-invalid')
                    $("<div class='invalid-feedback id_district-errors'><span>ID kota/kabupaten tidak terdaftar dalam sistem!</span></div>").insertAfter('#id_district');
                    $("#submit").attr('disabled', 'disabled'); //disable.
                } else if (data.success) {
                    $('#id_district').removeClass('is-invalid')
                    $('#id_district').addClass('is-valid')
                    $("<div class='valid-feedback id_district-errors'><span>ID kota/kabupaten dapat digunakan!</span></div>").insertAfter('#id_district');
                    if(!name) {
                        $("#submit").attr('disabled', 'disabled'); //disable.
                    } else {
                        $("#submit").removeAttr('disabled'); //enable.
                    }
                }
            });
        } else {
            $('#id_district').removeClass('is-valid')
            $('#id_district').addClass('is-invalid')
            $("<div class='invalid-feedback id_district-errors'><span>ID kota/kabupaten harus diisi!</span></div>").insertAfter('#id_district');
            $("#submit").attr('disabled', 'disabled'); //disable.
        }
    });

    // Cek nama kecamatan (Apakah sudah terdaftar di sistem?)
    $('#name').change(function () {
        let name = $('#name').val();
        let id_district = $('#id_district').val();
        $('.name-errors').empty();
        $('.name-errors').remove();
        if(!name) {
            $('#name').removeClass('is-valid')
            $('#name').addClass('is-invalid')
            $("<div class='invalid-feedback name-errors'><span>Nama kecamatan harus diisi!</span></div>").insertAfter('#name');
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $('#name').removeClass('is-invalid')
            if(id_district && id_district > 0) {
                $("#submit").removeAttr('disabled'); //enable.
            } else {
                $("#submit").attr('disabled', 'disabled'); //disable.
            }
        }
    });

});