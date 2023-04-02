$(document).ready(function () {
    let url = window.location.href;
    let id_umkm = url.substring(url.lastIndexOf('/') + 1);
    let ajax = '/product_type/data'
    $('#table-product-type').DataTable({
        ajax: ajax,
        processing: true,
        serverSide: true,
        columns: [{
                data: 'name'
            },
            {
                data: 'product_count',
                searchable: false,
                orderable: false
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
            'targets': 3
        }],
        order: [[3, 'desc']]
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