$(function() {

	function get_series_data(data) {
		// append value after each label
		for (var i = 0; i < data.signal.length; ++i) {
			data.signal[i].label = data.signal[i].label + " = 0";
		}

		return data.signal;
	}


	var number_of_signal = 200;
	var moving_average_status = false;
	var plot = null;

	function init_draw(data) {

		plot = $.plot('#signal-plot', data, {
			series: { 
				lines: { show: true, lineWidth: 1.5 },
				shadowSize: 0 },
			crosshair: { mode: "x" },
			grid: { hoverable: true, autoHighlight: false },
			xaxis: { show: false },
			yaxis: { min: -36000, max: 36000 },
			legend: { position: "sw" }
		});

	}

    // Websocket connection
    var ws = new WebSocket("ws://localhost:8888/ws");

    ws.onmessage = function (evt) {

		if (plot == null) {
			var data = JSON.parse(evt.data);
			data = get_series_data(data);
			init_draw(data);
		}

		var data = JSON.parse(evt.data);
		data = get_series_data(data);
		// set data for plot
		plot.setData(data);
		// redraw graph
		plot.draw();
		// uplate legend
		uplate_legend();

	};

	var legends = $('#signal-plot .legendLabel');

	var latest_pos = null;
	var update_legend_timeout = null;

	function uplate_legend() {
		update_legend_timeout = null;
		var pos = latest_pos;

		var axes = plot.getAxes();

		if (pos.x < axes.xaxis.min || pos.x > axes.xaxis.max ||
			pos.y < axes.yaxis.min || pos.y > axes.yaxis.max) {
			return;
		}

		var dataset = plot.getData();

		for (var i = 0; i < dataset.length; ++i) {
			var series = dataset[i];

			var idx = Math.floor(pos.x);

			var p1 = series.data[idx], p2 = series.data[idx + 1];
			var ret = null;

			ret = (p1 == null) ? p2[1] : p1[1];
			var new_label = series.label.replace(/=.*/, "= " + ret);
			legends.eq(i).text(new_label);
		}
	};

	$('#signal-plot').bind("plothover", function (event, pos, iten) {
		latest_pos = pos;
		if (!update_legend_timeout) {
			update_legend_timeout = setTimeout(uplate_legend, 50);
		}
	});

	$('#clear-btn').click(function () {
		ws.send("clear");
	});

	$('#status-btn').click(function () {
		// close connection
		if ($(this).hasClass('active')) {
			$(this).removeClass('active');
			$(this).empty();
			$(this).append("<i class='play icon'></i>");
			ws.send("pause");
		}
		// open connection
		else {
			$(this).addClass('active');
			$(this).empty();
			$(this).append("<i class='pause icon'></i>");
			ws.send("play");
		}
	});

	$('#moving-average-filter').click(function () {
		if ($(this).hasClass('active')) {
			$(this).removeClass('active');
			moving_average_status = false;
			ws.send("MAF 0");
		}
		else {
			$(this).addClass('active');
			moving_average_status = true;
			ws.send("MAF 10");
		}
	});


});
