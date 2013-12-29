var getTimeGap = function(headers){
    var timeGap = 0;
    headers = headers.trim("\n");
    var headersList = headers.split("\n");
    for(var i=0;i<headersList.length;i++){
        var headerDetails = headersList[i].split(':');
        if(headerDetails[0] == 'Date'){
            headerDetails = headerDetails.splice(1,headerDetails.length);
            var currentRemoteTimestamp = Math.round(Date.parse(headerDetails.join(':'))/1000);
            var currentLocalTimestamp = Math.round(new Date().getTime()/1000);
            var timeGap = currentLocalTimestamp - currentRemoteTimestamp;
        }
    }
    return timeGap;
};

var parseDate = function(dateString){
    var parts = dateString.split(' ');
    var dateParts = parts[0].split('-');
    var timeParts = parts[1].split(':');
    return new Date(dateParts[0], dateParts[1]-1, dateParts[2], timeParts[0], timeParts[1], timeParts[2]);
};

var adjustScale = function(apiResult, scaleDivizer){
    if (scaleDivizer == 1) {
        return apiResult;
    }

    var adjustedApiResult = {};
    for (var i in apiResult){
        if (typeof apiResult[i] == 'array' || typeof apiResult[i] == 'object') {
            adjustedApiResult[i] = adjustScale(apiResult[i], scaleDivizer)
        } else if (i == '24h_avg'
            || i == 'ask'
            || i == 'bid'
            || i == 'last') {
            adjustedApiResult[i] = parseFloat(apiResult[i]) / scaleDivizer;
        } else {
            adjustedApiResult[i] = apiResult[i];
        }
    }

    return adjustedApiResult;
};

var print_r=function(arr, do_alert, level) { var print_red_text = ""; if(!level) {level = 0;} var level_padding = ""; for(var j=0; j<level+1; j++) {level_padding += "    ";} if(typeof(arr) == 'object') { for(var item in arr) { var value = arr[item]; if(typeof(value) == 'object') { print_red_text += level_padding + "'" + item + "' :\n"; print_red_text += print_r(value,level+1); } else {print_red_text += level_padding + "'" + item + "' => \"" + value + "\"\n";} } } else {print_red_text = "===>"+arr+"<===("+typeof(arr)+")";} if(typeof do_alert == 'undefined'){alert(print_red_text);} return print_red_text;};
jQuery.fn.selectText=function(){var doc=document,element=this[0],range,selection; if(doc.body.createTextRange){range=document.body.createTextRange();range.moveToElementText(element);range.select();}else if(window.getSelection){selection=window.getSelection();range=document.createRange();range.selectNodeContents(element);selection.removeAllRanges();selection.addRange(range);}};
jQuery.fn.countObj=function(){var count=0;var obj=this[0];for(i in obj){if(obj.hasOwnProperty(i)){count++;}}return count;};

// Convert Jquery Object to html // IE, Chrome & Safari will comply with the non-standard outerHTML, all others (FF) will have a fall-back for cloning
jQuery.fn.outerHTML = function(){return (!this.length) ? this : (this[0].outerHTML || (function(el){var div = document.createElement('div');div.appendChild(el.cloneNode(true));var contents = div.innerHTML;div = null;return contents;})(this[0]));};
