$(document).ready(function () {
    // Cek input nama kabupaten ketika loading halaman telah selesai dilakukan
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

    // Cek ID provinsi (Apakah sudah terdaftar di sistem?)
    $('#id_province').change(function () {
        let name = $('#name').val();
        let id_province = $('#id_province').val();
        $('.id_province-errors').empty();
        $('.id_province-errors').remove();
        if(id_province || id_province > 0) {
            $.ajax({
                url: '/check_id_province',
                type: 'GET',
                data: {
                    id_province: id_province
                }
            }).done(function (data) {
                console.log(data);
                if (data.error) {
                    $('#id_province').removeClass('is-valid')
                    $('#id_province').addClass('is-invalid')
                    $("<div class='invalid-feedback id_province-errors'><span>ID provinsi tidak terdaftar dalam sistem!</span></div>").insertAfter('#id_province');
                    $("#submit").attr('disabled', 'disabled'); //disable.
                } else if (data.success) {
                    $('#id_province').removeClass('is-invalid')
                    $('#id_province').addClass('is-valid')
                    $("<div class='valid-feedback id_province-errors'><span>ID provinsi dapat digunakan!</span></div>").insertAfter('#id_province');
                    if(!name) {
                        $("#submit").attr('disabled', 'disabled'); //disable.
                    } else {
                        $("#submit").removeAttr('disabled'); //enable.
                    }
                }
            });
        } else {
            $('#id_province').removeClass('is-valid')
            $('#id_province').addClass('is-invalid')
            $("<div class='invalid-feedback name-errors'><span>ID provinsi harus diisi!</span></div>").insertAfter('#id_province');
            $("#submit").attr('disabled', 'disabled'); //disable.
        }
    });

    // Cek nama kota/kabupaten (Apakah sudah terdaftar di sistem?)
    $('#name').change(function () {
        let name = $('#name').val();
        let id_province = $('#id_province').val();
        $('.name-errors').empty();
        $('.name-errors').remove();
        if(!name) {
            $('#name').removeClass('is-valid')
            $('#name').addClass('is-invalid')
            $("<div class='invalid-feedback name-errors'><span>Nama kota/kabupaten harus diisi!</span></div>").insertAfter('#name');
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $('#name').removeClass('is-invalid')
            if(id_province && id_province > 0) {
                $("#submit").removeAttr('disabled'); //enable.
            } else {
                $("#submit").attr('disabled', 'disabled'); //disable.
            }
        }
    });

});