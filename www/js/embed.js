/*
 * Usage:
 * <div id="embed"></div>
 * <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
 * <script src="https://code.highcharts.com/stock/highstock.js"></script>
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
			'<div style="background:#f7f7f7; border-top:2px solid #dadada;border-bottom:2px solid #ccc;position:relative;">',
				'<div class="ba-chart"></div>',
				'<div style="display: inline-block">',
					'<span style = "color: #4f4f4f; font-size: 24px; font-weight: bold; display: inline-block; margin-left: 6px;">$</span>',
					'<span id="ba-range-int" style="color: #2f7ed8; font-size: 30px; font-weight: bold; display: inline-block; margin-left: 6px;"><!--',
					'--></span><!--',
					'--><span id="ba-range-frac" style="color: #2f7ed8; font-size: 24px; font-weight: bold; display: inline-block; ">',
					'</span>',
					'<div style = "margin-left:6px;font-family: "Open Sans","Helvetica Neue",Helvetica,Arial,sans-serif;">BitcoinAverage <span style = "color:#609de1;">price index</span></div>',
				'</div>',
				'<div style="display: inline-block; position:absolute; right:10px;bottom:6px;">',
					'<a href="https://bitcoinaverage.com/" alt="bitcoinaverage.com"><img src="img/logo_xsmall.png"/></a>',
				'</div>',
			'</div>',
		].join('\n')
	}

	this.createWidget = function () {
		self._widget = $('#' + self._wrapper_id);
		self._widget.html(self._template);
		var widget_total_height = self._widget.height();
		var chart_height = widget_total_height - 60;  // computed manually
		$('#' + self._wrapper_id + ' .ba-chart').height(chart_height);
		var data = []
		$('#' + self._wrapper_id + ' .ba-chart').highcharts("StockChart", {
			rangeSelector: {enabled: false},
			xAxis:{
				labels:{enabled: false},
				tickWidth:0,
				lineWidth:0
			},
			yAxis:{
				labels:{enabled: false},
				gridLineWidth: 0
			},
			scrollbar: {enabled: false},
			navigator: {enabled: false},
			exporting: {enabled: false},
			tooltip: {
				backgroundColor: 'transparent',
				borderWidth: 0,
				borderRadius: 0,
				headerFormat: '{point.key} ',
				pointFormat: ' | <b>{point.y}</b>',
				crosshairs: false,
				positioner: function () {
					return { x: 0, y: 0 };
				},
				shadow: false,
				valueDecimals: 2,
				valuePrefix: "$",
				xDateFormat: "%H:%M"
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
				backgroundColor: "#f7f7f7",
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

			var value = data[data.length-1][1];
			var integer = Math.floor(data[data.length-1][1]);
			var fraction = Math.round((value % 1)*100);
			document.getElementById('ba-range-int').innerHTML = integer+".";
			if(fraction >= 10) {
				document.getElementById('ba-range-frac').innerHTML = fraction;
			} else {
				document.getElementById('ba-range-frac').innerHTML = "0" + fraction;
			}
			
		});
		return data;
	}

	self.init()
}

var _widget = new BAWidget();
