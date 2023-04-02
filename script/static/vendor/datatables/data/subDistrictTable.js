$(document).ready(function () {
    $('#table-sub-district').DataTable({
        processing: true,
        serverSide: true,
        ajax: '/sub_district/data',
        columns: [{
                data: 'name'
            },
            {
                data: 'district',
                searchable: false,
                orderable: false,
            },
            {
                data: 'ward_count',
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