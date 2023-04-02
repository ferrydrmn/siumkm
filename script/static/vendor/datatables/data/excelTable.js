$(document).ready(function () {
    let url = window.location.href;
    let id_umkm = url.substring(url.lastIndexOf('/') + 1);
    let ajax = '/excel/data'
    if(id_umkm) {
        ajax = '/excel/data';
    } 
    $('#table-excel').DataTable({
        ajax: ajax,
        processing: true,
        serverSide: true,
        searching: false,
        columns: [{
                data: 'name',
                searchable: false,
                orderable: false
            },
            {
                data: 'uploader',
                searchable: false,
                orderable: false
            },
            {
                data: 'type',
                searchable: false,
                orderable: false
            },
            {
                data: 'updated_at'
            },
            {
                data: 'action',
                searchable: false,
                orderable: false
            },
        ],
        columnDefs: [{
            type: 'date-uk',
            'targets': 2
        }],
        order: [[2, 'desc']]
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