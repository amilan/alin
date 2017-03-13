/* DataMain.js
 * Electrometer data acquisition for web display
 * 1.0
 * 2016-09-28
 *
 * By Manuel Broseta, mbroseta@cells.es
 */

var acq_data1 = [];
var acq_data2 = [];
var acq_data3 = [];
var acq_data4 = [];

var password;
var pass1="12345";
var host = window.location.hostname;

var first_time_refresh = false;

password=prompt("Enter Password To view Page"," ");
if (password != pass1) 
{
    alert('Incorrect password!!!');
    window.close();
}

$( document ).ready(function() {
    $('#fvmaxlim').on('change focusout', function() {
        sendCommand('fvmaxlim',0);
    });    
    $('#fvminlim').on('change focusout', function() {
        sendCommand('fvminlim',0);
    });
    $('#fvrelay').on('change keypress focusout', function() {
        sendCommand('fvrealy',0);
    });
    $('#FVResetButton').on('click', function() {
        sendCommand('fvreset', 0);
    });    
    
    
    updater.start();
});

function refreshData(allData) {
    if (first_time_refresh == false ) {
        var elements = ["fvrelay"];
        var array = ["Off","On"];
        for (var j = 0; j < elements.length; j++) {
            var selectList = document.getElementById(elements[j]);    
            for (var i = 0; i < array.length; i++) {
                var option = document.createElement("option");
                option.value = array[i];
                option.text = array[i];
                option.innerHTML = array[i];
                selectList.add(option);
            }
        }

        document.getElementById("fvmaxlim").value = allData.fv_maxlim;        
        document.getElementById("fvminlim").value = allData.fv_minlim;        
        
        first_time_refresh = true;                
    }
    
    if ("fv_maxlim" in allData) { $("#fv_maxlim").html(allData.fv_maxlim); }
    if ("fv_minlim" in allData) { $("#fv_minlim").html(allData.fv_minlim); }
    
    if ("fv_relay" in allData) { 
        $("#fv_relay").html(allData.fv_relay);
        if (allData.fv_relay == "On") {
            $("#fv_relay").css("background-color", "#00FF00");
            $("#fv_relay").css("color", "black");                                        
        }
        else {
            $("#fv_relay").css("background-color", "#FF0000");
            $("#fv_relay").css("color", "white");                    
        }
    }
} 

function sendCommand(command, value, event ) {
    var data = {}
    var tmp_value;
    
    data['command'] = "";
    switch (command) {
        case 'fvmaxlim':
            tmp_value = parseInt(document.getElementById("fvmaxlim").value);
            data['command'] = "FVCT:MAXL " + tmp_value
            break;
            
        case 'fvminlim':
            tmp_value = parseInt(document.getElementById("fvminlim").value);
            data['command'] = "FVCT:MINL " + tmp_value
            break;
            
        case 'fvrealy':    
            tmp_value = document.getElementById("fvrelay").value;
            if (tmp_value == "On") { tmp_value = "1" } else { tmp_value = "0"} 
            data['command'] = "FVCT:RELA " + tmp_value;
            break;            

        case 'fvreset':
            data['command'] = "FVCT:RESE 1"
            break;
            
            
        default:
            return;
    }
    
    if (data['command'] != "" ) {
        console.log(data['command']);
        updater.socket.send(JSON.stringify(data));
        
        $("#Message").html("** Processing data **");
        setTimeout("clearMessage();",2000);
    }
};

function clearMessage() {
    $("#Message").html("");
}   


var updater = {
    socket: null,
    
    start: function() {
        var url = "ws://" + location.host + "/electrometer";
        updater.socket = new WebSocket(url);
        updater.socket.onmessage = function(event) {
            updater.showMessage(JSON.parse(event.data));
        }
    },
    
    showMessage: function(jsondata) {
        refreshData(jsondata)
    }
};