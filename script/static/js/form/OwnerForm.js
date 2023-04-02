$(document).ready(function () {
    // Cek input NIK ketkika loading halaman telah selesai dilakukan
    // Digunakan untuk menentukan tombol submit disabled atau tidak
    jQuery(window).on('load', function () {
        $("#submit").removeAttr('disabled');
        let id = $('#id_owner').val();
        let nik = $('#nik').val();
        if (nik == '' && id == 0) {
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $("#submit").removeAttr('disabled'); //enable.
        }
    });

    // Validasi NIK
    $('#nik').change(function () {
        let id = $('#id_owner').val();
        let nik = $('#nik').val();
        let name = $('#name').val();
        let ward = $('#ward').val();
        let postal_code = $('#postal_code').val();
        let address = $('#address').val();
        console.log(nik);
        console.log(id);
        $('.nik-errors').empty();
        $('.nik-errors').remove();
        if (!nik || nik == '') {
            $('#nik').removeClass('is-valid')
            $('#nik').addClass('is-invalid')
            $("<div class='invalid-feedback nik-errors'><span>Data NIK tidak boleh kosong!</span></div>").insertAfter('#nik');
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $.ajax({
                url: '/get_nik',
                type: 'GET',
                data: {
                    nik: nik,
                    id: id,
                }
            }).done(function (data) {
                console.log(data);
                if (data.error) {
                    $('#nik').removeClass('is-valid')
                    $('#nik').addClass('is-invalid')
                    $("<div class='invalid-feedback nik-errors'><span>NIK sudah digunakan!</span></div>").insertAfter('#nik');
                    $("#submit").attr('disabled', 'disabled'); //disable.
                } else if (data.success) {
                    $('#nik').removeClass('is-invalid')
                    $('#nik').addClass('is-valid')
                    $("<div class='valid-feedback nik-errors'><span>NIK dapat digunakan!</span></div>").insertAfter('#nik');
                    if (!name || !ward || !postal_code || !address) {
                        $("#submit").attr('disabled', 'disabled'); //disable.
                    } else {
                        $("#submit").removeAttr('disabled'); //enable.
                    }
                }
            });
        }
    });

    // Validasi nama
    $('#name').change(function () {
        let nik = $('#nik').val();
        let name = $('#name').val();
        let ward = $('#ward').val();
        let postal_code = $('#postal_code').val();
        let address = $('#address').val();

        $('.name-errors').empty();
        $('.name-errors').remove();

        if (!name || name == '') {
            $('#name').removeClass('is-valid');
            $('#name').addClass('is-invalid');
            $("<div class='invalid-feedback name-errors'><span>Data nama tidak boleh kosong!</span></div>").insertAfter('#name');
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $('#name').removeClass('is-invalid');
            $('#name').addClass('is-valid');
            if (!nik || !ward || !postal_code || !address) {
                $("#submit").attr('disabled', 'disabled'); //disable.
            } else {
                $("#submit").removeAttr('disabled'); //enable.
            }
        }
    })

    // Validasi Kode Pos
    $('#postal_code').change(function () {
        let nik = $('#nik').val();
        let name = $('#name').val();
        let ward = $('#ward').val();
        let postal_code = $('#postal_code').val();
        let address = $('#address').val();

        $('.postal_code-errors').empty();
        $('.postal_code-errors').remove();

        if (!postal_code || postal_code == '') {
            $('#postal_code').removeClass('is-valid');
            $('#postal_code').addClass('is-invalid');
            $("<div class='invalid-feedback postal_code-errors'><span>Data kode pos tidak boleh kosong!</span></div>").insertAfter('#postal_code');
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $('#postal_code').removeClass('is-invalid');
            $('#postal_code').addClass('is-valid');
            if (!nik || !ward || !address || !name) {
                $("#submit").attr('disabled', 'disabled'); //disable.
            } else {
                $("#submit").removeAttr('disabled'); //enable.
            }
        }
    })

    // Validasi alamat
    $('#address').change(function () {
        let nik = $('#nik').val();
        let name = $('#name').val();
        let ward = $('#ward').val();
        let postal_code = $('#postal_code').val();
        let address = $('#address').val();

        $('.address-errors').empty();
        $('.address-errors').remove();

        if (!postal_code || postal_code == '') {
            $('#address').removeClass('is-valid');
            $('#address').addClass('is-invalid');
            $("<div class='invalid-feedback address-errors'><span>Data alamat tidak boleh kosong!</span></div>").insertAfter('#address');
            $("#submit").attr('disabled', 'disabled'); //disable.
        } else {
            $('#address').removeClass('is-invalid');
            $('#address').addClass('is-valid');
            if (!nik || !ward || !postal_code || !name || !address) {
                $("#submit").attr('disabled', 'disabled'); //disable.
            } else {
                $("#submit").removeAttr('disabled'); //enable.
            }
        }
    })

    // SelectField dinamis (provinsi)
    $('#province').change(function () {
        let id_province = $('#province option:selected').val();
        $("#submit").attr('disabled', 'disabled'); //disable.
        if (id_province == 0) {
            // Animasikan fadeOut dan fadeIn
            $('#district').fadeOut(250).fadeIn(250);
            $('#sub_district').fadeOut(250).fadeIn(250);
            $('#ward').fadeOut(250).fadeIn(250);

            // Reset kota/kabupaten
            $('#district').attr('disabled', true);
            $('#district').empty();

            // Reset kecamatan
            $('#sub_district').attr('disabled', true);
            $('#sub_district').empty();

            // Reset desa
            $('#ward').attr('disabled', true);
            $('#ward').empty();

            console.log('Tidak berubah ya!');
        } else {
            // Animasikan fadeOut dan fadeIn
            $('#district').fadeOut(250).fadeIn(250);
            $('#sub_district').fadeOut(250).fadeIn(250);
            $('#ward').fadeOut(250).fadeIn(250);

            // Reset kota/kabupaten
            $('#district').attr('disabled', true);
            $('#district').empty();

            // Reset kecamatan
            $('#sub_district').attr('disabled', true);
            $('#sub_district').empty();

            // Reset desa
            $('#ward').attr('disabled', true);
            $('#ward').empty();

            // Kirim request GET dengan datanya adalah ID provinsi
            // ID provinsi digunakan untuk mengambil data kabupaten
            $.ajax({
                url: '/get_district',
                type: 'GET',
                data: {
                    id_province: id_province
                }
            }).done(function (data) {
                if (data) {
                    $('#district').attr('disabled', false);
                    $('#district').empty();

                    $('#district').append($("<option></option>")
                        .attr('value', 0).text('- Pilih Kota/Kabupaten -'));


                    $.each(data.districts, function (index, element) {

                        $('#district').append($("<option></option>")
                            .attr('value', element.id).text(element.name));

                    });

                    // console.log(data.districts[0]['id']);
                }
            });
        }
    });

    // SelectField dinamis (kota/kabupaten)
    $('#district').change(function () {
        $("#submit").attr('disabled', 'disabled'); //disable.
        let id_district = $('#district option:selected').val();
        if (id_district == 0) {
            // Animasikan fadeOut dan fadeIn
            $('#sub_district').fadeOut(250).fadeIn(250);

            // Reset kecamatan
            $('#sub_district').attr('disabled', true);
            $('#sub_district').empty();

            // Animasikan fadeOut dan fadeIn dan reset desa
            // jika data desa telah diisi sebelumnya
            if (!$('#ward').attr('disabled')) {
                $('#ward').fadeOut(250).fadeIn(250);
                $('#ward').attr('disabled', true);
                $('#ward').empty();

            }
        } else {
            // Animasikan fadeOut dan fadeIn
            $('#sub_district').fadeOut(250).fadeIn(250);

            // Reset kecamatan
            $('#sub_district').attr('disabled', true);
            $('#sub_district').empty();

            // Animasikan fadeOut dan fadeIn dan reset desa
            // jika data desa telah diisi sebelumnya
            if (!$('#ward').attr('disabled')) {
                $('#ward').fadeOut(250).fadeIn(250);
                $('#ward').attr('disabled', true);
                $('#ward').empty();

            }
            // Kirim request GET dengan datanya adalah ID kota/kabupaten
            // ID kota/kabupaten digunakan untuk mengambil data kecamatan
            $.ajax({
                url: '/get_sub_district',
                type: 'GET',
                data: {
                    id_district: id_district
                }
            }).done(function (data) {
                if (data) {
                    $('#sub_district').attr('disabled', false);
                    $('#sub_district').empty();

                    $('#sub_district').append($("<option></option>")
                        .attr('value', 0).text('- Pilih Kecamatan -'));

                    $.each(data.sub_districts, function (index, element) {

                        $('#sub_district').append($("<option></option>")
                            .attr('value', element.id).text(element.name));

                    });

                }
            });
        }

    });

    // SelectField dinamis (kecamatan)
    $('#sub_district').change(function () {
        let id_sub_district = $('#sub_district option:selected').val();
        let nik = $('#nik').val();
        let name = $('#name').val();
        let postal_code = $('#postal_code').val();
        let address = $('#address').val();
        if (id_sub_district == 0) {
            $("#submit").attr('disabled', 'disabled'); //disable.
            $('#ward').fadeOut(250).fadeIn(250);
            $('#ward').empty();
            $('#ward').attr('disabled', true);
        } else {
            // Animasikan fadeOut dan fadeIn
            $('#ward').fadeOut(250).fadeIn(250);

            // Reset kecamatan
            $('#ward').attr('disabled', true);
            $('#ward').empty();

            // Kirim request GET dengan datanya adalah ID kecamatan
            // ID kecamatan digunakan untuk mengambil data kelurahan/desa
            $.ajax({
                url: '/get_ward',
                type: 'GET',
                data: {
                    id_sub_district: id_sub_district
                }
            }).done(function (data) {
                if (data) {
                    $('#ward').attr('disabled', false);
                    $('#ward').empty();

                    $.each(data.wards, function (index, element) {

                        $('#ward').append($("<option></option>")
                            .attr('value', element.id).text(element.name));

                    });

                    if(!nik || !name || !ward || !postal_code || !address) {
                        $("#submit").attr('disabled', 'disabled'); //disable.
                    } else {
                        $("#submit").removeAttr('disabled'); //enable.
                    }
                }
            });
        }
    });
});