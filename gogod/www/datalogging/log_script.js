$(function () {
	var recentUpdate = {};
    var isLoading = {};
    var seriesOptions = [],
        seriesCounter = 0,
        names = getLogNameFromUrl(),//, 'AAPL', 'GOOG'],
        // create the chart when all data is loaded
        createChart = function () {

            $('#container').highcharts('StockChart', {
		        chart : {
		            events : {
		                load : function () {
		                	console.log(recentUpdate);
		                    // set up the updating of the chart each second
		                    // var series = this.series[0];
		                    var series2 = this.series;
                                $.each(series2, function (i, detail) {
                                    if (i!=series2.length-1){
                                        setInterval(function () {
                                            if ($('[name=auto_update]').prop( "checked" ) && isLoading[detail.name] ==  false){
                                                    isLoading[detail.name] =  true;
                                                    //console.log(detail.name+"==========================================="+recentUpdate[detail.name]);
                                                    
                                                    var fetch = $.getJSON('http://reader:reader@'+window.location.hostname+':2480/function/logger/logafter/'+detail.name+'/'+recentUpdate[detail.name]+'/100?callback=?',    function (data) {

                                                    //$.getJSON('http://reader:reader@'+window.location.hostname+':2480/function/logger/logafter/'+detail.name+'/'+recentUpdate[detail.name]+'/1000?callback=?',    function (data) {
                                                    
                                                            $.each(data.result, function (index, record) {
                                                            	var date = new Date(record.datetime);
                												var localdate = date-2*date.getTimezoneOffset()*60*1000;
                                                                detail.addPoint([localdate,record.value], true, true);
                                                            });
                                                    
                                                            if (data.result.length>0){
                                                               recentUpdate[detail.name] =  data.result[data.result.length-1].datetime;
                                                               console.log(detail.name + " new "+data.result.length)
                                                            }
                                                            if (data.result.length>-1) {
                                                                isLoading[detail.name] =  false;
                                                            }
                                                    });
                                            }
                                            }, 1000);
                                    }
                                });
		                }
		            }
		        },

                rangeSelector: {
                    //selected: 4,
                    buttons: [
                    {
                        type: 'minute',
                        count: 5,
                        text: '5min'
                    },
                    {
                        type: 'hour',
                        count: 1,
                        text: '1hr'
                    },
                    {
                        type: 'day',
                        count: 1,
                        text: '1d'
                    },
                    {
                        type: 'week',
                        count: 1,
                        text: '1w'
                    },
                    {
                        type: 'month',
                        count: 1,
                        text: '1m'
                    }, {
                        type: 'ytd',
                        text: 'YTD'
                    }, {
                        type: 'year',
                        count: 1,
                        text: '1y'
                    }, {
                        type: 'all',
                        text: 'All'
                    }]
                },

                yAxis: {
                    // labels: {
                    //     formatter: function () {
                    //         return (this.value > 0 ? ' + ' : '') + this.value + '%';
                    //     }
                    // },
                    plotLines: [{
                        value: 0,
                        width: 2,
                        color: 'silver'
                    }]
                },
				legend: {
					enabled: true,
		            layout: 'vertical',
		            align: 'right',
		            verticalAlign: 'middle',
		            borderWidth: 0
		        },
                plotOptions: {
                    // series: {
                    //     compare: 'percent'
                    // }
                     bar: {
                        dataLabels: {
                            enabled: true
                        }
                    }

                },

                tooltip: {
                    pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b><br/>',
                    valueDecimals: 2
                },

                series: seriesOptions
            });
        };

    $.each(names, function (i, name) {

            console.log("Loading...");
/*
              $.ajax({
                url: 'http://'+window.location.hostname+':2480/cluster/logger/'+name+'/0?callback=?',
                type: 'GET',
                contentType: 'application/json',
                datatype: 'jsonp',
                success: function(data) { console.log(data) },
                error: function() { alert('Failed!'); },
                beforeSend: setHeader       
              }); 
*/

        var fetch_url = 'http://reader:reader@'+window.location.hostname+':2480/function/logger/logafter/'+name+'/0/-1?callback=?'

        if (getReduce()){
            fetch_url = 'http://reader:reader@'+window.location.hostname+':2480/function/logger/reduce/'+name+'/'+getBy()+'/0/-1?callback=?'
        }
//        $.getJSON('http://reader:reader@'+window.location.hostname+':2480/function/logger/reduce/'+name+'/minute/0/-1?callback=?',    function (data) {
	$.getJSON(fetch_url,    function (data) {
//        $.getJSON('http://reader:reader@'+window.location.hostname+':2480/function/logger/logafter/'+name+'/0/-1?callback=?',    function (data) {
			
            var list = []
           
            $.each(data.result, function (index, record) {
                //list.push([Date.parse(record.datetime.substring(0, record.datetime.length-7)),record.value]);
                var date = new Date(record.datetime);
                var localdate = date-2*date.getTimezoneOffset()*60*1000;
                //var localdate = Date.parse(record.datetime);
                list.push([localdate,record.value]);
            });
            recentUpdate[name] =  data.result[data.result.length-1].datetime;
            
            isLoading[name] =  false;
            seriesOptions[i] = {
                name: name,
                data: list
            };

            // As we're loading the data asynchronously, we don't know what order it will arrive. So
            // we keep a counter and create the chart when all the data is loaded.
            seriesCounter += 1;

            if (seriesCounter === names.length) {
                createChart();
            }
            
        });
    });
});
function setHeader(xhr) {
  xhr.setRequestHeader('Authorization', 'Basic YWRtaW46YWRtaW4=');
}

function getUrlParameter(sParam)
{
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i++) 
    {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == sParam) 
        {
            return sParameterName[1];
        }
    }
}

function getLogNameFromUrl() {
	return getUrlParameter("name").split(",");
}
function getReduce() {
    if (getUrlParameter("average")==undefined){
        return false;
    } else if (getUrlParameter("average")=="true"){
        return true;
    } else {
        return false;
    }
}
function getBy() {
    if (getUrlParameter("by")==undefined){
        return 'minute';
    } else {
        return getUrlParameter("by");
    }
}