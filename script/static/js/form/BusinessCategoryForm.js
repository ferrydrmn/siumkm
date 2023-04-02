$(document).ready(function () {
    // Cek input nama kategori bisnis ketika loading halaman telah selesai dilakukan
    // Digunakan untuk menentukan tombol submit disabled atau tidak
    jQuery(window).on('load', function () {
        $("#submit").removeAttr('disabled');
        let business_category = $('#business_category').val();
        if (!business_category) {
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $("#submit").removeAttr('disabled'); //enable.
        }
    });

    // Cek nama kategori bisnis (Apakah sudah terdaftar di sistem?)
    $('#business_category').change(function () {
        let id_business_category = $('#id_business_category').val();
        let business_category = $('#business_category').val();
        $('.business_category-errors').empty();
        $('.business_category-errors').remove();
        if(business_category) {
            $.ajax({
                url: '/get_business_category',
                type: 'GET',
                data: {
                    business_category: business_category,
                    id_business_category: id_business_category
                }
            }).done(function (data) {
                console.log(data);
                if (data.error) {
                    $('#business_category').removeClass('is-valid')
                    $('#business_category').addClass('is-invalid')
                    $("<div class='invalid-feedback business_category-errors'><span>Nama kategori bisnis telah terdaftar dalam sistem!</span></div>").insertAfter('#business_category');
                    $("#submit").attr('disabled', 'disabled'); //disable.
                } else if (data.success) {
                    $('#business_category').removeClass('is-invalid')
                    $('#business_category').addClass('is-valid')
                    $("<div class='valid-feedback business_category-errors'><span>Nama kategori bisnis dapat digunakan!</span></div>").insertAfter('#business_category');
                    $("#submit").removeAttr('disabled'); //enable.

                }
            });
        } else {
            $('#business_category').removeClass('is-valid')
            $('#business_category').addClass('is-invalid')
            $("<div class='invalid-feedback business_category-errors'><span>Nama kategori bisnis harus diisi!</span></div>").insertAfter('#business_category');
            $("#submit").attr('disabled', 'disabled'); //disable.
        }
    });

});