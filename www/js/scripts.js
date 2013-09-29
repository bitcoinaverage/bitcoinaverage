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

if (config.apiIndexUrlNoGox[config.apiIndexUrlNoGox.length-1] != '/') {
    config.apiIndexUrlNoGox = config.apiIndexUrlNoGox + '/';
}
var API_all_url_nogox = config.apiIndexUrlNoGox+'all';

if (config.apiHistoryIndexUrl[config.apiHistoryIndexUrl.length-1] != '/') {
    config.apiHistoryIndexUrl = config.apiHistoryIndexUrl + '/';
}

var active_API_URL = API_all_url;

var legendClickStatus = false;
var firstRenderDone = false;
var fiatExchangeRates = [];
var timeGap = 0; //actual time is fetched from remote resource, and user's local time is adjusted by X seconds to be completely exact

$(function(){
    callAPI();
    setInterval(callAPI, config.refreshRate);
    setInterval(renderSecondsSinceUpdate, 5000);

    $('#legend-block').click(function(event){
        event.stopPropagation();
    });

    $('#nogox-button').click(function(event){
        var button = $(this);
        if (active_API_URL == API_all_url){
            active_API_URL = API_all_url_nogox;
            $(this).removeClass('btn-default');
            $(this).addClass('btn-primary');
            button.html('MTGox ignored for USD/EUR/GBP');

            var currentHash = window.location.hash;
            var currentLocation = document.location.href;
            var newLocation = currentLocation.replace(currentHash, '')+'#USD|nogox';
            window.location.replace(newLocation);
        } else {
            active_API_URL = API_all_url;
            $(this).addClass('btn-default');
            $(this).removeClass('btn-primary');
            button.html('ignore MTGox for USD/EUR/GBP');

            var currentHash = window.location.hash;
            var currentLocation = document.location.href;
            var newLocation = currentLocation.replace(currentHash, '')+'#USD';
            window.location.replace(newLocation);
        }
        callAPI(function(result){
            renderAll(result);
            renderLegend('USD');
        });
        renderSmallChart('USD');
    });

    for(var slotNum in config.currencyOrder){
        $('#slot'+slotNum+'-last, #slot'+slotNum+'-ask, #slot'+slotNum+'-bid').dblclick(function(event){
            event.preventDefault();
            $(this).selectText();
        });

        var slotLegendBox = $('#slot'+slotNum+'-box');
        slotLegendBox.mouseover(function(event){
            var curCode = $(this).data('currencycode');
            renderLegend(curCode);
            $('#currency-navtabs').children('li').removeClass('active');
            $(this).addClass('active');
        });
        slotLegendBox.mouseout(function(event){
            $('#currency-navtabs').children('li').removeClass('active');
            if (legendClickStatus != false) {
                renderLegend(legendClickStatus);
                $('#currency-navtabs').children('li[data-currencycode="'+legendClickStatus+'"]').addClass('active');
            }
        });
        slotLegendBox.click(function(event){
            event.preventDefault();
            event.stopPropagation();
            var curCode = $(this).data('currencycode');
            if (legendClickStatus == false || legendClickStatus != curCode) {
                renderLegend(curCode);
                renderSmallChart(curCode);
                legendClickStatus = curCode;

                $('#currency-navtabs').children('li').removeClass('active');
                $('#currency-navtabs').children('li[data-currencycode="'+legendClickStatus+'"]').addClass('active');
                $('#currency-sidebar li').removeClass('active');
                $('#currency-sidebar li[data-currencycode="'+legendClickStatus+'"]').addClass('active');

                var currentHash = window.location.hash;
                var currentLocation = document.location.href;
                var newLocation = currentLocation.replace(currentHash, '')+'#'+curCode;
                if (active_API_URL == API_all_url_nogox){
                    newLocation = newLocation + '|nogox';
                }
                window.location.replace(newLocation);
            }
        });

        var slotLegendLink = $('#slot'+slotNum+'-link');
        slotLegendLink.mouseover(function(event){
            var curCode = $(this).data('currencycode');
            renderLegend(curCode);
            $('#currency-sidebar li').removeClass('active');
            $(this).addClass('active');
        });
        slotLegendLink.mouseout(function(event){
            $('#currency-sidebar li').removeClass('active');
            if (legendClickStatus != false) {
                renderLegend(legendClickStatus);
                $('#currency-sidebar li[data-currencycode="'+legendClickStatus+'"]').addClass('active');
            }
        });
        slotLegendLink.click(function(event){
            event.preventDefault();
            event.stopPropagation();
            var curCode = $(this).data('currencycode');
            if (legendClickStatus == false || legendClickStatus != curCode) {
                legendClickStatus = curCode;
                renderLegend(curCode);
                renderSmallChart(curCode);

                $('#currency-navtabs').children('li').removeClass('active');
                $('#currency-navtabs').children('li[data-currencycode="'+legendClickStatus+'"]').addClass('active');
                $('#currency-sidebar li').removeClass('active');
                $('#currency-sidebar li[data-currencycode="'+legendClickStatus+'"]').addClass('active');

                var currentHash = window.location.hash;
                var currentLocation = document.location.href;
                var newLocation = currentLocation.replace(currentHash, '')+'#'+curCode;
                if (active_API_URL == API_all_url_nogox){
                    newLocation = newLocation + '|nogox';
                }
                window.location.replace(newLocation);
            }
        });

    }

    $("#question-mark").tooltip({
        'trigger':'click',
        'html': $(this).data('original-title'),
        'placement': 'left'
    });

});

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

    getTimeGap(responseObj.getAllResponseHeaders());
    API_data = result;

    $('#currency-sidebar li[id^="slot"] a').hide();

    for(var slotNum in config.currencyOrder){
        var currencyCode = config.currencyOrder[slotNum];
        renderRates(currencyCode, result[currencyCode], slotNum);
    }

    renderSecondsSinceUpdate();
    if (!firstRenderDone) {
        $('body').show();
        var currentHash = window.location.hash;
        currentHash = currentHash.replace('#', '');
        currentHash = currentHash.split('|');
        if (currentHash.length == 2 && currentHash[1] == 'nogox'){
            $('#nogox-button').click();
        }
        currentHash = currentHash[0];


        if (currentHash != '' && $('#currency-sidebar li[data-currencycode="'+currentHash+'"]').size() > 0) {
            $('#currency-sidebar li[data-currencycode="'+currentHash+'"]').click();
        } else {
            $('#slot0-box').click();
        }

        firstRenderDone = true;
    }

    if (legendClickStatus != false){
        renderLegend(legendClickStatus);
        document.title = API_data[legendClickStatus].averages.last+' '+legendClickStatus+' | BitcoinAverage - independent bitcoin price';
    } else {
        renderLegend('USD');
        document.title = API_data['USD'].averages.last+' USD | BitcoinAverage - independent bitcoin price';
    }
}

var lastusdvalue = 0;
var renderRates = function(currencyCode, currencyData, slotNum){
    $('#slot'+slotNum+'-link').attr('data-currencycode', currencyCode);

    var slotLegendLink_a = $('#slot'+slotNum+'-link a');
    slotLegendLink_a.text(currencyCode);
    slotLegendLink_a.attr('href', '#'+currencyCode);
    slotLegendLink_a.show();

    majorCurrencies
    $('#slot'+slotNum+'-box').attr('data-currencycode', currencyCode);
    $('#slot'+slotNum+'-curcode').text(currencyCode);

    var dataChanged = false;
    dataChanged = (dataChanged || $('#slot'+slotNum+'-last').text() != currencyData.averages.last);
    dataChanged = (dataChanged || $('#slot'+slotNum+'-ask').text() != currencyData.averages.ask);
    dataChanged = (dataChanged || $('#slot'+slotNum+'-bid').text() != currencyData.averages.bid);
    $('#slot'+slotNum+'-last').text(currencyData.averages.last.toFixed(2));
    $('#slot'+slotNum+'-ask').text(currencyData.averages.ask.toFixed(2));
    $('#slot'+slotNum+'-bid').text(currencyData.averages.bid.toFixed(2));

    if (currencyCode == "USD") {
        if (lastusdvalue == 0) {
            lastusdvalue = currencyData.averages.last;
        } else {
            if (currencyData.averages.last > lastusdvalue) {
                $('#usd-arrowup').show();
                $('#usd-arrowdown').hide();
            } else if (currencyData.averages.last < lastusdvalue) {
                $('#usd-arrowup').hide();
                $('#usd-arrowdown').show();
            }
            lastusdvalue = currencyData.averages.last;
        }
    }

    if (dataChanged) {
        var flashingFigures = $('#slot'+slotNum+'-last, #slot'+slotNum+'-ask, #slot'+slotNum+'-bid');
        flashingFigures.css({ 'opacity' : 0.5});
        flashingFigures.animate({ 'opacity' : 1 }, 500);
    }
}

var renderLegend = function(currencyCode){
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
        document.title = API_data[currencyCode].averages.last+' '+currencyCode+' | BitcoinAverage - independent bitcoin price';
    }

    $('.legend-curcode').text(currencyCode);
    $('#legend-last').html(currencyData.averages.last.toFixed(2));
    $('#legend-bid').html(currencyData.averages.bid.toFixed(2));
    $('#legend-ask').html(currencyData.averages.ask.toFixed(2));
    $('#legend-total-volume').html(currencyData.averages.total_vol.toFixed(2));
    if (typeof currencyData.averages['24h_avg'] != 'undefined') {
        $('#legend-24h-avg').html(currencyData.averages['24h_avg'].toFixed(2));
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
            $('#legend-ignored-slot'+index+'-reason').text(API_data.ignored_exchanges[exchange_name]);
            $('#legend-ignored-slot'+index+'-box').show();
            index++;
        }
    }

    if (currencyCode != 'USD') {
        var USD_BTC_fiat_rate = parseFloat(API_data['USD'].averages.last) * parseFloat(fiatCurrencies[currencyCode]);
        USD_BTC_fiat_rate = Math.round(USD_BTC_fiat_rate*100)/100;
        USD_BTC_fiat_rate = USD_BTC_fiat_rate + ' ' + currencyCode;
        $('#legend-converted-to-USD').html(USD_BTC_fiat_rate);
    } else {
        $('#legend-converted-to-USD').html('N/A');
    }

    for(var slotNum=0;slotNum<legendSlots;slotNum++){
        $('#legend-slot'+slotNum).toggle(false);
    }
    $('#legend-other').toggle(false);

    var otherCount = 0;
    var otherPercent = 0;
    var otherVolume = 0;

    $('#legend-api-unavailable-note').hide();
    $('#legend-api-down-note').hide();
    for(var slotNum in exchangeArray){
        if (exchangeArray[slotNum]['source'] == 'cache') {
            exchangeArray[slotNum]['name'] = exchangeArray[slotNum]['name'] + '**';
            $('#legend-api-down-note').show();
        } else if (exchangeArray[slotNum]['source'] == 'bitcoincharts') {
            exchangeArray[slotNum]['name'] = exchangeArray[slotNum]['name'] + '*';
            $('#legend-api-unavailable-note').show();
        }

        $('#legend-slot'+slotNum+'-name').text(exchangeArray[slotNum]['name']);
        $('#legend-slot'+slotNum+'-volume_btc').text(exchangeArray[slotNum]['volume_btc'].toFixed(2));
        $('#legend-slot'+slotNum+'-volume_percent').text(exchangeArray[slotNum]['volume_percent'].toFixed(2));
        $('#legend-slot'+slotNum+'-rate').text(exchangeArray[slotNum]['rates']['last'].toFixed(2));
        $('#legend-slot'+slotNum).toggle(true);
    }

    $('#24h-sliding-link').attr('href', config.apiHistoryIndexUrl+currencyCode+'/per_minute_24h_sliding_window.csv');
    $('#monthly-sliding-link').attr('href', config.apiHistoryIndexUrl+currencyCode+'/per_hour_monthly_sliding_window.csv');
    $('#daily-averages-link').attr('href', config.apiHistoryIndexUrl+currencyCode+'/per_day_all_time_history.csv');
    $('#volumes-link').attr('href', config.apiHistoryIndexUrl+currencyCode+'/volumes.csv');
}

var renderSmallChart = function(currencyCode){
    $('#small-chart').html('');
    $('#charts-link a').show();
    $('#charts-link a').attr('href', 'charts.htm#'+currencyCode);

    if ($.inArray(currencyCode, config.currencyOrder) >= majorCurrencies || active_API_URL == API_all_url_nogox) {
        $('#charts-link a').hide();
        return;
    }


    var data_24h_URL = config.apiHistoryIndexUrl + currencyCode + '/per_minute_24h_sliding_window.csv';
	$.get(data_24h_URL, function(csv){
        var data = [];
        $.each(csv.split('\n'), function(i, line){
            var values = line.split(',');
            if (i == 0 || line.length == 0 || values.length != 2){
                return;
            }
            data.push([parseDate(values[0]).getTime(),
                       parseFloat(values[1])
                        ]);
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

var renderSecondsSinceUpdate = function(){
    var seconds = Math.round(new Date().getTime()/1000) - Math.round(Date.parse(API_data['timestamp'])/1000) - timeGap;
    if (seconds < 120) {
        var timeString = seconds+' sec';
    } else if (seconds < 120*60) {
        var timeString = Math.round(seconds/60)+' min';
    } else {
        var timeString = Math.round(seconds/60/60)+' hours';
    }
    $('#legend-update-time-ago').html(timeString);
}

var getTimeGap = function(headers){
    headers = headers.trim("\n");
    var headersList = headers.split("\n");
    for(var i=0;i<headersList.length;i++){
        var headerDetails = headersList[i].split(':');
        if(headerDetails[0] == 'Date'){
            headerDetails = headerDetails.splice(1,headerDetails.length);
            var currentRemoteTimestamp = Math.round(Date.parse(headerDetails.join(':'))/1000);
            var currentLocalTimestamp = Math.round(new Date().getTime()/1000);
            timeGap = currentLocalTimestamp - currentRemoteTimestamp;
        }
    }
}

var parseDate = function(dateString){
    var parts = dateString.split(' ');
    var dateParts = parts[0].split('-');
    var timeParts = parts[1].split(':');
    var result = new Date(dateParts[0], dateParts[1]-1, dateParts[2], timeParts[0], timeParts[1], timeParts[2]);
    return result;
}

jQuery.fn.selectText=function(){var doc=document,element=this[0],range,selection; if(doc.body.createTextRange){range=document.body.createTextRange();range.moveToElementText(element);range.select();}else if(window.getSelection){selection=window.getSelection();range=document.createRange();range.selectNodeContents(element);selection.removeAllRanges();selection.addRange(range);}};
jQuery.fn.countObj=function(){var count=0;var obj=this[0];for(i in obj){if(obj.hasOwnProperty(i)){count++;}}return count;};