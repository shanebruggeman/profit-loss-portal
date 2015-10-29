$(document).ready(function() {

	$("#foot01").innerHTML =
	"<p>&copy; " + new Date().getFullYear() + " ProfitLossPortal</p>";

	$('.date_radio').on('click', function(e) {
		if ($('#selected_date:checked').val()) {
			$('#date_selectors').show();
		}
		else {
			$('#date_selectors').hide();
		}
	});
});