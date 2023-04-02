$(document).ready(function () {
    // Cek input nama kategori produk ketika loading halaman telah selesai dilakukan
    // Digunakan untuk menentukan tombol submit disabled atau tidak
    jQuery(window).on('load', function () {
        $("#submit").removeAttr('disabled');
        let product_category = $('#product_category').val();
        if (!product_category) {
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $("#submit").removeAttr('disabled'); //enable.
        }
    });

    // Cek nama kategori bisnis (Apakah sudah terdaftar di sistem?)
    $('#product_category').change(function () {
        let id_product_category = $('#id_product_category').val();
        let product_category = $('#product_category').val();
        $('.product_category-errors').empty();
        $('.product_category-errors').remove();
        if(product_category) {
            $.ajax({
                url: '/get_product_category',
                type: 'GET',
                data: {
                    product_category: product_category,
                    id_product_category: id_product_category
                }
            }).done(function (data) {
                console.log(data);
                if (data.error) {
                    $('#product_category').removeClass('is-valid')
                    $('#product_category').addClass('is-invalid')
                    $("<div class='invalid-feedback product_category-errors'><span>Nama kategori produk telah terdaftar dalam sistem!</span></div>").insertAfter('#product_category');
                    $("#submit").attr('disabled', 'disabled'); //disable.
                } else if (data.success) {
                    $('#product_category').removeClass('is-invalid')
                    $('#product_category').addClass('is-valid')
                    $("<div class='valid-feedback product_category-errors'><span>Nama kategori produk dapat digunakan!</span></div>").insertAfter('#product_category');
                    $("#submit").removeAttr('disabled'); //enable.
                }
            });
        } else {
            $('#product_category').removeClass('is-valid')
            $('#product_category').addClass('is-invalid')
            $("<div class='invalid-feedback product_category-errors'><span>Nama kategori produk harus diisi!</span></div>").insertAfter('#product_category');
            $("#submit").attr('disabled', 'disabled'); //disable.
        }
    });

});