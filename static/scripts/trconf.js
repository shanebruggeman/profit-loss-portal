$(document).ready(function () {
	// $('#myChart').hide();
    var canvas_html = '<canvas id="myChart" class="col-sm-6"></canvas>';
    $('#hideChartButton').hide();

	// Setup - add a text input to each header cell
	$('#datatable thead th').each(function() {
		var title = $('#datatable thead th').eq($(this).index()).text();
		$(this).append('<input type=\'text\' placeholder=\'Search ' + title + '\'/>');
	});

	// DataTable
	var datatable = $('#datatable').DataTable();
	$('#datatable_filter').hide();

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

	$('#hideChartButton').on('click', function () {
		$('#chart_container').html("");
		$('#hideChartButton').hide();
	});

	$('#getChartButton').on('click', function() {
	// $('#.sec_sym_link').on('click', function() {
	// 	stock_sym = 
      $.getJSON($SCRIPT_ROOT + '/_get_transactions', {
        account: $('input[name="account_id"]').val(),
        stock_sym: $('input[name="stock_sym"]').val()
      }, function(data) {
		$('#hideChartButton').show();
        var data_list = data.values;
        var label_list = data.labels;
        // alert(data_list + label_list);
        var graph_data = {
    		labels: label_list,
    		datasets: [
        		{
            		label: "My First dataset",
            		fillColor: "rgba(220,220,220,0.2)",
            		strokeColor: "rgba(220,220,220,1)",
            		pointColor: "rgba(220,220,220,1)",
            		pointStrokeColor: "#fff",
            		pointHighlightFill: "#fff",
            		pointHighlightStroke: "rgba(220,220,220,1)",
            		data: data_list
        		}
        	]
		};
		var options = {
			scaleShowGridLines : true
		};

		$('#chart_container').html(canvas_html);

        var ctx = $("#myChart").get(0).getContext("2d");
		var myNewChart = new Chart(ctx).Line(graph_data, options);
		// $('#myChart').attr('width', 400)
		// $('#myChart').attr('height', 400)
		// $('#myChart').show();
      });
      return false;
    });
});