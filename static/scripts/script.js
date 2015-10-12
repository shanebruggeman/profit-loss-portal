$(document).ready(function() {
	$("#foot01").innerHTML =
	"<p>&copy; " + new Date().getFullYear() + " ProfitLossPortal</p>";

	// Setup - add a text input to each header cell
	$('#datatable thead th').each(function() {
		var title = $('#datatable thead th').eq($(this).index()).text();
		$(this).append('<input type=\'text\' placeholder=\'Search ' + title + '\'/>');
	});

	// DataTable
	var datatable = $('#datatable').DataTable();
	$('#datatable_filter').css('display: none');

	// Apply the search
	datatable.columns().eq(0).each(function(colIdx) {
		$('input', datatable.column(colIdx).header()).on('keyup change', function() {
			datatable
			.column(colIdx)
			.search(this.value)
			.draw();
		});

		$('input', datatable.column(colIdx).header()).on('click', function(e) {
			e.stopPropagation();
		});
	});
});