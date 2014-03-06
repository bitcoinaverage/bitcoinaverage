/*
 * Usage:
 * <div id="embed"></div>
 * <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
 * <script src="http://code.highcharts.com/stock/highstock.js"></script>
 * <script src="embed.js"></script>
 *
 */

function _maxelm(v) {
	var m = v[0][1];
	for (var i=1; i < v.length; i++) {
		m = Math.max(m, v[i][1]);
	}
	return m;
}

function _minelm(v) {
	var m = v[0][1];
	for (var i=1; i < v.length; i++) {
		m = Math.min(m, v[i][1]);
	}
	return m;
}

var BAWidget = function () {
	this._protocol = window.location.protocol;
	this._wrapper_id = 'ba-embed';
	this._apiHistoryIndexUrl = 'https://api.bitcoinaverage.com/history/';
	this._currencyCode = 'USD'  // for now
	this._data24hURL = this._apiHistoryIndexUrl + this._currencyCode + '/per_minute_24h_sliding_window.csv';
	var self = this

	this.init = function () {
		// jQuery is required for different stuff
		if (!window.jQuery) {
			console.warn('jQuery is required');
			return;
		}
		this.createTemplate();
		this.createWidget();
	}

	this._ajaxCall = function(url, callback) {
		if (typeof callback == 'undefined') {
			callback = function(data){};
		}

		if (window.XDomainRequest) { //IE9-10 implements crossdomain AJAX this way only
			var xhr = new window.XDomainRequest();
			xhr.open('GET', url, true);
			xhr.onload = function() {
				callback(xhr.responseText);
			};
			xhr.send();
		} else {
			$.get(url, callback);
		}
	}

	this._parseDate = function(dateString) {
		var parts = dateString.split(' ');
		var dateParts = parts[0].split('-');
		if (typeof parts[1] != 'undefined') {
		var timeParts = parts[1].split(':');
		} else {
		var timeParts = [0,0,0];
		}
		var result = new Date(dateParts[0], dateParts[1]-1, dateParts[2], timeParts[0], timeParts[1], timeParts[2]);
		return result;
	}

	this.createTemplate = function () {
		this._template = [
			'<div class="ba-chart"></div>',
			'<div>',
				'<span style="color: #2f7ed8; font-size: 10px; display: inline-block; margin-left: 6px;">',
					'High: <span id="ba-range-high"></span>',
				'</span>',
				'<span style="color: #2f7ed8; font-size: 10px; display: inline-block; margin-left: 6px;">',
					'Low: <span id="ba-range-low"></span>',
				'</span>',
			'</div>',
		].join('\n')
	}

	this.createWidget = function () {
		self._widget = $('#' + self._wrapper_id);
		self._widget.html(self._template);
		var widget_total_height = self._widget.height();
		var chart_height = widget_total_height - 20;  // 20 computed manually
		$('#' + self._wrapper_id + ' .ba-chart').height(chart_height);
		var data = []
		$('#' + self._wrapper_id + ' .ba-chart').highcharts("StockChart", {
			rangeSelector: {enabled: false},
			xAxis:{labels:{enabled: false}},
			yAxis:{labels:{enabled: false}},
			scrollbar: {enabled: false},
			navigator: {enabled: false},
			exporting: {enabled: false},
			tooltip: {
				backgroundColor: 'transparent',
				borderWidth: 0,
				borderRadius: 0,
				//headerFormat: '{point.key} ',
				pointFormat: ' | <b>{point.y}</b>',
				crosshairs: false,
				positioner: function () {
					return { x: 0, y: 0 };
				},
				shadow: false,
				valueDecimals: 2
			},
			credits: {enabled : false},

			plotOptions: {
				series: {
					dataGrouping: {
						groupPixelWidth: 1,
						units: [
							['minute', [1, 2, 5, 10, 15, 22, 30]],
							['hour', [1, 2, 3, 6, 8, 10, 12]],
							['day', [1]]
							]
					}
				}
			},

			chart : {
				events : {
					load : function () {
						highchart = this
						self.updateData(highchart);
						setInterval(function() {
							self.updateData(highchart);
						}, 60000);
					}
				}
			},
			series : [{
				data : data,
			}]
		})
	}

	self.updateData = function (highchart) {
		var data = [];
		self._ajaxCall(self._data24hURL, function (csv) {
			$.each(csv.split('\n').slice(-60), function(i, line) {
				var values = line.split(',');
				if (i == 0 || line.length == 0 || values.length != 2) {
					return;
				}
				data.push([self._parseDate(values[0]).getTime(),
					   parseFloat(values[1])]);
			});
			highchart.series[0].setData(data);
			document.getElementById('ba-range-high').innerHTML = _maxelm(data);
			document.getElementById('ba-range-low').innerHTML = _minelm(data);
		});
		return data;
	}

	self.init()
}

var _widget = new BAWidget();
