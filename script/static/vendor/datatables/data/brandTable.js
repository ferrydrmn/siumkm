$(document).ready(function () {
    let url = window.location.href;
    let id_umkm = url.substring(url.lastIndexOf('/') + 1);
    let ajax = '/brand/data'
    if(id_umkm) {
        ajax = '/brand/data?id_umkm=' + id_umkm;
    } 
    $('#table-brand').DataTable({
        ajax: ajax,
        processing: true,
        serverSide: true,
        columns: [{
                data: 'name'
            },
            {
                data: 'umkm'
            },
            {
                data: 'product_count'
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
            'targets': 4
        }],
        order: [[4, 'desc']]
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