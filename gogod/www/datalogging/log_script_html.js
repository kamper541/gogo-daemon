var params = getUrlParameter();
var config = {default_image_value:500, hasSnapshots:false};
var chart_names = [];
var image_list = [];
var image_dict = {};
var recentUpdate = {};
var isLoading = {};
var seriesOptions = [],
seriesCounter = 0,
names = getLogNameFromUrl();

$(function () {
	config.dynamic = ("dynamic" in params && params.dynamic=='true');
	if (! ("dynamic" in params)) { config.dynamic = true; }
	$('[name=auto_update]').prop( "checked", config.dynamic );
	checkHasSnapshots();
	//Create empty chart
	createChart(false);
	chart.showLoading();
	initData();
//	initImageView();
});

	function checkHasSnapshots(){
		var snapshotsIndex = names.indexOf('snapshots');
		if ( snapshotsIndex > -1){
				names.splice(snapshotsIndex, 1);
				config.hasSnapshots = true;
		}
	}
	function initData(){

		$.each(names, function (i, name) {

				console.log("Loading...");
				// var fetch_url = '/api/datalog/get/'+name;
				var fetch_url = '/media/log/'+name+'.csv';
				$.get(fetch_url,    function (data) {
					var list = []
					if (data){
						var fetch_data = data.split("\r\n");
						$.each(fetch_data, function (index, record) {
							var entry = record.split(",");
							if (entry.length == 2){
								var parsedData = parseDataLog({datetime:entry[0],value:entry[1]});
								list.push([parsedData.datetime, parsedData.value ]);
							}
						});
					}

					//recentUpdate[name] =  data.result[data.result.length-1].datetime;
					isLoading[name] =  false;
					seriesOptions[seriesCounter] = {
						name: name,
						data: list
					};
					chart_names[seriesCounter] = name;
				}).always(function() {
					// As we're loading the data asynchronously, we don't know what order it will arrive. So
					// we keep a counter and create the chart when all the data is loaded.
					seriesCounter += 1;

					if (seriesCounter === names.length) {
						createChart(true);
						chart.hideLoading();
						initImageView();
					}

				});

		});

		if (names.length===0){
		    createChart(true);
		    initImageView();
		}


	}

	function initImageView(){
		if (!config.hasSnapshots) {
		    chart.hideLoading();
		    return;
		}
		console.log("Loading image list...");

		var name = 'snapshots';
		// var fetch_url = '/api/datalog/get/'+name;
		var fetch_url = '/api/image/list';
		$.getJSON(fetch_url,    function (data) {

			var list = []
			if (data.data){
				// var fetch_data = data.data.split("\r\n");
				$.each(data.data, function (index, entry) {
					if (entry.length == 2){

						var parsedData = parseDataLog({datetime:entry[0],value:config.default_image_value});
						list.push([parsedData.datetime, parsedData.value ]);
						image_list.push(entry[1]);
						image_dict[parsedData.datetime] = entry[1];
					}
				});
				hasData = true;
			}

			//recentUpdate[name] =  data.result[data.result.length-1].datetime;
			isLoading[name] =  false;
			seriesOption = {
				name: name,
				data: list,
				dataGrouping : {enabled:false},
				tooltip: {
					useHTML: true,
					pointFormat: '<span style="color:{series.color}"></span> <a id="tooltip_link" href="#" target="_blank"><img width="250" height="187" /></a>',
					valueDecimals: 2
				},
                marker: {
					    enabled: true,
					    radius: 3
                    },
				point : {
					events: {
							click: function (event) {
									// console.log(this.name + ' clicked\n' +
									// 		'y: ' + event.pageY + '\n' +
									// 		'x: ' + event.pageX + '\n');
									showImage(this.index);
							},
							mouseOver: function (event) {
									// console.log(this.name + ' over\n' +
									// 		'y: ' + event.target.plotY + '\n' +
									// 		'x: ' + event.target.plotX + '\n');
									showImage(this.index, this.x);
							},

					}
				}
			};

			var result = chart.addSeries(seriesOption);
			chart_names[result._i] = name;

			chart.hideLoading();

		})

	}

	var currentIndex = -1;
	var currentTimestamp = 0;
	function showImage(index, timestamp){
		if (timestamp == currentTimestamp) return;

		currentIndex = index;
		currentTimestamp = timestamp;
		var image_src = '/media/snapshots/'+image_dict[timestamp]

		$('#tooltip_link').attr('href',image_src);
		$('#tooltip_link img').attr('src',image_src);

	}

	function createChart(hasData) {

		$('#container').highcharts('StockChart', {
			chart : {
				events : {
					load : function () {
						// console.log(recentUpdate);
						//Except the last one
						if (!hasData) {return;}
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
					useHTML: true,
					pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b><br/>',
					valueDecimals: 2
				},
				credits: {enabled :false},

				series: (hasData ? seriesOptions : [] )
			});

			chart = $('#container').highcharts();
		};

function setHeader(xhr) {
  xhr.setRequestHeader('Authorization', 'Basic YWRtaW46YWRtaW4=');
}

function getUrlParameter(sParam) {
	var sPageURL = window.location.search.substring(1);
	var sURLVariables = sPageURL.split('&');
	var datas = {};
	for (var i = 0; i < sURLVariables.length; i++)
	{
		var sParameterName = sURLVariables[i].split('=');
		datas[sParameterName[0]] = sParameterName[1];
		if (sParameterName[0] == sParam)
		{
			return sParameterName[1];
		}
	}
	return datas;
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

	// var datalog_names = [];
	// $.each(series, function (i, detail) {
	// 	datalog_names[i] = detail.name;
	// 	return;
	// });

	var ws = new ReconnectingWebSocket("ws://"+window.location.host+"/ws");
	ws.onmessage = function (evt) {

		if (!$('[name=auto_update]').prop( "checked" )){
			return;
		}

		var cmd = evt.data.split(",");
		if (cmd[0] == "datalog") {

			var packet_str = cmd.slice(1).join(',');
			var packet = JSON.parse(packet_str);
			var record = parseDataLog(packet);
			var record_index = chart_names.indexOf(record.name);

			if (record_index != -1){
			    if (record.name == 'snapshots') {
			        chart.series[record_index].addPoint([record.datetime, config.default_image_value], true, true);
			        image_list.push(record.filename);
			        image_dict[record.datetime] = record.filename;
			    } else {
			        chart.series[record_index].addPoint([record.datetime,record.value], true, true);
			    }

			}
		}
	}
}
