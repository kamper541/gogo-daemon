/*--------------------------------------------------------------------
 Description:	Detecting all button in the page and handle when click the button
 				, Send name and value of the button to websocket
 Authors:		Marutpong Chailangka
 Created:		2015-04-15
---------------------------------------------------------------------*/
var buttons = $( ":button, button, input[type='button'], input[type='submit'],[data-role='button']" );
var slider = "input[type='number'], [data-type='range'], input[type='range'],select";
var input_select = ",input[type='text']";
var slider_values = [];

var ws = new ReconnectingWebSocket("ws://"+window.location.host+"/ws");

// when data is comming from the server, this metod is called
        ws.onmessage = function (evt) {
            cmd = evt.data.split(",");
            if (cmd[0] == "play_sound") {
				//var aud = new Audio("/media/" + cmd[1]);
				//aud.play();				
				var aud = document.getElementById("sound");
				aud.volume=1;
				// Adds a uniqute time parameter so the browser re-loads
				// the image instead of using the cached one
				if (currentSound!==cmd[1]){
					aud.src = "/media/" + cmd[1];
					currentSound = cmd[1];
				}
				aud.play()
			} else if (cmd[0] == "say"){
				console.log("saying :  "+cmd[1]);
				speak(cmd[1]);
			}
        };


function sendEventKeyValue(key,value) {
	var string = "keyvalue,"+key+","+value;
	ws.send(string);
}

function speak(phrase){
	var msg = new SpeechSynthesisUtterance(phrase);
	window.speechSynthesis.speak(msg);
}

$(buttons).on( "click", function(event) {
    event.preventDefault();

	var key = "button";
	if ($( this ).attr('name')){
		key = $( this ).attr('name');
	} else if ($( this ).attr('id')){
		key = $( this ).attr('id');
	}

	var value = "";
	if ($( this ).val()){
		value = $( this ).val();
	} else if ($( this ).attr('value')){
		value = $( this ).attr('value');
	} else if ($( this ).html()){
		label = $( this ).html();
		value = $(label).text()
	}
  sendEventKeyValue(key, value);
  console.log("key : " + key);
  console.log("value : " + value);
  //speak(value);
});

function listen_slider() {
	console.log("start listen");
	if ($(slider).length>0){
		$(slider).each(function(index){
			console.log(index);
			slider_values[index] = $( this ).val();
		});

	    $(slider+input_select).change(function(event) {
	    	console.log($(this).attr('type'))
			var key = "slider";
			if ( ($(this).attr('type') == "number" || $(this).attr('type') == "text") && ($(this).prev("label").text()) ){
				key = $(this).prev("label").text();
			} else if ($(this).attr('class') == "ui-slider-switch" && !$( this ).attr('name') && !$( this ).attr('id')){
				key = "switch";
			} else if ($(this) == $("select") && !$( this ).attr('name') && !$( this ).attr('id')){
				key = "select";
			} else if ($( this ).attr('name')){
				key = $( this ).attr('name');
			} else if ($(this).attr('data-type')=="range" && $(this).parent("[data-role='fieldcontain']").attr('id')){
				key = $(this).parent("[data-role='fieldcontain']").attr('id');
			} else if ($( this ).attr('id')){
				key = $( this ).attr('id');
			}

			var value = "";
			if ($( this ).val()){
				value = $( this ).val();
			} else if ($( this ).attr('value')){
				value = $( this ).attr('value');
			} else if ($( this ).html()){
				label = $( this ).html();
				value = $(label).text()
			}
		  sendEventKeyValue(key, value);
		  slider_values[$(slider).index(this)] = value;
		  console.log("key : " + key);
		  console.log("value : " + value);
		});

		setInterval(function(){ 
			$(slider).each(function(index){
				if (slider_values[index] != $( this ).val()){
					$(this).change();
				}
			});
		}, 1000);
	}


}

 $(function() {
    $(this).bind("contextmenu", function(e) {
        e.preventDefault();
	});

	$.getScript("/www/bower_components/webui-popover/dist/jquery.webui-popover.min.js");
	$.getScript("/www/dist/js/jquery.qrcode.js");
	$.getScript("/www/dist/js/qrcode.js");

	$('body').append('<link rel="stylesheet" type="text/css" href="/www/bower_components/webui-popover/dist/jquery.webui-popover.css">');

	var buttonHtml = '  <div class="float" style="position: fixed; bottom: 12px; right: 25px;  z-index: 20;">\
	<div class="row top-buffer">\
	<span class="popover-wrapper">\
	<a id="qrcode-btn" href="javascript:;" data-role="popover" data-target="example-popover"><img src="/www/dist/icon/icon-qr.png"></a>\
	<div class="webui-popover-content">\
	<div id="qrcode-image"></div>\
	</div>\
	</span>\
	</div>\
	</div>';

	var viewHtml = '<meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">';

	$('body').append(buttonHtml);
	$('html').append(viewHtml);

	document.addEventListener('gesturestart', function (e) {
		e.preventDefault();
	});

	document.addEventListener('touchmove', function(event) {
        event = event.originalEvent || event;
        if (event.scale !== 1) {
           event.preventDefault();
        }
    }, false);

	setTimeout(function(){
		$('#qrcode-image').qrcode(window.location.href);
		$('#qrcode-btn').webuiPopover({width:284,height:265});
	},500)

});
  
setTimeout(listen_slider,750);