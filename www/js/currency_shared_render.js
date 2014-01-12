// Render Major currencies menu
var renderMajorCurrencies = function(){
    var majorCurrencies = config.currencyOrder.slice(0, config.majorCurrencies);
    var currencyIndex = 0;
    var primaryCurrencyList = '';
    for (var majorCurrencyIndex in majorCurrencies) {
        var currencyCode = majorCurrencies[majorCurrencyIndex];
        var li = $('<li></li>');
        var link = $('<a></a>');
        link.attr('href', '#'+currencyCode);
        li.attr('id', 'slot'+ currencyIndex +'-link');
        li.attr('data-currencycode', currencyCode);
        link.text(currencyCode);
        li.append(link);
        currencyIndex++;
        primaryCurrencyList += li.outerHTML();
    }
    $('.primary-currency-switch').html(primaryCurrencyList);
    $('.primary-currency-switch-calc').html(primaryCurrencyList);
};

var renderWorldCurrencies = function() {
    var generalCurrencies = config.currencyOrder;

    var generalCurrenciesLength = generalCurrencies.length;
    var currencyIndex = generalCurrenciesLength;
    var allCurrenciesList = '';
    $.getJSON(config.apiIndexUrl+'ticker/global/all', function(data){
        var items = [];
        $.each(data, function(key, val){
            if ( $.inArray(key, generalCurrencies) == -1 && key != 'timestamp'){
                var currencyInner = $('<li></li>');

                currencyInner.attr('id', 'slot' + currencyIndex + '-link');
                currencyInner.attr('data-currencycode', key );
                if (selectedFiatCurrency == key){
                    currencyInner.attr('class', 'active');
                }

                var currencyLink = $('<a></a>')
                currencyLink.attr('href', '#'+key);
                currencyLink.text(key);

                currencyInner.append(currencyLink);
                allCurrenciesList += currencyInner.outerHTML();
                currencyIndex++;

            }
        });
        $('.all-currencies').html(allCurrenciesList);
    });
};

// Render secondary currencies menu
var renderSecondaryCurrencies = function (){
    var secondaryCurrencies = config.currencyOrder.slice(config.majorCurrencies+1);
    var currencyIndex = config.majorCurrencies + 1;
    var secondaryCurrenciesList = '';
    for (var secondaryCurrencyIndex in secondaryCurrencies) {
        var currencyCode = secondaryCurrencies[secondaryCurrencyIndex];
        var li = $('<li></li>');
        var link = $('<a></a>');
        link.attr('href', '#'+currencyCode);
        li.attr('id', 'slot'+ currencyIndex +'-link');
        li.attr('data-currencycode', currencyCode);
        link.text(currencyCode);
        li.append(link);
        currencyIndex++;
        secondaryCurrenciesList += li.outerHTML();


    }
    $('.secondary-currency-switch').html(secondaryCurrenciesList);
    $('.secondary-currency-switch-calc').html(secondaryCurrenciesList);

};

var isCurrencyBelongsToPrimaryList = function(currencyCode) {
    if($.inArray(currencyCode, config.currencyOrder) != -1){
        return true;
    }

    return false;
};
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
};

var currencyNavigation = function(event){
    event.preventDefault();
    event.stopPropagation();

    var curCode = $(this).data('currencycode');
    if (selectedFiatCurrency == false || selectedFiatCurrency != curCode) {
        selectedFiatCurrency = curCode;

        var isPrimaryCurrency = isCurrencyBelongsToPrimaryList(selectedFiatCurrency);
        if ( isPrimaryCurrency ){
            $('.highcharts-container').show();
            renderLegend(curCode);
            renderSmallChart(curCode);
            $('.calculator-currency-switch').slideUp();
            $('#global-last').html(API_data[curCode].global_averages.last.toFixed(config.precision));
        }
        else {
            renderLegendForExtendedCurrencyList(curCode);
        }

        // add active class to selected currency
        $('.all-currency-navigation li').removeClass('active');
        $('.currency-navigation li').removeClass('active');

        $('.currency-navigation').find("[data-currencycode='" + curCode + "']").addClass('active');


        var currentHash = window.location.hash;
        var currentLocation = document.location.href;
        var newLocation = currentLocation.replace(currentHash, '')+'#'+curCode;
        if (config.scaleDivizer == 1){
            newLocation = newLocation + '-nomillibit';
        }
        window.location.replace(newLocation);
    }
};


var changeBaseButtonClick = function(event){
    var button = $(this);

    if (config.scaleDivizer == 1000){
        $.cookie('base', 'bitcoin');
        config.scaleDivizer = 1;
        config.precision = 1;

        button.removeClass('btn-default');
        button.addClass('btn-primary');
        button.html('฿1 base used');

        var currentHash = window.location.hash;
        var currentLocation = document.location.href;
        var newLocation = currentLocation.replace(currentHash, '') + '#' + selectedFiatCurrency + '-nomillibit';
        window.location.replace(newLocation);

        $('.bitcoin-label').text('฿');
        $('.market-page-description .base').text('bitcoin');
    } else {
        $.cookie('base', 'millibitcoin');
        config.scaleDivizer = 1000;
        config.precision = 3;

        button.addClass('btn-default');
        button.removeClass('btn-primary');
        button.html('switch to ฿1 base');

        var currentHash = window.location.hash;
        var currentLocation = document.location.href;
        var newLocation = currentLocation.replace(currentHash, '') + '#' + selectedFiatCurrency;
        window.location.replace(newLocation);

        $('.bitcoin-label').text('m฿');
        $('.market-page-description .base').text('millibitcoin');
    }

    calc_renderBitcoin(1, $.cookie('base'));

    callAPI(function(result){

        renderAll(result);

        var isPrimaryCurrency = isCurrencyBelongsToPrimaryList(selectedFiatCurrency);
        if(isPrimaryCurrency){
            renderLegend(selectedFiatCurrency);
            renderSmallChart(selectedFiatCurrency);
        } else {
            renderLegendForExtendedCurrencyList(selectedFiatCurrency);
        }
    });

};


var calc_fiatInputKeyup = function(e){
    var e = window.event || e;
    var keyUnicode = e.charCode || e.keyCode;
    if (e !== undefined) {
        switch (keyUnicode) {
            case 16: break; // Shift
            case 17: break; // Ctrl
            case 18: break; // Alt
            case 27: this.value = ''; break; // Esc: clear entry
            case 35: break; // End
            case 36: break; // Home
            case 37: break; // cursor left
            case 38: break; // cursor up
            case 39: break; // cursor right
            case 40: break; // cursor down
            case 78: break; // N (Opera 9.63+ maps the "." from the number key section to the "N" key too!) (See: http://unixpapa.com/js/key.html search for ". Del")
            case 110: break; // . number block (Opera 9.63+ maps the "." from the number block to the "N" key (78) !!!)
            case 190: break; // .
        }
        var currencyVal = $(this).toNumber().val();
        var globalLastPrice = $('#legend-last').text();
        calc_renderBitcoin(currencyVal / globalLastPrice, $.cookie('base'));
    }
};

var calc_bitcoinInputKeyup = function(e){
    var e = window.event || e;
    var keyUnicode = e.charCode || e.keyCode;
    if (e !== undefined) {
        switch (keyUnicode) {
            case 16: break; // Shift
            case 17: break; // Ctrl
            case 18: break; // Alt
            case 27: this.value = ''; break; // Esc: clear entry
            case 35: break; // End
            case 36: break; // Home
            case 37: break; // cursor left
            case 38: break; // cursor up
            case 39: break; // cursor right
            case 40: break; // cursor down
            case 78: break; // N (Opera 9.63+ maps the "." from the number key section to the "N" key too!) (See: http://unixpapa.com/js/key.html search for ". Del")
            case 110: break; // . number block (Opera 9.63+ maps the "." from the number block to the "N" key (78) !!!)
            case 190: break; // .
            default: $(this).formatCurrency({ symbol: '', colorize: true, negativeFormat: '-%s%n', roundToDecimalPlace: -1, eventOnDecimalsEntered: true });
        }
        var bitCoins = $(this).toNumber().val();
        var globalLastPrice = $('#legend-last').text();

        calc_renderFiat(globalLastPrice * bitCoins);
    }
};

var renderLegendForExtendedCurrencyList = function(currencyCode){

    $('.highcharts-container').hide();
    $.getJSON(config.apiIndexUrl+'ticker/global/all', function(data){

        var currencyCodeData =  adjustScale (data[currencyCode], config.scaleDivizer);

        $('.legend-curcode').text(currencyCode);
        $('.bitcoin-calc .currency-label').text(currencyCode + '↴');

        var last = currencyCodeData.last.toFixed(config.precision);
        var bid = currencyCodeData.bid.toFixed(config.precision);
        var ask = currencyCodeData.ask.toFixed(config.precision);

        $('#legend-last').html(last);

        var bitCoinInputValue = $('#bitcoin-input').toNumber().val();

        calc_renderBitcoin(bitCoinInputValue, $.cookie('base'));
        calc_renderFiat(last * bitCoinInputValue);

        $('#legend-bid').html(bid);
        $('#legend-bid').html(ask);
        $('#global-last').html(last);

        $('#legend-bid, #legend-ask, #legend-last').formatCurrency({symbol: '',
            positiveFormat: '%n',
            negativeFormat: '-%s%n',
            roundToDecimalPlace: 2 //always 2 dec places for fiat
        });



        $('#legend-curcode').text(currencyCode);
        $('.curcode-main').text(currencyCode);

    });

    $('.legend-currency-code-update').text(fiatCurrencies[currencyCode]['name']);

    $('#legend-global-volume-percent').text(0);
    $('#legend-24h-avg').text(0);
    $('#legend-currency-trading-volume').text(0);
};

var calc_renderFiat = function(fiat_value){
    $('#currency-input').val(fiat_value).formatCurrency({symbol: '',
                                                          colorize: true,
                                                            positiveFormat: '%n',
                                                            negativeFormat: '-%s%n',
                                                            roundToDecimalPlace: 2 //always 2 dec places for fiat
                                                            });
};

var calc_renderBitcoin = function(btc_value, base){
    if (base == 'bitcoin'){
        var precision = 5;
    } else {
        var precision = 2;
    }
    $('#bitcoin-input').val(btc_value)
                       .formatCurrency({symbol: '',
                                        colorize: true,
                                        positiveFormat: '%n',
                                        negativeFormat: '-%s%n',
                                        roundToDecimalPlace: precision
                                          });
};
