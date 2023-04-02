$(document).ready(function () {
    // Cek input nama provinsi ketika loading halaman telah selesai dilakukan
    // Digunakan untuk menentukan tombol submit disabled atau tidak
    jQuery(window).load(function () {
        $("#submit").removeAttr('disabled');
        let name = $('#name').val();
        if (name == '') {
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else if (uid != '' && brand != '-') {
            $("#submit").removeAttr('disabled'); //enable.
        }
    });

    // Cek nama provinsi (apakah kosong atau tidak)
    $('#name').change(function () {
        let name = $('#name').val();
        $('.name-errors').empty();
        $('.name-errors').remove();
        if (name == '') {
            $('#name').removeClass('is-valid')
            $('#name').addClass('is-invalid')
            $("<div class='invalid-feedback name-errors'><span>Nama provinsi tidak boleh kosong!</span></div>").insertAfter('#name');
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $("div").removeClass("name-errors");
            $('#name').removeClass('is-invalid');
            $("#submit").removeAttr('disabled'); //enable.
        }
    });

});