
$(document).ready(function() {
	document.getElementById("foot01").innerHTML =
	"<p>&copy; " + new Date().getFullYear() + " ProfitLossPortal</p>";
 
 document.getElementById("nav01").innerHTML =
	"<ul id='menu'>" +
	"<li><a href='index'>Home</a></li>" +
	"<li><a href='customers'>Data</a></li>" +
	"<li><a href='about'>About</a></li>" +
	"</ul>";

	$('#datatable').tablesorter();
});