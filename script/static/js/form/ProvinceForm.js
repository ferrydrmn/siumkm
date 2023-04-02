$(document).ready(function () {
    // Cek input nama provinsi ketika loading halaman telah selesai dilakukan
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

    // Cek nama provinsi (Apakah sudah terdaftar di sistem?)
    $('#name').change(function () {
        let name = $('#name').val();
        let id_province = $('#id_province').val();
        $('.name-errors').empty();
        $('.name-errors').remove();
        if(name) {
            $.ajax({
                url: '/check_province',
                type: 'GET',
                data: {
                    name: name,
                    id_province: id_province
                }
            }).done(function (data) {
                console.log(data);
                if (data.error) {
                    $('#name').removeClass('is-valid')
                    $('#name').addClass('is-invalid')
                    $("<div class='invalid-feedback name-errors'><span>Nama provinsi telah terdaftar pada sistem! Gunakan nama yang lain!</span></div>").insertAfter('#name');
                    $("#submit").attr('disabled', 'disabled'); //disable.
                } else if (data.success) {
                    $('#name').removeClass('is-invalid')
                    $('#name').addClass('is-valid')
                    $("<div class='valid-feedback name-errors'><span>Nama provinsi dapat digunakan!</span></div>").insertAfter('#name');
                    $("#submit").removeAttr('disabled'); //enable.
                }
            });
        } else {
            $('#name').removeClass('is-valid')
            $('#name').addClass('is-invalid')
            $("<div class='invalid-feedback name-errors'><span>Nama provinsi harus diisi!</span></div>").insertAfter('#name');
            $("#submit").attr('disabled', 'disabled'); //disable.
            // console.log(data.districts[0]['id']);
        }
    });

});