var ws = undefined;
var signal_info = {};

function update_MA(value) {
    if (value != '') {
        $('#moving-average-filter label').text('MA Filter (' + value + ')');
        $('#MA-slider').val(value);
        ws.send("MAF " + value);
    }
    else {
        $('#moving-average-filter label').text('MA Filter');
    }
}

$(function() {

	function insert_signal(name) {
		var panel = $('#signal-panel .ui.form');
		var id = signal_info[name].label, color = signal_info[name].color;
		panel.append('<div class="field"><div id="signal-toggle-' + id + '" class="ui toggle checkbox"><input type="checkbox" checked /><label><i style="color: ' + color + '" class="sign icon"></i>' + id + '</label></div></div>');
	}

	var number_of_signal = 200;
	var plot = null;
	var legends = null;

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
				'label': data[i].label,
				'color': data[i].color
			}
			insert_signal(data[i].label);
		}

		$("[id^='signal-toggle-']").click(function () {
		});

		$('.ui.checkbox').checkbox();

	}

    // Websocket connection
    ws = new WebSocket("ws://localhost:8888/ws");

    ws.onmessage = function (evt) {

		if (plot == null) {
			var data = JSON.parse(evt.data);
			data = data.signal;
			init_draw(data);
		}

		var data = JSON.parse(evt.data);
		data = data.signal;
		// set data for plot
		plot.setData(data);
		// redraw graph
		plot.draw();
		// uplate legend
		update_legend();
	};


	var latest_pos = null;
	var update_legend_timeout = null;

	function update_legend() {

		if (latest_pos == null) {
			return;
		}

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
			update_legend_timeout = setTimeout(update_legend, 50);
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
            update_MA('');
			ws.send("MAF 0");
		}
		else {
			$(this).addClass('active');
            update_MA($('#MA-slider').val());
            $('#MA-slider').toggle('fast');
            $('#MA-slider').attr('disabled', false);
		}
	});

    $('.ui.checkbox').checkbox();


});
