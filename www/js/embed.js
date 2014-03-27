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

function getCurrencySymbol(curCode) {
	var symbol = '';
	var codes = config.currencySymbols[curCode];
	if (codes) {
		for (var i = 0; i < codes.length; i++) {
			symbol += String.fromCharCode(parseInt(codes[i], 16));
		}
	}
	return symbol;
}

var ba_widget = function (html_id, currency) {
	var self = this;
	self._protocol = window.location.protocol;
	self._wrapper_id = html_id;
	self._currencyCode = currency;
	self._apiHistoryIndexUrl = 'https://api.bitcoinaverage.com/history/';
	self._data24hURL = self._apiHistoryIndexUrl + self._currencyCode + '/per_minute_24h_sliding_window.csv';

	self.init = function () {
		// jQuery is required for different stuff
		if (!window.jQuery) {
			console.warn('jQuery is required');
			return;
		}
		self.createWidget();
	}

	self._ajaxCall = function(url, callback) {
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

	self._parseDate = function(dateString) {
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

	self._template =
		'<style>\
			@import url(http://fonts.googleapis.com/css?family=Open+Sans:400,600,400italic,600italic&subset=latin,cyrillic-ext);\
			.ba-wrapper {background: #f7f7f7; border-top: 2px solid #dadada; border-bottom: 2px solid #ccc; font-family: Open Sans; position: relative;}\
			.ba-rate {display: inline-block;}\
			.ba-cur-symbol {color: #4f4f4f; font-size: 22px; font-weight: bold; display: inline-block; margin-left: 6px;}\
			.ba-range-int {color: #2f7ed8; display: inline-block; font-size: 28px; font-weight: bold; margin-left: 3px;}\
			.ba-range-frac {color: #2f7ed8; display: inline-block; font-size: 22px; font-weight: bold;}\
			.ba-cur-code {color: #4f4f4f; font-size: 22px;}\
			.ba-text {font-size: 0.8em; margin-left: 3px;}\
			.ba-text a {color: #609de1; text-decoration: none;}\
			.ba-text a:hover {text-decoration: underline;}\
			.ba-logo {display: inline-block; bottom: 1px; right: 3px; position: absolute;}\
		</style>\
		<div class="ba-wrapper">\
			<div class="ba-chart"></div>\
			<div class="ba-rate">\
				<span class="ba-cur-symbol"></span><!--\
				--><span class="ba-range-int"></span><!--\
				--><span class="ba-range-frac"></span><!--\
				-->&nbsp;<span class="ba-cur-code"></span>\
			</div>\
			<div class="ba-text">BitcoinAverage <a>price index</a></div>\
			<div class="ba-logo"><a href="https://bitcoinaverage.com/"><img src="img/logo_chart.png" alt="bitcoinaverage.com"></a></div>\
		</div>';

	self.createWidget = function () {
		self._widget = $('#' + self._wrapper_id);
		self._widget.html(self._template);
		self._widget.find('.ba-text a').attr('href', 'https://bitcoinaverage.com/#' + self._currencyCode);
		var widget_total_height = self._widget.height();
		var chart_height = widget_total_height - 56;  // computed manually
		self._widget.find('.ba-chart').height(chart_height);
		var data = []
		self._widget.find('.ba-chart').highcharts("StockChart", {
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
				valuePrefix: getCurrencySymbol(self._currencyCode) + ' ',
				xDateFormat: "%H:%M"
			},
			credits: {enabled : false},


			chart : {
				backgroundColor: "#f7f7f7",
				events : {
					load : function () {
						var highchart = this;
						self.updateData(highchart);
						setInterval(function() {
							self.updateData(highchart);
						}, 60000);
					}
				},
				panning:false,
				spacing:[0, 0, 0, 0]
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
				data.push([
					self._parseDate(values[0]).getTime(),
					parseFloat(values[1])
				]);
			});
			highchart.series[0].setData(data);

			var value = data[data.length-1][1];
			var integer = Math.floor(data[data.length-1][1]);
			var fraction = Math.round((value % 1)*100);
			$('.ba-range-int').html(integer + ".");
			if(fraction >= 10) {
				$('.ba-range-frac').html(fraction);
			} else {
				$('.ba-range-frac').html("0" + fraction);
			}
			$('.ba-cur-symbol').html(getCurrencySymbol(self._currencyCode));
			$('.ba-cur-code').html(self._currencyCode);
		});
		return data;
	}
	self.init();
}
