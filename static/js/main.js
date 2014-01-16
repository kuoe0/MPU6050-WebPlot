
$(function() {

	var plot = null;
	var ws = undefined;
	var signal_info = {};

	function insert_signal(name) {
		var panel = $('#signal-panel .ui.grid');
		var id = signal_info[name].label, color = signal_info[name].color;
		panel.append('<div id="signal-panel-' + id + '" class="row"><div class="five wide column"><div id="signal-toggle-' + id + '" class="ui toggle checkbox"><input type="checkbox" checked /><label><i style="color: ' + color + '" class="sign icon"></i>' + id + '</label></div></div><div class="three wide column"><input class="signal-value" readonly/></div></div>');
	}

	function init_draw(data) {

		plot = $.plot('#signal-plot', data, {
			series: { 
				lines: { show: true, lineWidth: 1.5 },
				shadowSize: 0 },
			crosshair: { mode: "x" },
			grid: { hoverable: true, autoHighlight: false },
			xaxis: { show: false },
			yaxis: { min: -36000, max: 36000 },
			legend: { show: false}
		});

		data = plot.getData();

		for (var i = 0; i < data.length; ++i) {
			signal_info[data[i].label] = {
				'idx': i,
				'label': data[i].label,
				'color': data[i].color,
				'show': true
			}
			insert_signal(data[i].label);
		}

		$("[id^='signal-toggle-']").click(function () {
			var data = plot.getData();
			var label = $(this).attr('id').replace(/signal-toggle-/, '');
			var idx = signal_info[label].idx;
			data[idx].lines.show = !data[idx].lines.show;
			signal_info[label].show = !signal_info[label].show;
			plot.setData(data);
			plot.draw();
		});

		$('.ui.checkbox').checkbox();

	}

    // Websocket connection
    ws = new WebSocket("ws://localhost:8888/ws");

    ws.onmessage = function (evt) {

		var data = JSON.parse(evt.data);
		data = data.signal;

		if (plot == null) {
			init_draw(data);
		}
		else {

			for (var i = 0; i < data.length; ++i) {
				var label = data[i].label;
				data[i]['lines'] = {};
				data[i].lines['show'] = signal_info[label].show;
				data[i]['color'] = signal_info[label].color;
			}
			// set data for plot
			plot.setData(data);
			// redraw graph
			plot.draw();
		}
		// uplate value of signal
		update_signal_value();
	};


	var latest_pos = null;
	var update_signal_value_timeout = null;

	function update_signal_value() {

		if (latest_pos == null) {
			return;
		}

		update_signal_value_timeout = null;

		var pos = latest_pos;
		var axes = plot.getAxes();

		if (pos.x < axes.xaxis.min || pos.x > axes.xaxis.max ||
			pos.y < axes.yaxis.min || pos.y > axes.yaxis.max) {
			return;
		}

		var dataset = plot.getData();

		for (var i = 0; i < dataset.length; ++i) {
			var label = dataset[i].label;
			var series = dataset[i];

			var idx = Math.floor(pos.x);

			var p1 = series.data[idx], p2 = series.data[idx + 1];
			var ret = null;

			ret = (p1 == null) ? p2[1] : p1[1];

			$('#signal-panel-' + label + ' .signal-value').val(ret.toFixed(0));
		}
	};

	$('#signal-plot').bind("plothover", function (event, pos, iten) {
		latest_pos = pos;
		if (!update_signal_value_timeout) {
			update_signal_value_timeout = setTimeout(update_signal_value, 50);
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
            $('#MA-slider').toggle('slow');
            $('#MA-slider').attr('disabled', true);
			$('#MA-value').text('');
			ws.send("MAF 0");
		}
		else {
			var value = $('#MA-slider').val();
			$(this).addClass('active');
			$('#MA-value').text('(' + value + ')');
            $('#MA-slider').toggle('fast');
            $('#MA-slider').attr('disabled', false);
		}
	});

	$('#MA-slider').change(function () {
		var value = $(this).val();
		$('#MA-value').text('(' + value + ')');
		$('#MA-slider').val(value);
		ws.send("MAF " + value);
	});

    $('.ui.checkbox').checkbox();


});
