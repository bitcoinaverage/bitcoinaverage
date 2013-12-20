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
        var currentHash = window.location.hash;
        currentHash = currentHash.replace('#', '');
        currentHash = currentHash.split('|');
        if (currentHash.length == 2 && currentHash[1] == 'nomillibit'){
            $('#nomillibit-button').click();
        }
        currentHash = currentHash[0];

        var global_average_default = $.cookie('global-average');
        if (currentHash != '' && $('#currency-sidebar li[data-currencycode="'+currentHash+'"]').size() > 0) {
            $('#currency-sidebar li[data-currencycode="'+currentHash+'"]').click();
        } else if (typeof global_average_default != 'undefined') {
            $('#currency-sidebar li[data-currencycode="'+global_average_default+'"]').click();
        } else {
            $('#slot0-link').click();
        }

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
        document.title = API_data[currencyCode].global_averages.last.toFixed(config.precision)+' '+currencyCode+' | BitcoinAverage - independent bitcoin price';
    }

    $('.legend-curcode').text(currencyCode);
    $('#legend-last').html(currencyData.averages.last.toFixed(config.precision));
    $('#legend-bid').html(currencyData.averages.bid.toFixed(config.precision));
    $('#legend-ask').html(currencyData.averages.ask.toFixed(config.precision));
    $('#legend-total-volume').html(currencyData.averages.total_vol.toFixed(config.precision));
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

    $('#legend-currency-name').html(fiatCurrencies[currencyCode]['name']);

    $('#legend-global-average').html(currencyData.global_averages.last.toFixed(config.precision))
    $('#legend-global-volume-percent').html(currencyData.global_averages.volume_percent.toFixed(config.precision))


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
        $('#legend-slot'+slotNum+'-volume_btc').text(exchangeArray[slotNum]['volume_btc'].toFixed(config.precision));
        $('#legend-slot'+slotNum+'-volume_percent').text(exchangeArray[slotNum]['volume_percent'].toFixed(config.precision));
        $('#legend-slot'+slotNum+'-rate').text(exchangeArray[slotNum]['rates']['last'].toFixed(config.precision));
        $('#legend-slot'+slotNum).toggle(true);
    }

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
