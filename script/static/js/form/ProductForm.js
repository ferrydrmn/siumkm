$(document).ready(function () {
    // Cek input UID UMKM dan brand ketkika loading halaman telah selesai dilakukan
    // Digunakan untuk menentukan tombol submit disabled atau tidak
    jQuery(window).on('load', function () {
        $("#submit").removeAttr('disabled');
        let name = $('#name').val();
        let brand = $('#brand').val();
        let product_type = $('#product_type').val();
        let price = $('#price').val();
        if (!name|| !brand || !product_type || !price) {
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else if (uid != '' && brand != '-') {
            $("#submit").removeAttr('disabled'); //enable.
        }
    });

    // Validasi nama brand
    $('#brand').change(function () {
        let name = $('#name').val();
        let brand = $('#brand').val();
        let product_type = $('#product_type').val();
        let product_category = $('#product_category').val();
        let price = $('#price').val();
        $('.brand-errors').empty();
        $('.brand-errors').remove();
        if (brand != '') {
            $.ajax({
                url: '/check_brand',
                type: 'GET',
                data: {
                    brand: brand,
                }
            }).done(function (data) {
                console.log(name);
                console.log(brand);
                console.log(product_type);
                console.log(product_category);
                console.log(price);
                if (data.error) {
                    console.log(data.error);
                    $('#brand').removeClass('is-valid')
                    $('#brand').addClass('is-invalid')
                    $("<div class='invalid-feedback brand-errors'><span>Nama brand tidak terdaftar dalam sistem!</span></div>").insertAfter('#brand');
                    $("#submit").attr('disabled', 'disabled'); //disable.
                    // console.log(data.districts[0]['id']);
                } else if (data.success) {
                    $("div").removeClass("brand-errors");
                    $('#brand').removeClass('is-invalid')
                    $('#brand').addClass('is-valid')
                    $("<div class='valid-feedback brand-errors'><span>Nama brand dapat digunakan!</span></div>").insertAfter('#brand');
                    if (name != '' || product_type != 0 || product_category != 0 || price != 0) {
                        $("#submit").removeAttr('disabled'); //enable.
                    } else if ($('div').hasClass('invalid-feedback')) {
                        console.log('Sini gan!');
                        $("#submit").attr('disabled', 'disabled'); //disable.
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

    // Periksa perubahan nama produk untuk membuat tombol submit bekerja
    $('#name').change(function () {
        let name = $('#name').val();
        let brand = $('#brand').val();
        let product_type = $('#product_type').val();
        let product_category = $('#product_category').val();
        let price = $('#price').val();
        $('.name-errors').empty();
        $('.name-errors').remove();
        if (name != '') {
            $('#name').removeClass('is-invalid')
            if(brand != '' && product_type != 0 && product_category != 0 && price != 0) {
                $("#submit").removeAttr('disabled'); //enable.
            } else {
                $("#submit").attr('disabled', 'disabled'); //disable.
            }
        } else {
            $('#name').removeClass('is-valid')
            $('#name').addClass('is-invalid')
            $("<div class='invalid-feedback name-errors'><span>Nama produk harus diisi!</span></div>").insertAfter('#name');
            $("#submit").attr('disabled', 'disabled'); //disable.
        }
    });

    // Periksa perubahan tipe produk untuk membuat tombol submit bekerja
    $('#product_type').change(function () {
        let name = $('#name').val();
        let brand = $('#brand').val();
        let product_type = $('#product_type').val();
        let product_category = $('#product_category').val();
        let price = $('#price').val();
        $('.product_type-errors').empty();
        $('.product_type-errors').remove();
        if (product_type != 0) {
            $('#product_type').removeClass('is-invalid')
            if(name != '' && brand != '' && product_category != 0 && price != 0) {
                $("#submit").removeAttr('disabled'); //enable.
            } else {
                $("#submit").attr('disabled', 'disabled'); //disable.
            }
        } else {
            $('#product_type').removeClass('is-valid')
            $('#product_type').addClass('is-invalid')
            $("<div class='invalid-feedback product_type-errors'><span>Jenis produk harus dipilih!</span></div>").insertAfter('#product_type');
            $("#submit").attr('disabled', 'disabled'); //disable.
        }
    });

    // Periksa perubahan kategori produk untuk membuat tombol submit bekerja
    $('#product_category').change(function () {
        let name = $('#name').val();
        let brand = $('#brand').val();
        let product_type = $('#product_type').val();
        let product_category = $('#product_category').val();
        let price = $('#price').val();
        $('.product_category-errors').empty();
        $('.product_category-errors').remove();
        if (product_category != 0) {
            $('#product_category').removeClass('is-invalid')
            if(name != '' && brand != '' && product_type != 0 && price != 0) {
                $("#submit").removeAttr('disabled'); //enable.
            } else {
                $("#submit").attr('disabled', 'disabled'); //disable.
            }
        } else {
            $('#product_category').removeClass('is-valid')
            $('#product_category').addClass('is-invalid')
            $("<div class='invalid-feedback product_category-errors'><span>Kategori produk harus dipilih!</span></div>").insertAfter('#product_category');
            $("#submit").attr('disabled', 'disabled'); //disable.
        }
    });

    // Periksa perubahan harga untuk membuat tombol submit bekerja
    $('#price').change(function () {
        let name = $('#name').val();
        let brand = $('#brand').val();
        let product_type = $('#product_type').val();
        let product_category = $('#product_category').val();
        let price = $('#price').val();
        $('.price-errors').empty();
        $('.price-errors').remove();
        if (price > 0) {
            $('#price').removeClass('is-invalid')
            if(brand != '' && name != '' && product_type != 0 && product_category != 0) {
                $("#submit").removeAttr('disabled'); //enable.
            } else {
                $("#submit").attr('disabled', 'disabled'); //disable.
            }
        } else {
            $('#price').removeClass('is-valid')
            $('#price').addClass('is-invalid')
            $("<div class='invalid-feedback price-errors'><span>Harga harus diisi lebih dari 0 rupiah!</span></div>").insertAfter('#price');
            $("#submit").attr('disabled', 'disabled'); //disable.
        }
    });
});