$(function() {

	var number_of_signal = 200;
	// set update interval in micro second (ms)
	var updateInterval = 1;

    // Websocket connection
    var ws = new WebSocket("ws://localhost:8888/ws");
    ws.onmessage = function (evt) {
        var data = JSON.parse(evt.data);
        // append value after each label
        for (var i = 0; i < data.signal.length; ++i) {
            data.signal[i].label = data.signal[i].label + " = 0";
        }
        // set data for plot
        plot.setData(data.signal);
        // redraw graph
        plot.draw();
        // uplate legend
        uplate_legend();
    };


	var signal_type = ['x-acc = 0', 'y-acc = 0', 'z-acc = 0', 'x-gyro = 0', 'y-gyro = 0', 'z-gyro = 0'];
	var init = [];

	for (var i = 0; i < 6; ++i) {
		var init_signal = [];
		for (var j = 0; j < number_of_signal; ++j) {
			init_signal.push([j, 0]);
		}
		init.push({
			label: signal_type[i],
			data: init_signal
		});
	}

	var plot = $.plot('#signal-plot', init, {
		series: { 
			lines: { show: true, lineWidth: 1 },
			shadowSize: 0 },
		crosshair: { mode: "x" },
		grid: { hoverable: true, autoHighlight: false },
		xaxis: { show: false },
		yaxis: { min: -36000, max: 36000 },
		legend: { position: "sw" }
	});

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


});
