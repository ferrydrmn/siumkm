$(document).ready(function () {
    let url = window.location.href;
    let id_brand = url.substring(url.lastIndexOf('/') + 1);
    let ajax = '/product/data'
    if(id_brand) {
        ajax = '/product/data?id_brand=' + id_brand;
    }
    console.log(ajax);
    $('#table-product').DataTable({
        ajax: ajax,
        columns: [{
                data: 'name'
            },
            {
                data: 'brand'
            },
            {
                data: 'product_type'
            },
            {
                data: 'product_cat'
            },
            {
                data: 'price'
            },
            {
                data: 'action',
                searchable: false,
                orderable: false
            },
            {
                data: 'updated_at',
                "sType": "date-uk",
            },
        ],
        columnDefs: [{
            type: 'date-uk',
            'targets': 6
        }],
        order: [
            [6, 'desc']
        ]
    });
    jQuery.extend(jQuery.fn.dataTableExt.oSort, {
        "date-uk-pre": function (a) {
            var ukDatea = a.split('/');
            return (ukDatea[2] + ukDatea[1] + ukDatea[0]) * 1;
        },

        "date-uk-asc": function (a, b) {
            return ((a < b) ? -1 : ((a > b) ? 1 : 0));
        },

        "date-uk-desc": function (a, b) {
            return ((a < b) ? 1 : ((a > b) ? -1 : 0));
        }
    });
});