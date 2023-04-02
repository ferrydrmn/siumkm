$(document).ready(function () {
    // Cek input password lama, password baru dan konfirmasi password ketkika loading halaman telah selesai dilakukan
    // Digunakan untuk menentukan tombol submit disabled atau tidak
    jQuery(window).on('load', function () {
        console.log('Hello World!');
        $("#submit").removeAttr('disabled');
        let old_password = $('#old_password').val();
        let new_password = $('#new_password').val();
        let confirm_password = $('#confirm_password').val();
        if (old_password == '' || new_password == '' || confirm_password == '') {
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else if (old_password != '' && new_password != '-' && confirm_password != '') {
            $("#submit").removeAttr('disabled'); //enable.
        }
    });

    // Periksa apakah password lama kosong atau tidak
    $('#old_password').change(function () {
        let old_password = $('#old_password').val();
        let new_password = $('#new_password').val();
        let confirm_password = $('#confirm_password').val();
        $('.old_password-errors').empty();
        $('.old_password-errors').remove();
        if (!old_password) {
            $('#old_password').addClass('is-invalid')
            $("<div class='invalid-feedback old_password-errors'><span>Password lama tidak boleh kosong!</span></div>").insertAfter('#old_password');
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $('#old_password').removeClass('is-invalid')
            if(!new_password || !old_password || !confirm_password) {
                $("#submit").attr('disabled', 'disabled'); //disable.
            } else {
                $("#submit").removeAttr('disabled'); //enable.
            }
        }
    });

    // Periksa apakah password baru kosong atau tidak
    $('#new_password').change(function () {
        // Reset konfirmasi password
        $('#confirm_password').fadeOut(250).fadeIn(250);
        $('#confirm_password').val('');
        $('.new_password-errors').empty();
        $('.new_password-errors').remove();
        let old_password = $('#old_password').val();
        let new_password = $('#new_password').val();
        let confirm_password = $('#confirm_password').val();
        if (!new_password) {
            $('#new_password').addClass('is-invalid')
            $("<div class='invalid-feedback old_password-errors'><span>Password baru tidak boleh kosong!</span></div>").insertAfter('#new_password');
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $('#new_password').removeClass('is-invalid')
            if(!old_password || !confirm_password) {
                $("#submit").attr('disabled', 'disabled'); //disable.
            } else {
                $("#submit").removeAttr('disabled'); //enable.
            }
        }
    });

    // Periksa apakah konfirmasi password kosong atau tidak
    $('#confirm_password').change(function () {
        let old_password = $('#old_password').val();
        let new_password = $('#new_password').val();
        let confirm_password = $('#confirm_password').val();
        $('.confirm_password-errors').empty();
        $('.confirm_password-errors').remove();
        $('#confirm_password').removeClass('is-invalid')
        if (!confirm_password) {
            $('#confirm_password').addClass('is-invalid')
            $("<div class='invalid-feedback confirm_password-errors'><span>Password baru tidak boleh kosong!</span></div>").insertAfter('#confirm_password');
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else if (confirm_password != new_password){
            $('#confirm_password').addClass('is-invalid')
            $("<div class='invalid-feedback confirm_password-errors'><span>Password baru dengan konfirmasi password harus sama!</span></div>").insertAfter('#confirm_password');
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $('#confirm_password').removeClass('is-invalid')
            if(!old_password || !new_password) {
                $("#submit").attr('disabled', 'disabled'); //disable.
            } else {
                $("#submit").removeAttr('disabled'); //enable.
            }
        }
    });
});