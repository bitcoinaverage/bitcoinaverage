(function(d){d.formatCurrency={};d.formatCurrency.regions=[];d.formatCurrency.regions[""]={symbol:"$",positiveFormat:"%s%n",negativeFormat:"(%s%n)",decimalSymbol:".",digitGroupSymbol:",",groupDigits:true};
d.fn.formatCurrency=function(e,f){if(arguments.length==1&&typeof e!=="string"){f=e;e=false}var g={name:"formatCurrency",colorize:false,region:"",global:true,roundToDecimalPlace:2,eventOnDecimalsEntered:false};
g=d.extend(g,d.formatCurrency.regions[""]);f=d.extend(g,f);if(f.region.length>0){f=d.extend(f,b(f.region))}f.regex=a(f);return this.each(function(){$this=d(this);
var o="0";o=$this[$this.is("input, select, textarea")?"val":"html"]();if(o.search("\\(")>=0){o="-"+o}if(o===""||(o==="-"&&f.roundToDecimalPlace===-1)){return
}if(isNaN(o)){o=o.replace(f.regex,"");if(o===""||(o==="-"&&f.roundToDecimalPlace===-1)){return}if(f.decimalSymbol!="."){o=o.replace(f.decimalSymbol,".")
}if(isNaN(o)){o="0"}}var m=String(o).split(".");var r=(o==Math.abs(o));var l=(m.length>1);var k=(l?m[1].toString():"0");var j=k;o=Math.abs(m[0]);
o=isNaN(o)?0:o;if(f.roundToDecimalPlace>=0){k=parseFloat("1."+k);k=k.toFixed(f.roundToDecimalPlace);if(k.substring(0,1)=="2"){o=Number(o)+1}k=k.substring(2)
}o=String(o);if(f.groupDigits){for(var n=0;n<Math.floor((o.length-(1+n))/3);n++){o=o.substring(0,o.length-(4*n+3))+f.digitGroupSymbol+o.substring(o.length-(4*n+3))
}}if((l&&f.roundToDecimalPlace==-1)||f.roundToDecimalPlace>0){o+=f.decimalSymbol+k}var q=r?f.positiveFormat:f.negativeFormat;var h=q.replace(/%s/g,f.symbol);
h=h.replace(/%n/g,o);var p=d([]);if(!e){p=$this}else{p=d(e)}p[p.is("input, select, textarea")?"val":"html"](h);if(l&&f.eventOnDecimalsEntered&&j.length>f.roundToDecimalPlace){p.trigger("decimalsEntered",j)
}if(f.colorize){p.css("color",r?"black":"red")}})};d.fn.toNumber=function(e){var f=d.extend({name:"toNumber",region:"",global:true},d.formatCurrency.regions[""]);
e=jQuery.extend(f,e);if(e.region.length>0){e=d.extend(e,b(e.region))}e.regex=a(e);return this.each(function(){var g=d(this).is("input, select, textarea")?"val":"html";
d(this)[g](d(this)[g]().replace("(","(-").replace(e.regex,""))})};d.fn.asNumber=function(f){var g=d.extend({name:"asNumber",region:"",parse:true,parseType:"Float",global:true},d.formatCurrency.regions[""]);
f=jQuery.extend(g,f);if(f.region.length>0){f=d.extend(f,b(f.region))}f.regex=a(f);f.parseType=c(f.parseType);var h=d(this).is("input, select, textarea")?"val":"html";
var e=d(this)[h]();e=e?e:"";e=e.replace("(","(-");e=e.replace(f.regex,"");if(!f.parse){return e}if(e.length==0){e="0"}if(f.decimalSymbol!="."){e=e.replace(f.decimalSymbol,".")
}return window["parse"+f.parseType](e)};function b(g){var f=d.formatCurrency.regions[g];if(f){return f}else{if(/(\w+)-(\w+)/g.test(g)){var e=g.replace(/(\w+)-(\w+)/g,"$1");
return d.formatCurrency.regions[e]}}return null}function c(e){switch(e.toLowerCase()){case"int":return"Int";case"float":return"Float";default:throw"invalid parseType"
}}function a(e){if(e.symbol===""){return new RegExp("[^\\d"+e.decimalSymbol+"-]","g")}else{var f=e.symbol.replace("$","\\$").replace(".","\\.");
return new RegExp(f+"|[^\\d"+e.decimalSymbol+"-]","g")}}})(jQuery);