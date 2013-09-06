var legendSlots = 20;
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

function callAPI(callback){
    if (typeof callback == 'undefined'){
        callback = renderAll;
    }

    if (window.XDomainRequest) {
        var xhr = new window.XDomainRequest();
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

function renderAll(result){
    API_data = result;

//            config.currencyOrder.sort(function(a,b){
//                result[a].total_volume_btc = 0;
//                for (var exchange in result[a].exchanges){
//                    result[a].total_volume_btc += parseInt(result[a].exchanges[exchange].volume_btc);
//                }
//
//                result[b].total_volume_btc = 0;
//                for (var exchange in result[b].exchanges){
//                    result[b].total_volume_btc += parseInt(result[b].exchanges[exchange].volume_btc);
//                }
//                if (result[a].total_volume_btc<result[b].total_volume_btc) {
//                    return 1;
//                } else {
//                    return -1;
//                }
//            });

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
        document.title = API_data[legendClickStatus].averages.last+' '+legendClickStatus+' - BitcoinAverage';
    } else {
        document.title = API_data['USD'].averages.last+' USD - BitcoinAverage';
    }
}

var lastusdvalue = 0;
function renderRates(currencyCode, currencyData, slotNum){
    $('#slot'+slotNum+'-link').attr('data-currencycode', currencyCode);
    $('#slot'+slotNum+'-link a').text(currencyCode);
    $('#slot'+slotNum+'-link a').attr('href', '#'+currencyCode);
    $('#slot'+slotNum+'-link a').show();
    $('#slot'+slotNum+'-box').attr('data-currencycode', currencyCode);
    $('#slot'+slotNum+'-curcode').text(currencyCode);

    var dataChanged = false;
    dataChanged = (dataChanged || $('#slot'+slotNum+'-last').text() != currencyData.averages.last);
    dataChanged = (dataChanged || $('#slot'+slotNum+'-ask').text() != currencyData.averages.ask);
    dataChanged = (dataChanged || $('#slot'+slotNum+'-bid').text() != currencyData.averages.bid);
    $('#slot'+slotNum+'-last').text(currencyData.averages.last);
    $('#slot'+slotNum+'-ask').text(currencyData.averages.ask);
    $('#slot'+slotNum+'-bid').text(currencyData.averages.bid);

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

function renderLegend(currencyCode){
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
        document.title = API_data[currencyCode].averages.last+' '+currencyCode+' - BitcoinAverage';
    }

    $('.legend-curcode').text(currencyCode);
    $('#legend-last').html(currencyData.averages.last);
    $('#legend-bid').html(currencyData.averages.bid);
    $('#legend-ask').html(currencyData.averages.ask);
    $('#legend-total-volume').html(currencyData.averages.total_vol);
    $('#legend-24h-avg').html(currencyData.averages['24h_avg']);


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


        if(slotNum<legendSlots){
            $('#legend-slot'+slotNum+'-name').text(exchangeArray[slotNum]['name']);
            $('#legend-slot'+slotNum+'-volume_btc').text(exchangeArray[slotNum]['volume_btc']);
            $('#legend-slot'+slotNum+'-volume_percent').text(exchangeArray[slotNum]['volume_percent']);
            $('#legend-slot'+slotNum+'-rate').text(exchangeArray[slotNum]['rates']['last']);
            $('#legend-slot'+slotNum).toggle(true);
        } else {
            otherCount = otherCount+1;
            otherPercent = otherPercent+exchangeArray[slotNum]['volume_percent'];
            otherVolume = otherVolume+exchangeArray[slotNum]['volume_btc'];
        }
    }
    if(otherCount > 0){
        $('#slot'+slotNum+'-subslot-other').toggle(true);
        $('#slot'+slotNum+'-subslot-other-count').text(otherCount);
        $('#slot'+slotNum+'-subslot-other-volume_btc').text(otherVolume);
        $('#slot'+slotNum+'-subslot-other-volume_percent').text(otherPercent);
    }
}

function renderSecondsSinceUpdate(){
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

function getTimeGap(timeData){
    var currentRemoteTimestamp = Math.round(Date.parse(timeData['dateString'])/1000);
    var currentLocalTimestamp = Math.round(new Date().getTime()/1000);

    timeGap = currentLocalTimestamp - currentRemoteTimestamp;
}
jQuery.fn.selectText = function(){
    var doc = document
        , element = this[0]
        , range, selection
    ;
    if (doc.body.createTextRange) {
        range = document.body.createTextRange();
        range.moveToElementText(element);
        range.select();
    } else if (window.getSelection) {
        selection = window.getSelection();
        range = document.createRange();
        range.selectNodeContents(element);
        selection.removeAllRanges();
        selection.addRange(range);
    }
};

jQuery.fn.countObj = function(){
    var count = 0;
    var obj = this[0];
    for (i in obj) {
        if (obj.hasOwnProperty(i)) {
            count++;
        }
    }
    return count;
}



//$.get('data/intradata.csv', function(csv) {
//jQuery(function($) { $.get('data/intradata.csv', function(csv) {
//    var start = + new Date(); // parse the CSV data
//    var data = [], volume = [], header, comment = /^#/, x;
//    $.each(csv.split('\n'), function(i, line){
//        if (!comment.test(line)) {
//            if (!header) {
//                header = line;
//            } else if (line.length) {
//                var point = line.split(','), date = point[0].split('-'), time = point[1].split(':');
//                x = Date.UTC(date[2], date[1] - 1, date[0], time[0], time[1], time[2]);
//                data.push([ parseFloat( x ));
//            }
//        }
//        // time parseFloat(point[2]), // O parseFloat(point[3]), // H parseFloat(point[4]), // L parseFloat(point[5]) // C
//        volume.push([ parseFloat( x ), parseFloat(point[6])]);
//    })
//}, volume)
//
//});