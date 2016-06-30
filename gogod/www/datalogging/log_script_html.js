var log_series = [];
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
		                	// console.log(recentUpdate);
                            //Except the last one
                            var series2 = this.series.slice(0,this.series.length-1);
                            handleLoaded(series2);

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
            var fetch_url = '/api/datalog/fetch/'+name;

            $.getJSON(fetch_url,    function (data) {

                var list = []
                if (data.data){
                    var fetch_data = data.data.split("\r\n");
                    $.each(fetch_data, function (index, record) {
                        var entry = record.split(",");
                        if (entry.length == 2){
                            var parsedData = parseDataLog({datetime:entry[0],value:entry[1]});
                            list.push([parsedData.datetime, parsedData.value ]);    
                        }
                        //list.push([Date.parse(record.datetime.substring(0, record.datetime.length-7)),record.value]);
                    });
                }

                //recentUpdate[name] =  data.result[data.result.length-1].datetime;
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

function parseDataLog(data){
    var date = new Date(data.datetime);
    var localdate = date-2*date.getTimezoneOffset()*60*1000;
    data.datetime = localdate;
    data.value    = Number(data.value);
    return data;
    //var localdate = Date.parse(record.datetime);
}

function handleLoaded(series){

    var datalog_names = [];
    $.each(series, function (i, detail) {
        datalog_names[i] = detail.name;
        return;
    });

    var ws = new ReconnectingWebSocket("ws://"+window.location.hostname+":8888/ws");
    ws.onmessage = function (evt) {

        if (!$('[name=auto_update]').prop( "checked" )){
            return;
        }

        var cmd = evt.data.split(",");
        if (cmd[0] == "datalog") {

            var packet_str = cmd.slice(1).join(',');
            var packet = JSON.parse(packet_str);
            var record = parseDataLog(packet);
            var record_index = datalog_names.indexOf(record.name);
            if (record_index != -1){
                series[record_index].addPoint([record.datetime,record.value], true, true);
            }
        }
    }
}