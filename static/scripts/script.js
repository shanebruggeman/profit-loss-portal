$(document).ready(function() {
	$("#foot01").innerHTML =
	"<p>&copy; " + new Date().getFullYear() + " ProfitLossPortal</p>";
 
 // 	$("#nav01").innerHTML =
	// "<ul id='menu'>" +
	// "<li><a href='index'>Home</a></li>" +
	// "<li><a href='customers'>Data</a></li>" +
	// "<li><a href='about'>About</a></li>" +
	// "</ul>";

	$('#datatable').tablesorter();
	$('#fromdate').datepicker();
	$('#todate').datepicker();


	$('#date_selectors').hide();

	$('.date_radio').on('click', function(e) {
		if ($('#selected_date:checked').val()) {
			$('#date_selectors').show();
		}
		else {
			$('#date_selectors').hide();
		}
	});

	$('#report_btn').on('click', function(e) {
		window.location.replace("localhost:5000/customers");
	});
});