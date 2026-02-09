$(document).ready(function() {
    $('#workersTable').DataTable({
        dom: 'Bfrtip',  // b - buttons, f - filter, r - processing, t - table, i - info, p - pagination
        buttons: [
            {
                extend: 'excelHtml5',
                text: '⬇ Download Excel',
                className: 'btn btn-success'
            }
        ]
    });
});
