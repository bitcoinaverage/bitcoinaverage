var legendSlots = 20;
var majorCurrencies = 6; //first X currencies in the config are major

var API_data = {};
if (typeof config.apiIndexUrl == 'undefined' || config.apiIndexUrl == ''){
    alert('API URL config value empty!');
}
if (config.apiIndexUrl[config.apiIndexUrl.length-1] != '/') {
    config.apiIndexUrl = config.apiIndexUrl + '/';
}
var API_all_url = config.apiIndexUrl+'all';

if (config.apiHistoryIndexUrl[config.apiHistoryIndexUrl.length-1] != '/') {
    config.apiHistoryIndexUrl = config.apiHistoryIndexUrl + '/';
}

var active_API_URL = API_all_url;

var legendClickStatus = false;
var firstRenderDone = false;
var fiatExchangeRates = [];
var timeGap = 0; //actual time is fetched from remote resource, and user's local time is adjusted by X seconds to be completely exact

var callAPI = function(callback){
    if (typeof callback == 'undefined'){
        callback = renderAll;
    }

    if (window.XDomainRequest) {

        var xhr = new window.XDomainRequest(); //IE9-10 implements crossdomain AJAX this way only

        xhr.open('GET', active_API_URL, true);

        xhr.onload = function() {
            var result = JSON.parse(xhr.responseText);
            callback(result);
        };
        xhr.send();
    } else {

        $.getJSON(active_API_URL, callback);
    }
}

var renderAll = function(result, status, responseObj){

    result = adjustScale(result);

    //responseObj is not available in IE
    if(typeof responseObj == 'object'){
        getTimeGap(responseObj.getAllResponseHeaders());
    }

    API_data = result;

    $('#currency-sidebar li[id^="slot"] a').hide();

    for(var slotNum in config.currencyOrder){
        var currencyCode = config.currencyOrder[slotNum];
        renderRates(currencyCode, result[currencyCode], slotNum);
    }

    renderSecondsSinceUpdate();
    if (!firstRenderDone) {
        $('body').show();
        //@TODO: what this peace of code is doing?
//        var currentHash = window.location.hash;
//        currentHash = currentHash.replace('#', '');
//        currentHash = currentHash.split('|');
//
//        if (currentHash.length == 2 && currentHash[1] == 'nomillibit'){
//            $('.legend-curcode').click();
//        }
//
//        currentHash = currentHash[0];
//
//        var global_average_default = $.cookie('global-average');
//
//        if (currentHash != '' && $('#currency-sidebar li[data-currencycode="'+currentHash+'"]').size() > 0) {
//            $('#currency-navtabs li[data-currencycode="'+currentHash+'"]').click();
//        } else if (typeof global_average_default != 'undefined') {
//            $('#currency-navtabs li[data-currencycode="'+global_average_default+'"]').click();
//        } else {
//            $('#slot0-link').click();
//        }
        $('#slot0-link').click();
        firstRenderDone = true;
    }
   renderLegend(legendClickStatus);
}


var lastGlobalAvgValue = 0;
var renderRates = function(currencyCode, currencyData, slotNum){
    $('#slot'+slotNum+'-link').attr('data-currencycode', currencyCode);

    var slotLegendLink_a = $('#slot'+slotNum+'-link a');
    slotLegendLink_a.text(currencyCode);
    slotLegendLink_a.attr('href', '#'+currencyCode);
    slotLegendLink_a.attr('title', fiatCurrencies[currencyCode]['name']);
    slotLegendLink_a.show();


    $('#slot'+slotNum+'-box').attr('data-currencycode', currencyCode);
    $('#slot'+slotNum+'-box').attr('title', fiatCurrencies[currencyCode]['name']);
    $('#slot'+slotNum+'-curcode').text(currencyCode);

    var dataChanged = false;
    dataChanged = (dataChanged || $('#slot'+slotNum+'-last').text() != currencyData.averages.last);
    dataChanged = (dataChanged || $('#slot'+slotNum+'-ask').text() != currencyData.averages.ask);
    dataChanged = (dataChanged || $('#slot'+slotNum+'-bid').text() != currencyData.averages.bid);
    $('#slot'+slotNum+'-last').text(currencyData.averages.last.toFixed(config.precision));
    $('#slot'+slotNum+'-ask').text(currencyData.averages.ask.toFixed(config.precision));
    $('#slot'+slotNum+'-bid').text(currencyData.averages.bid.toFixed(config.precision));


    var global_avg_currency = $.cookie('global-average');
    if ((typeof global_avg_currency != 'undefined' && currencyCode == global_avg_currency)
        || (typeof global_avg_currency == 'undefined' && currencyCode == 'USD') ){

        $('#global-last').html(currencyData.global_averages.last.toFixed(config.precision));
        $('#global-curcode').html(currencyCode);
        $('#global-bid').html(currencyData.global_averages.bid.toFixed(config.precision));
        $('#global-ask').html(currencyData.global_averages.ask.toFixed(config.precision));

        if (lastGlobalAvgValue == 0) {
            lastGlobalAvgValue = currencyData.global_averages.last;
        } else {
            if (currencyData.global_averages.last > lastGlobalAvgValue) {
                $('#global-avg-arrowup').show();
                $('#global-avg-arrowdown').hide();
            } else if (currencyData.global_averages.last < lastGlobalAvgValue) {
                $('#global-avg-arrowup').hide();
                $('#global-avg-arrowdown').show();
            }
            lastGlobalAvgValue = currencyData.global_averages.last;
        }
    }


    if (dataChanged) {
        var flashingFigures = $('#slot'+slotNum+'-last, #slot'+slotNum+'-ask, #slot'+slotNum+'-bid');
        flashingFigures.css({ 'opacity' : 0.5});
        flashingFigures.animate({ 'opacity' : 1 }, 500);
    }
}
var sort = function (list) {

    var comparisons = 0,
        swaps = 0;

    for (var i = 0, swapping; i < list.length - 1; i++) {
        comparisons++;
        if (list[i] > list[i + 1]) {
            // swap
            swapping = list[i + 1];

            list[i + 1] = list[i];
            list[i] = swapping;
            swaps++;
        };
    };

    return list;
};
var orderByVolume = function(a, b) {
    if (a['global_averages']['volume_percent'] == b['global_averages']['volume_percent'] ) {
        return 0;
    } else if (a['global_averages']['volume_percent'] < b['global_averages']['volume_percent']) {
        return 1;
    }
    return -1;
}

var renderGlobalAverageData = function(apiData, currency)
{

   var globalAverageData = $.map(apiData, function(value, index) {
    value['currency'] = index;
    return [value];
   });

   globalAverageData.splice(-2,2); // delete timestamp and ignored_exchanges from data
   globalAverageData.sort(orderByVolume);


   var html='';
   var majorCurrency = config.majorCurrencies;
   $.each(globalAverageData, function(i, item) {

       var currencyCode   = item['currency'];
       var volumeBtc      = item['global_averages']['volume_btc'].toFixed(config.precision);
       var volumePercent  = item['global_averages']['volume_percent'].toFixed(2);
       var lastPrice      = item['global_averages']['last'].toFixed(config.precision);
       var crossPrice     = (fiatCurrencies[currency]['rate'] / fiatCurrencies[currencyCode]['rate']) * lastPrice;
       crossPrice = crossPrice.toFixed(config.precision);
       var cookieHideLink = $.cookie("global-average-table");
       var oneRow = $('<tr></tr>');
       if (i > majorCurrency) {
           if(cookieHideLink == null) cookieHideLink = 'hidden';
           if ( cookieHideLink == 'hidden'){
                oneRow.addClass('secondary-global-avg-row hidden');
                $('#show-more-currencies-in-global-avg-table').text('more');
           } else if(cookieHideLink =='collapsed'){
               oneRow.addClass('secondary-global-avg-row');
               $('#show-more-currencies-in-global-avg-table').text('less');
           }
       }
       oneRow.attr('id', 'currency-name-'+currencyCode);
       var spanLegendCurrency = $('<span></span>');
       var tdLegendCurrency = $('<td></td>');

       oneRow.attr('id' , 'global-average-data' + currencyCode);

        /* Currency NAME */
       spanLegendCurrency.text(currencyCode);
       tdLegendCurrency.attr('class', 'legend-currency');
       tdLegendCurrency.append(spanLegendCurrency);
       oneRow.append(tdLegendCurrency);

       /* Volume Percent */
       var spanVolumePercent = $('<span></span>');
       var tdVolumePercent = $('<td></td>');
       spanVolumePercent.text(volumePercent);
       tdVolumePercent.attr('class', 'legend-volume_percent');
       tdVolumePercent.append(spanVolumePercent);
       oneRow.append(tdVolumePercent);

        /* Volume BTC */
       var spanVolumeBtc = $('<span></span>');
       var tdVolumeBtc = $('<td></td>');
       spanVolumeBtc.text(volumeBtc);
       tdVolumeBtc.attr('class', 'legend-volume_btc');
       tdVolumeBtc.append(spanVolumeBtc);
       oneRow.append(tdVolumeBtc);

        /* Last Price */
       var spanLastPrice = $('<span></span>');
       var tdLastPrice = $('<td></td>');
       spanLastPrice.text(volumeBtc);
       tdLastPrice.attr('class', 'legend-price text-right');
       tdLastPrice.append(lastPrice + ' ' + currency);
       oneRow.append(tdLastPrice);

       /* Cross Price */
       var spanCrossPrice = $('<span></span>');
       var tdCrossPrice = $('<td></td>');
       var insLegendCurcode = $('<ins></ins>');

       spanCrossPrice.text(crossPrice+' ');
       insLegendCurcode.text(currency);
       insLegendCurcode.attr('class', 'legend-curcode');
       tdCrossPrice.attr('class', 'legend-last-cross-price text-right');
       tdCrossPrice.append(spanCrossPrice);
       tdCrossPrice.append(insLegendCurcode);
       oneRow.append(tdCrossPrice);

       html += oneRow.outerHTML();
   });

   var table    = $('#global-average-data-table');
   table.children('tbody').html(html);
}



var renderLegend = function(currencyCode){
    renderGlobalAverageData(API_data, currencyCode);

    $('#global-curcode').text(currencyCode);

    var exchangeArray = [];
    var currencyData = API_data[currencyCode];

    var index = 0;
    for(var exchange_name in currencyData.exchanges){
        currencyData.exchanges[exchange_name]['name'] = exchange_name;
        exchangeArray[index] = currencyData.exchanges[exchange_name];
        index++;
    }

    exchangeArray.sort(function(a, b){
        if(parseFloat(a.volume_percent) < parseFloat(b.volume_percent)){
            return 1;
        } else {
            return -1;
        }
    });

    if (legendClickStatus == currencyCode){
        document.title = API_data[currencyCode].global_averages.last.toFixed(config.precision)+' '+currencyCode+' | BitcoinAverage - independent bitcoin price';
    }

    $('.legend-curcode').text(currencyCode);
    $('.bitcoin-calc .currency-label').text(currencyCode);

    var last = currencyData.averages.last.toFixed(config.precision);
    $('#legend-last').html(last);

    var bitCoinInputVal  = $('#bitcoin-input').toNumber().val();
    var fiatCalcVaule = (last * bitCoinInputVal).toFixed(2);
    $('#currency-input').val(fiatCalcVaule);

    $('#global-last').html(currencyData.averages.last.toFixed(config.precision));
    $('#legend-bid').html(currencyData.averages.bid.toFixed(config.precision));
    $('#legend-ask').html(currencyData.averages.ask.toFixed(config.precision));
    $('#legend-total-volume').html(currencyData.averages.total_vol.toFixed(2));

    if (typeof currencyData.averages['24h_avg'] != 'undefined') {
        $('#legend-24h-avg').html(currencyData.averages['24h_avg'].toFixed(config.precision));
        $('#legend-24h-avg-container').show();
    } else {
        $('#legend-24h-avg-container').hide();
    }


    $('#legend-ignored-table').hide();
    if ($(API_data.ignored_exchanges).countObj() > 0) {
        $('#legend-ignored-table').show();
        $('#legend-ignored-table tr[id^="legend-ignored-slot"]').hide();
        var index = 0;
        for (var exchange_name in API_data.ignored_exchanges) {
            $('#legend-ignored-slot'+index+'-name').text(exchange_name);
            $('#legend-ignored-slot'+index+'-reason').html(API_data.ignored_exchanges[exchange_name]);
            $('#legend-ignored-slot'+index+'-box').show();
            index++;
        }
    }

    $('.legend-currency-code-update').html(fiatCurrencies[currencyCode]['name']);

    $('#legend-global-average').html(currencyData.global_averages.last.toFixed(config.precision))
    $('#legend-global-volume-percent').html(currencyData.global_averages.volume_percent.toFixed(2))


    for(var slotNum=0;slotNum<legendSlots;slotNum++){
        $('#legend-slot'+slotNum).toggle(false);
    }
    $('#legend-other').toggle(false);

    var otherCount = 0;
    var otherPercent = 0;
    var otherVolume = 0;

    $('#legend-api-unavailable-note').hide();
    $('#legend-api-down-note').hide();

    $('#24h-sliding-link').attr('href', config.apiHistoryIndexUrl+currencyCode+'/per_minute_24h_sliding_window.csv');
    $('#monthly-sliding-link').attr('href', config.apiHistoryIndexUrl+currencyCode+'/per_hour_monthly_sliding_window.csv');
    $('#daily-averages-link').attr('href', config.apiHistoryIndexUrl+currencyCode+'/per_day_all_time_history.csv');
    $('#volumes-link').attr('href', config.apiHistoryIndexUrl+currencyCode+'/volumes.csv');

    $('#set-global-average-currency').attr('title','click to set '+currencyCode+' as your global average default currency');
    $('#set-global-average-currency').attr('href','#'+currencyCode);
}

var renderSmallChart = function(currencyCode){
    $('#small-chart').html('');
    $('#charts-link a').show();
    $('#charts-link a').attr('href', 'charts.htm#'+currencyCode);

    if ($.inArray(currencyCode, config.currencyOrder) >= majorCurrencies) {
        $('#charts-link a').hide();
        return;
    }

     var  global_avg_url   = config.apiHistoryIndexUrl;
     var data_24h_URL = global_avg_url + currencyCode + '/24h_global_average_sliding_window.csv';

	$.get(data_24h_URL, function(csv){
        var data = [];
        $.each(csv.split('\n'), function(i, line){
            var values = line.split(',');
            if (i == 0 || line.length == 0){
                return;
            }

            var chartDailyValue = parseFloat(values.slice(-1)[0]) / config.scaleDivizer;
            data.push([parseDate(values[0]).getTime(), chartDailyValue] );
        });
        data.sort(function(a,b){
            if (a[0] > b[0]){
                return 1;
            } else if (a[0] < b[0]){
                return -1;
            } else {
                return -0;
            }
        });

		$('#small-chart').highcharts('StockChart', {
			chart : {
                animation : {
                    duration: 10000
                                },
                events: {
                    click: function(e){
                        window.location.href = 'charts.htm#'+currencyCode;
                    }
                },
                spacingBottom: 0,
                spacingLeft: 0,
                spacingRight: 0,
                spacingTop: 0
			},
			rangeSelector: {enabled: false},
			title: {text: '24h price '+currencyCode+' movement'},
			scrollbar: {enabled: false},
			navigator: {enabled: false},
			exporting: {enabled: false},
			tooltip: {enabled : false},
			credits: {enabled : false},

			series : [{
				data : data,
                cursor:'pointer',
                events:{
                    click: function(event){
                        window.location.href = 'charts.htm#'+currencyCode;
                    }
                }
			}]

		});
    });
}

$(function(){
    $('#show-more-currencies-in-global-avg-table').click(function(e){
        e.preventDefault();
        if ($('.secondary-global-avg-row').is(':hidden')){
            $('.secondary-global-avg-row').removeClass('hidden');
            $.cookie("global-average-table", 'collapsed');
            $('#show-more-currencies-in-global-avg-table').text('less');
        } else {
            $('.secondary-global-avg-row').addClass('hidden');
            $.cookie("global-average-table", 'hidden');
            $('#show-more-currencies-in-global-avg-table').text('more');

        }
        return false;
    });

})

