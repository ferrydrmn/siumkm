$(document).ready(function () {
    let url = window.location.href;
    let id_owner = url.substring(url.lastIndexOf('/') + 1);
    let ajax = '/umkm/data'
    if(id_owner) {
        ajax = '/umkm/data?id_owner=' + id_owner;
    } 
    $('#table-umkm').DataTable({
        ajax: ajax,
        columns: [{
                data: 'name'
            },
            {
                data: 'business_cat'
            },
            {
                data: 'ward'
            },
            {
                data: 'sub_district'
            },
            {
                data: 'district'
            },
            {
                data: 'province'
            },
            {
                data: 'brand_count'
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
            'targets': 8
        }],
        order: [
            [8, 'desc']
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