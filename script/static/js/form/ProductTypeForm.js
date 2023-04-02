$(document).ready(function () {
    // Cek input nama tipe produk ketika loading halaman telah selesai dilakukan
    // Digunakan untuk menentukan tombol submit disabled atau tidak
    jQuery(window).on('load', function () {
        $("#submit").removeAttr('disabled');
        let product_type = $('#product_type').val();
        if (!product_type) {
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $("#submit").removeAttr('disabled'); //enable.
        }
    });

    // Cek nama kategori bisnis (Apakah sudah terdaftar di sistem?)
    $('#product_type').change(function () {
        let id_product_type = $('#id_product_type').val();
        let product_type = $('#product_type').val();
        $('.product_type-errors').empty();
        $('.product_type-errors').remove();
        if(product_type) {
            $.ajax({
                url: '/get_product_type',
                type: 'GET',
                data: {
                    product_type: product_type,
                    id_product_type: id_product_type
                }
            }).done(function (data) {
                console.log(data);
                if (data.error) {
                    $('#product_type').removeClass('is-valid')
                    $('#product_type').addClass('is-invalid')
                    $("<div class='invalid-feedback product_type-errors'><span>Nama tipe produk telah terdaftar dalam sistem!</span></div>").insertAfter('#product_type');
                    $("#submit").attr('disabled', 'disabled'); //disable.
                } else if (data.success) {
                    $('#product_type').removeClass('is-invalid')
                    $('#product_type').addClass('is-valid')
                    $("<div class='valid-feedback product_type-errors'><span>Nama tipe produk dapat digunakan!</span></div>").insertAfter('#product_type');
                    $("#submit").removeAttr('disabled'); //enable.

                }
            });
        } else {
            $('#product_type').removeClass('is-valid')
            $('#product_type').addClass('is-invalid')
            $("<div class='invalid-feedback product_type-errors'><span>Nama tipe produk harus diisi!</span></div>").insertAfter('#product_type');
            $("#submit").attr('disabled', 'disabled'); //disable.
        }
    });

});