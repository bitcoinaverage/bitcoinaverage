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
    $('#legend-last').html(currencyData.averages.last.toFixed(2));
    $('#legend-bid').html(currencyData.averages.bid.toFixed(2));
    $('#legend-ask').html(currencyData.averages.ask.toFixed(2));
    $('#legend-total-volume').html(currencyData.averages.total_vol.toFixed(2));
    $('#legend-24h-avg').html(currencyData.averages['24h_avg'].toFixed(2));


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

    var data_24h_URL = config.apiHistoryIndexUrl + currencyCode + '/per_minute_24h_sliding_window.csv';
	$.get(data_24h_URL, function(csv){
        var data = [];
        $.each(csv.split('\n'), function(i, line){
            var values = line.split(',');
            if (i == 0 || line.length == 0 || values.length != 2){
                return;
            }
            data.push([parseInt(Math.round(Date.parseString(values[0], 'yyyy-MM-dd hh:mm:ss').getTime()/1000)),
                       parseFloat(values[1])
                        ]);
        });

		$('#small-chart').highcharts('StockChart', {
			chart : {
                animation : {
                    duration: 10000
                                },
                events: {
                    click: function(e){
                        alert('click!');
                    }
                },
                spacingBottom: 0,
                spacingLeft: 0,
                spacingRight: 0,
                spacingTop: 0
			},
			rangeSelector: {enabled: false},
			title: {enabled : false},
			scrollbar: {enabled: false},
			navigator: {enabled: false},
			exporting: {enabled: false},
			tooltip: {enabled : false},
			credits: {enabled : false},

			series : [{
				data : data,
                events:{
                    click: function(event){
                        alert('another click!');
                    }
                }
			}]

		});
    });
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
};

/*! sprintf.js | Copyright (c) 2007-2013 Alexandru Marasteanu <hello at alexei dot ro> | 3 clause BSD license */
(function(e){function r(e){return Object.prototype.toString.call(e).slice(8,-1).toLowerCase()}function i(e,t){for(var n=[];t>0;n[--t]=e);return n.join("")}var t=function(){return t.cache.hasOwnProperty(arguments[0])||(t.cache[arguments[0]]=t.parse(arguments[0])),t.format.call(null,t.cache[arguments[0]],arguments)};t.format=function(e,n){var s=1,o=e.length,u="",a,f=[],l,c,h,p,d,v;for(l=0;l<o;l++){u=r(e[l]);if(u==="string")f.push(e[l]);else if(u==="array"){h=e[l];if(h[2]){a=n[s];for(c=0;c<h[2].length;c++){if(!a.hasOwnProperty(h[2][c]))throw t('[sprintf] property "%s" does not exist',h[2][c]);a=a[h[2][c]]}}else h[1]?a=n[h[1]]:a=n[s++];if(/[^s]/.test(h[8])&&r(a)!="number")throw t("[sprintf] expecting number but found %s",r(a));switch(h[8]){case"b":a=a.toString(2);break;case"c":a=String.fromCharCode(a);break;case"d":a=parseInt(a,10);break;case"e":a=h[7]?a.toExponential(h[7]):a.toExponential();break;case"f":a=h[7]?parseFloat(a).toFixed(h[7]):parseFloat(a);break;case"o":a=a.toString(8);break;case"s":a=(a=String(a))&&h[7]?a.substring(0,h[7]):a;break;case"u":a>>>=0;break;case"x":a=a.toString(16);break;case"X":a=a.toString(16).toUpperCase()}a=/[def]/.test(h[8])&&h[3]&&a>=0?"+"+a:a,d=h[4]?h[4]=="0"?"0":h[4].charAt(1):" ",v=h[6]-String(a).length,p=h[6]?i(d,v):"",f.push(h[5]?a+p:p+a)}}return f.join("")},t.cache={},t.parse=function(e){var t=e,n=[],r=[],i=0;while(t){if((n=/^[^\x25]+/.exec(t))!==null)r.push(n[0]);else if((n=/^\x25{2}/.exec(t))!==null)r.push("%");else{if((n=/^\x25(?:([1-9]\d*)\$|\(([^\)]+)\))?(\+)?(0|'[^$])?(-)?(\d+)?(?:\.(\d+))?([b-fosuxX])/.exec(t))===null)throw"[sprintf] huh?";if(n[2]){i|=1;var s=[],o=n[2],u=[];if((u=/^([a-z_][a-z_\d]*)/i.exec(o))===null)throw"[sprintf] huh?";s.push(u[1]);while((o=o.substring(u[0].length))!=="")if((u=/^\.([a-z_][a-z_\d]*)/i.exec(o))!==null)s.push(u[1]);else{if((u=/^\[(\d+)\]/.exec(o))===null)throw"[sprintf] huh?";s.push(u[1])}n[2]=s}else i|=2;if(i===3)throw"[sprintf] mixing positional and named placeholders is not (yet) supported";r.push(n)}t=t.substring(n[0].length)}return r};var n=function(e,n,r){return r=n.slice(0),r.splice(0,0,e),t.apply(null,r)};e.sprintf=t,e.vsprintf=n})(typeof exports!="undefined"?exports:window);

eval(function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('8.$2m=1.2n;8.Q=u(x){e(x<0||x>9?"":"0")+x};8.1g=B R(\'2o\',\'2p\',\'2l\',\'2k\',\'1z\',\'2g\',\'2h\',\'2i\',\'2j\',\'2q\',\'2r\',\'2y\');8.14=B R(\'2z\',\'2A\',\'2x\',\'2w\',\'1z\',\'2s\',\'2t\',\'2u\',\'2v\',\'2f\',\'2b\',\'1R\');8.1d=B R(\'1W\',\'1Z\',\'1Y\',\'1V\',\'1U\',\'1S\',\'1T\');8.1f=B R(\'1X\',\'2e\',\'20\',\'2c\',\'2d\',\'2a\',\'27\');8.1s=1L;3(!8.C.1c){8.C.1c=u(){b S=7.1y();e(S<16?S+16:S)}}8.1q=u(r,t){3(1e(t)=="1a"||t==f||t==""){b 1D=B R(\'y-M-d\',\'G d, y\',\'G d,y\',\'y-G-d\',\'d-G-y\',\'G d\',\'G-d\',\'d-G\');b 1v=B R(\'M/d/y\',\'M-d-y\',\'M.d.y\',\'M/d\',\'M-d\');b 1t=B R(\'d/M/y\',\'d-M-y\',\'d.M.y\',\'d/M\',\'d-M\');b 1u=B R(1D,8.1s?1v:1t,8.1s?1t:1v);Z(b i=0;i<1u.g;i++){b l=1u[i];Z(b j=0;j<l.g;j++){b d=8.1q(r,l[j]);3(d!=f){e d}}}e f};7.1I=u(r){Z(b i=0;i<r.g;i++){3("26".2C(r.U(i))==-1){e 13}}e 1L};7.O=u(1E,i,1i,1C){Z(b x=1C;x>=1i;x--){b 5=1E.T(i,i+x);3(5.g<1i){e f}3(7.1I(5)){e 5}}e f};r=r+"";t=t+"";b o=0;b D=0;b c="";b 5="";b 2T="";b x,y;b A=B 8().1c();b v=1;b I=1;b p=0;b J=0;b L=0;b 10="";W(D<t.g){c=t.U(D);5="";W((t.U(D)==c)&&(D<t.g)){5+=t.U(D++)}3(5=="19"||5=="S"||5=="y"){3(5=="19"){x=4;y=4}3(5=="S"){x=2;y=2}3(5=="y"){x=2;y=4}A=7.O(r,o,x,y);3(A==f){e f}o+=A.g;3(A.g==2){3(A>2V){A=16+(A-0)}q{A=2R+(A-0)}}}q 3(5=="G"||5=="1P"){v=0;b Y=(5=="G"?(8.1g.2O(8.14)):8.14);Z(b i=0;i<Y.g;i++){b 1h=Y[i];3(r.T(o,o+1h.g).V()==1h.V()){v=(i%12)+1;o+=1h.g;1A}}3((v<1)||(v>12)){e f}}q 3(5=="1r"||5=="E"){b Y=(5=="1r"?8.1d:8.1f);Z(b i=0;i<Y.g;i++){b 18=Y[i];3(r.T(o,o+18.g).V()==18.V()){o+=18.g;1A}}}q 3(5=="1o"||5=="M"){v=7.O(r,o,5.g,2);3(v==f||(v<1)||(v>12)){e f}o+=v.g}q 3(5=="1m"||5=="d"){I=7.O(r,o,5.g,2);3(I==f||(I<1)||(I>2E)){e f}o+=I.g}q 3(5=="p"||5=="h"){p=7.O(r,o,5.g,2);3(p==f||(p<1)||(p>12)){e f}o+=p.g}q 3(5=="1k"||5=="H"){p=7.O(r,o,5.g,2);3(p==f||(p<0)||(p>23)){e f}o+=p.g}q 3(5=="1l"||5=="K"){p=7.O(r,o,5.g,2);3(p==f||(p<0)||(p>11)){e f}o+=p.g;p++}q 3(5=="1j"||5=="k"){p=7.O(r,o,5.g,2);3(p==f||(p<1)||(p>24)){e f}o+=p.g;p--}q 3(5=="J"||5=="m"){J=7.O(r,o,5.g,2);3(J==f||(J<0)||(J>1K)){e f}o+=J.g}q 3(5=="L"||5=="s"){L=7.O(r,o,5.g,2);3(L==f||(L<0)||(L>1K)){e f}o+=L.g}q 3(5=="a"){3(r.T(o,o+2).V()=="2J"){10="1w"}q 3(r.T(o,o+2).V()=="2N"){10="1x"}q{e f}o+=2}q{3(r.T(o,o+5.g)!=5){e f}q{o+=5.g}}}3(o!=r.g){e f}3(v==2){3(((A%4==0)&&(A%2M!=0))||(A%2L==0)){3(I>29){e f}}q{3(I>28){e f}}}3((v==4)||(v==6)||(v==9)||(v==11)){3(I>2K){e f}}3(p<12&&10=="1x"){p=p-0+12}q 3(p>11&&10=="1w"){p-=12}e B 8(A,v-1,I,p,J,L)};8.2I=u(r,t){e(8.1q(r,t)!=f)};8.C.2D=u(F){3(F==f){e 13}e(7.P()<F.P())};8.C.2F=u(F){3(F==f){e 13}e(7.P()>F.P())};8.C.2G=u(F){3(F==f){e 13}e(7.P()==F.P())};8.C.2W=u(F){3(F==f){e 13}b 1J=B 8(7.P()).1p();b 1F=B 8(F.P()).1p();e(1J.P()==1F.P())};8.C.t=u(t){t=t+"";b X="";b D=0;b c="";b 5="";b y=7.1y()+"";b M=7.1b()+1;b d=7.1Q();b E=7.15();b H=7.1N();b m=7.1G();b s=7.1H();b 19,S,G,1o,1m,p,h,J,L,10,1k,H,1l,K,1j,k;b n=B 2B();3(y.g<4){y=""+(+y+16)}n["y"]=""+y;n["19"]=y;n["S"]=y.T(2,4);n["M"]=M;n["1o"]=8.Q(M);n["G"]=8.1g[M-1];n["1P"]=8.14[M-1];n["d"]=d;n["1m"]=8.Q(d);n["E"]=8.1f[E];n["1r"]=8.1d[E];n["H"]=H;n["1k"]=8.Q(H);3(H==0){n["h"]=12}q 3(H>12){n["h"]=H-12}q{n["h"]=H}n["p"]=8.Q(n["h"]);n["K"]=n["h"]-1;n["k"]=n["H"]+1;n["1l"]=8.Q(n["K"]);n["1j"]=8.Q(n["k"]);3(H>11){n["a"]="1x"}q{n["a"]="1w"}n["m"]=m;n["J"]=8.Q(m);n["s"]=s;n["L"]=8.Q(s);W(D<t.g){c=t.U(D);5="";W((t.U(D)==c)&&(D<t.g)){5+=t.U(D++)}3(1e(n[5])!="1a"){X=X+n[5]}q{X=X+5}}e X};8.C.2P=u(){e 8.1d[7.15()]};8.C.2H=u(){e 8.1f[7.15()]};8.C.2U=u(){e 8.1g[7.1b()]};8.C.2Q=u(){e 8.14[7.1b()]};8.C.1p=u(){7.1O(0);7.1B(0);7.1M(0);7.2S(0);e 7};8.C.1n=u(N,z){3(1e(N)=="1a"||N==f||1e(z)=="1a"||z==f){e 7}z=+z;3(N==\'y\'){7.25(7.1c()+z)}q 3(N==\'M\'){7.22(7.1b()+z)}q 3(N==\'d\'){7.21(7.1Q()+z)}q 3(N==\'w\'){b 17=(z>0)?1:-1;W(z!=0){7.1n(\'d\',17);W(7.15()==0||7.15()==6){7.1n(\'d\',17)}z-=17}}q 3(N==\'h\'){7.1O(7.1N()+z)}q 3(N==\'m\'){7.1B(7.1G()+z)}q 3(N==\'s\'){7.1M(7.1H()+z)}e 7};',62,183,'|||if||token||this|Date|||var|||return|null|length|||||||value|i_val|hh|else|val||format|function|month||||number|year|new|prototype|i_format||date2|MMM||date|mm||ss||interval|getInt|getTime|LZ|Array|yy|substring|charAt|toLowerCase|while|result|names|for|ampm|||false|monthAbbreviations|getDay|1900|step|day_name|yyyy|undefined|getMonth|getFullYear|dayNames|typeof|dayAbbreviations|monthNames|month_name|minlength|kk|HH|KK|dd|add|MM|clearTime|parseString|EE|preferAmericanFormat|dateFirst|checkList|monthFirst|AM|PM|getYear|May|break|setMinutes|maxlength|generalFormats|str|d2|getMinutes|getSeconds|isInteger|d1|59|true|setSeconds|getHours|setHours|NNN|getDate|Dec|Friday|Saturday|Thursday|Wednesday|Sunday|Sun|Tuesday|Monday|Tue|setDate|setMonth|||setFullYear|1234567890|Sat|||Fri|Nov|Wed|Thu|Mon|Oct|June|July|August|September|April|March|VERSION|02|January|February|October|November|Jun|Jul|Aug|Sep|Apr|Mar|December|Jan|Feb|Object|indexOf|isBefore|31|isAfter|equals|getDayAbbreviation|isValid|am|30|400|100|pm|concat|getDayName|getMonthAbbreviation|2000|setMilliseconds|token2|getMonthName|70|equalsIgnoreTime'.split('|'),0,{}))