$(document).ready(function () {
    $('#table-owner').DataTable({
        ajax: '/owner/data',
        processing: true,
        serverSide: true,
        columns: [{
                data: 'nik'
            },
            {
                data: 'name'
            },
            {
                data: 'ward',
                searchable: false,
                orderable: false
            },
            {
                data: 'sub_district',
                searchable: false,
                orderable: false
            },
            {
                data: 'district',
                searchable: false,
                orderable: false
            },
            {
                data: 'province',
                searchable: false,
                orderable: false
            },
            {
                data: 'umkm_count',
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
            'targets': 8
        }],
        order: [[8, 'desc']]
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