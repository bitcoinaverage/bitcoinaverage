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

var selectedFiatCurrency = false;
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
};

var renderCurrencyTabs = function(){
    var majorCurrencies = config.currencyOrder.slice(0, config.majorCurrencies);

    var currencyIndex = 0;
    var primaryCurrencyTabs = '';

    var currentHash = window.location.hash;
        currentHash = currentHash.replace('#', '');
        currentHash = currentHash.split('-');

    for (var majorCurrency in majorCurrencies) {
        var currentCurrency = majorCurrencies[majorCurrency];
        var data = API_data[currentCurrency];

        var last = (data['averages']['last']).toFixed(config.precision);
        var ask  = (data['averages']['ask']).toFixed(config.precision);
        var bid  = (data['averages']['bid']).toFixed(config.precision);


        var currencyCode = majorCurrencies[majorCurrency];
        var li = $('<li></li>');
        if(currencyCode  == currentHash[0]) {
            li.attr('class','active');
        }

        li.attr('data-currencycode', currencyCode);
        li.attr('id','slot'+currencyIndex+'-box');
        li.attr('title', fiatCurrencies[currencyCode]['name']);

        var h2 = $('<h2></h2>');
        h2.attr('itemsscope', '');
        h2.attr('itemtype', 'http://schema.org/PriceSpecification');

        // last price
        var slotLast = $('<span></span>');
        slotLast.attr('id', 'slot'+currencyIndex+'-last');
        slotLast.text(last);
        slotLast.attr('class', 'last-price');
        slotLast.attr('itemprop','price');

        //currency code
        var slotCurCode = $('<span></span>');
        slotCurCode.attr('id', 'slot'+currencyIndex+'-curcode');
        slotCurCode.attr('class', 'curcode');
        slotCurCode.text(currentCurrency);
        slotCurCode.attr('itemprop','priceCurrency');

        h2.append(slotLast);
        h2.append(slotCurCode);

        var bidAsk = $('<p class="bid_ask"></p>');

        var slotBid = $('<span></span>');
        slotBid.attr('id', 'slot'+currencyIndex+'-bid');
        slotBid.text(bid);
        slotBid.attr('title', 'bid');



        var slotAsk = $('<span></span>');
        slotAsk.attr('id', 'slot'+currencyIndex+'-ask');
        slotAsk.text(ask);
        slotAsk.attr('title', 'ask');

        bidAsk.append(slotBid);
        bidAsk.append('<span>&nbsp;/&nbsp;</span>');
        bidAsk.append(slotAsk);

        li.append(h2);
        li.append(bidAsk);

        primaryCurrencyTabs += li.outerHTML();
        currencyIndex++;
    }

    $('#currency-navtabs').html(primaryCurrencyTabs);
};

var renderAll = function(result, status, responseObj){
    result = adjustScale(result, config.scaleDivizer);

    //responseObj is not available in IE
    if(typeof responseObj == 'object'){
        timeGap = getTimeGap(responseObj.getAllResponseHeaders());
    }

    API_data = result;

    renderCurrencyTabs();
    renderSecondsSinceUpdate();

    if (!firstRenderDone) {
        var currencyCode = window.location.hash;
        currencyCode = currencyCode.slice(1);
        currencyCode = currencyCode.split('-')[0];

        // if currency hash isn't defined
        if(typeof fiatCurrencies[currencyCode] == 'undefined'){
            currencyCode = config.currencyOrder[0];
        }

        $('.currency-navigation').children("[data-currencycode='" + currencyCode + "']").click();
        selectedFiatCurrency = currencyCode;

        var baseCookie = $.cookie('base');
        if(baseCookie == 'bitcoin'){
            $('#nomillibit-button').click();
        } else if(baseCookie == null){
            $.cookie('base', 'millibitcoin');
        }

        $('body').show();

        $('#currency-input').focus();
        firstRenderDone = true;
    }

    renderLegend(selectedFiatCurrency);
};

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
    }


    if (dataChanged) {
        var flashingFigures = $('#slot'+slotNum+'-last, #slot'+slotNum+'-ask, #slot'+slotNum+'-bid');
        flashingFigures.css({ 'opacity' : 0.5});
        flashingFigures.animate({ 'opacity' : 1 }, 500);
    }
};

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

    if (selectedFiatCurrency == currencyCode){
        document.title = API_data[currencyCode].global_averages.last.toFixed(config.precision)+' '+currencyCode+' | BitcoinAverage - independent bitcoin price';
    }

    $('.legend-curcode').text(currencyCode);

    $('.bitcoin-calc .currency-label').text(currencyCode);
    $('.bitcoin-calc .currency-label').append($('<i class="glyphicon glyphicon-chevron-down"></i>'));

    var last = currencyData.averages.last.toFixed(config.precision);
    $('#legend-last').html(last);

    var bitCoinInputVal  = $('#bitcoin-input').toNumber().val();
    var fiatCalcVaule = (last * bitCoinInputVal).toFixed(2);
    $('#currency-input').val(fiatCalcVaule);

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

    // full currency name update on description block and in the info block
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
    for(var slotNum in exchangeArray){
        if (exchangeArray[slotNum]['source'] == 'cache') {
            exchangeArray[slotNum]['name'] = exchangeArray[slotNum]['name'] + '**';
            $('#legend-api-down-note').show();
        } else if (exchangeArray[slotNum]['source'] == 'bitcoincharts') {
            exchangeArray[slotNum]['name'] = exchangeArray[slotNum]['name'] + '*';
            $('#legend-api-unavailable-note').show();
        }

        var volumePercent = exchangeArray[slotNum]['volume_percent'].toFixed(2);
        var pad = "00000";
        volumePercent = pad.substring(0, pad.length - volumePercent.length) + volumePercent;

        $('#legend-slot'+slotNum+'-name').text(exchangeArray[slotNum]['name']);
        $('#legend-slot'+slotNum+'-volume_btc').text(exchangeArray[slotNum]['volume_btc'])
                                               .formatCurrency({symbol: '',
                                                                positiveFormat: '%n',
                                                                negativeFormat: '-%s%n',
                                                                roundToDecimalPlace: 2
                                                                });

        $('#legend-slot'+slotNum+'-volume_percent').text(volumePercent);
        $('#legend-slot'+slotNum+'-rate').text(exchangeArray[slotNum]['rates']['last'].toFixed(config.precision));
        $('#legend-slot'+slotNum).toggle(true);
    }

    $('#24h-sliding-link').attr('href', config.apiHistoryIndexUrl+currencyCode+'/per_minute_24h_sliding_window.csv');
    $('#monthly-sliding-link').attr('href', config.apiHistoryIndexUrl+currencyCode+'/per_hour_monthly_sliding_window.csv');
    $('#daily-averages-link').attr('href', config.apiHistoryIndexUrl+currencyCode+'/per_day_all_time_history.csv');
    $('#volumes-link').attr('href', config.apiHistoryIndexUrl+currencyCode+'/volumes.csv');

    $('#set-global-average-currency').attr('title','click to set '+currencyCode+' as your global average default currency');
    $('#set-global-average-currency').attr('href','#'+currencyCode);
};

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
            var dailyChartValue =  parseFloat(values[1]) /config.scaleDivizer
            data.push([ parseDate(values[0]).getTime(), dailyChartValue ]);
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
};


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

    $('#show-ignored').click(function(e){
        e.preventDefault();


        $('#legend-ignored-table').show();
        $(this).hide();

        return false;
    });

    callAPI();

    setInterval(callAPI, config.refreshRate);
    setInterval(renderSecondsSinceUpdate, 5000);

    renderMajorCurrencies();
    renderSecondaryCurrencies();


    $('#legend-block').click(function(event){
        event.stopPropagation();
    });

    $(document).on('click', '.currency-navigation li', currencyNavigation );

    $('#nomillibit-button').click(changeBaseButtonClick);

    $('#currency-input').blur(function() {
        calc_renderFiat($(this).toNumber().val());
    });
    $('#currency-input').focus(function() {
        $('#currency-input').val($(this).toNumber().val());
    });
    $('#currency-input').keyup(calc_fiatInputKeyup);

    $('#bitcoin-input').blur(function() {
        calc_renderBitcoin($(this).toNumber().val(), $.cookie('base'));
    });
    $('#bitcoin-input').focus(function() {
        $('#bitcoin-input').val($(this).toNumber().val());
    });
    $('#bitcoin-input').keyup(calc_bitcoinInputKeyup);


    // currency navigation (primary currency, secondary currency, currency tabs on markets page
    $(document).on('click', '.currency-navigation li', currencyNavigation );

    // hide or show calc currency list by calc currency label click
    $('#bitcoin-calc-currency-label').click(function(e){
        e.stopPropagation();
        if ($('.calculator-currency-switch').is(':visible')){
            $('.calculator-currency-switch').slideUp();
        } else {
            $('.calculator-currency-switch').slideDown();
        }
    });

});
