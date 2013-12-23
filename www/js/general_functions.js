
// Convert Jquery Object to html
$.fn.outerHTML = function(){
    // IE, Chrome & Safari will comply with the non-standard outerHTML, all others (FF) will have a fall-back for cloning
    return (!this.length) ? this : (this[0].outerHTML || (
        function(el){
            var div = document.createElement('div');
            div.appendChild(el.cloneNode(true));
            var contents = div.innerHTML;
            div = null;
            return contents;
        })(this[0]));

}


// Render Major currencies menu
var renderMajorCurrencies = function(){
    var majorCurrencies = config.currencyOrder.slice(0, config.majorCurrencies);

    var currencyIndex = 0;
    var primaryCurrencyList = '';
    for (var majorCurrency in majorCurrencies) {
        var currencyCode = majorCurrencies[majorCurrency];
        var li = $('<li></li>');
        var link = $('<a></a>');
        link.attr('href', '#'+currencyCode);
        li.attr('id', 'slot'+ currencyIndex +'-link');
        li.attr('data-currencycode', majorCurrency);
        link.text(currencyCode);
        li.append(link);
        currencyIndex++;
        primaryCurrencyList += li.outerHTML();
    }
    $('.primary-currency-switch').html(primaryCurrencyList);
}

// Render secondary currencies menu
var renderSecondaryCurrencies = function (){
    var secondaryCurrencies = config.currencyOrder.slice(config.majorCurrencies+1);

    var currencyIndex = config.majorCurrencies+1;
    var secondaryCurrenciesList = '';
    for (var secondaryCurrency in secondaryCurrencies) {

        var currencyCode = majorCurrencies[secondaryCurrency];
        var li = $('<li></li>');
        var link = $('<a></a>');
        link.attr('href', '#'+currencyCode);
        li.attr('id', 'slot'+ currencyIndex +'-link');
        li.attr('data-currencycode', secondaryCurrency);
        link.text(currencyCode);
        li.append(link);
        currencyIndex++;
        secondaryCurrenciesList += li.outerHTML();
        if( (currencyIndex-6) % 6 == 0) {
            secondaryCurrenciesList += '<br/>';
        }
    }
    $('.secondary-currency-switch').html(secondaryCurrenciesList);
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

var adjustScale = function(apiResult){
    if (config.scaleDivizer == 1) {
        return apiResult;
    }

    var adjustedApiResult = {};
    for (var i in apiResult){
        if (typeof apiResult[i] == 'array' || typeof apiResult[i] == 'object') {
            adjustedApiResult[i] = adjustScale(apiResult[i])
        } else if (i == '24h_avg'
            || i == 'ask'
            || i == 'bid'
            || i == 'last') {
            adjustedApiResult[i] = parseFloat(apiResult[i]) / config.scaleDivizer;
        } else {
            adjustedApiResult[i] = apiResult[i];
        }
    }

    return adjustedApiResult;
}

$(function(){
    callAPI();
    setInterval(callAPI, config.refreshRate);
    setInterval(renderSecondsSinceUpdate, 5000);

    renderMajorCurrencies();
    renderSecondaryCurrencies();

    $('#legend-block').click(function(event){
        event.stopPropagation();
    });

    $('#nomillibit-button').click(function(event){
        var button = $(this);

        if (config.scaleDivizer == 1000){

            config.scaleDivizer = 1;
            config.precision = 1;
            $(this).removeClass('btn-default');
            $(this).addClass('btn-primary');
            button.html('฿1 base used');
            var currentHash = window.location.hash;
            var currentLocation = document.location.href;
            var newLocation = currentLocation.replace(currentHash, '')+'#USD-nomillibit';
            window.location.replace(newLocation);
            $('.bitcoin-label').text('฿');
            $('.market-page-description .base').text('bitcoin');
        } else {
            config.scaleDivizer = 1000;
            config.precision = 3;
            $(this).addClass('btn-default');
            $(this).removeClass('btn-primary');
            button.html('switch to ฿1 base');

            var currentHash = window.location.hash;
            var currentLocation = document.location.href;

            var newLocation = currentLocation.replace(currentHash, '')+'#USD';
            window.location.replace(newLocation);
            $('.bitcoin-label').text('m฿');
            $('.market-page-description .base').text('millibitcoin');
        }
        callAPI(function(result){
            renderAll(result);
            renderLegend('USD');

        });
        //$('.primary-currency-switch li:first-child').click();
    });

    $('#set-global-average-currency').click(function(event){
        $.cookie('global-average', legendClickStatus);
        callAPI();
    });

    for(var slotNum in config.currencyOrder){
        $('#slot'+slotNum+'-last, ' +
            '#slot'+slotNum+'-ask, ' +
            '#slot'+slotNum+'-bid, '+
            '#global-last, '+
            '#global-bid, '+
            '#global-ask').dblclick(function(event){
                event.preventDefault();
                $(this).selectText();
            });
    }


// currency navigation (primary currency, secondary currency, currency tabs on markets page
$(document).on('click', '.currency-navigation li', function(event){
    event.preventDefault();
    event.stopPropagation();
    var curCode = $(this).data('currencycode');
    if (legendClickStatus == false || legendClickStatus != curCode) {
        legendClickStatus = curCode;
        renderLegend(curCode);
        renderSmallChart(curCode);


        // add active class to selected currency
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
});

// Format while typing & warn on decimals entered, 2 decimal places
$('#bitcoin-input').blur(function() {
    $('#bitcoin-input').html(null);
    $(this).formatCurrency({ symbol: '', colorize: true, positiveFormat: '%n', negativeFormat: '-%s%n', roundToDecimalPlace: 2 });
})
    .keyup(function(e) {
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

            var calculateCurrency = (globalLastPrice * bitCoins).toFixed(config.precision);

            $('#currency-input').val(calculateCurrency);
        }
    });

$('#currency-input').blur(function() {
    $('#currency-inputt').html(null);
    $(this).formatCurrency({ symbol: '', colorize: true, positiveFormat: '%n', negativeFormat: '-%s%n', roundToDecimalPlace: 2 });
})
    .keyup(function(e) {
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
            var currencyVal = $(this).toNumber().val();
            var globalLastPrice = $('#legend-last').text();

            var calculateBitCoins =   (currencyVal / globalLastPrice).toFixed(config.precision);
            $('#bitcoin-input').val(calculateBitCoins);
        }
    });

})


var print_r=function(arr, do_alert, level) { var print_red_text = ""; if(!level) {level = 0;} var level_padding = ""; for(var j=0; j<level+1; j++) {level_padding += "    ";} if(typeof(arr) == 'object') { for(var item in arr) { var value = arr[item]; if(typeof(value) == 'object') { print_red_text += level_padding + "'" + item + "' :\n"; print_red_text += print_r(value,level+1); } else {print_red_text += level_padding + "'" + item + "' => \"" + value + "\"\n";} } } else {print_red_text = "===>"+arr+"<===("+typeof(arr)+")";} if(typeof do_alert == 'undefined'){alert(print_red_text);} return print_red_text;}
jQuery.fn.selectText=function(){var doc=document,element=this[0],range,selection; if(doc.body.createTextRange){range=document.body.createTextRange();range.moveToElementText(element);range.select();}else if(window.getSelection){selection=window.getSelection();range=document.createRange();range.selectNodeContents(element);selection.removeAllRanges();selection.addRange(range);}};
jQuery.fn.countObj=function(){var count=0;var obj=this[0];for(i in obj){if(obj.hasOwnProperty(i)){count++;}}return count;};