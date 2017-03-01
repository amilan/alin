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
    $('#chn1aout').on('change keypress', function(event) {
        sendCommand('aout',1, event);
    });            
    $('#chn2aout').on('change keypress', function(event) {
        sendCommand('aout',2, event);
    });            
    $('#chn3aout').on('change keypress', function(event) {
        sendCommand('aout',3, event);
    });            
    $('#chn4aout').on('change keypress', function(event) {
        sendCommand('aout',4, event);
    });        
    
    $('#dacgain').on('change keypress', function() {
        sendCommand('dacgain',1);
    });            
    
    
    $('#ioport1_config').on('change keypress', function() {
        sendCommand('ioportconfig',1);
    });            
    $('#ioport2_config').on('change keypress', function() {
        sendCommand('ioportconfig',2);
    });            
    $('#ioport3_config').on('change keypress', function() {
        sendCommand('ioportconfig',3);
    });            
    $('#ioport4_config').on('change keypress', function() {
        sendCommand('ioportconfig',4);
    });            
    
    $('#ioport1_value').on('change keypress', function() {
        sendCommand('ioportvalue',1);
    });            
    $('#ioport2_value').on('change keypress', function() {
        sendCommand('ioportvalue',2);
    });            
    $('#ioport3_value').on('change keypress', function() {
        sendCommand('ioportvalue',3);
    });            
    $('#ioport4_value').on('change keypress', function() {
        sendCommand('ioportvalue',4);
    });            
    
    $('#supplyport1').on('change keypress', function() {
        sendCommand('supplyport',1);
    });            
    $('#supplyport2').on('change keypress', function() {
        sendCommand('supplyport',2);
    });            
    $('#supplyport3').on('change keypress', function() {
        sendCommand('supplyport',3);
    });            
    $('#supplyport4').on('change keypress', function() {
        sendCommand('supplyport',4);
    });            
    
    updater.start();
});

function refreshData(allData) {
    if (first_time_refresh == false ) {    
        var elements = ["ioport1_config","ioport2_config","ioport3_config","ioport4_config"];
        var array = ["OUTPUT","INPUT"];
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
        
        var elements = ["ioport1_value","ioport2_value","ioport3_value","ioport4_value"];
        var array = ["Low","High"];
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
        
        document.getElementById("ioport1_config").value = allData.ioport_1_config;
        document.getElementById("ioport2_config").value = allData.ioport_2_config;
        document.getElementById("ioport3_config").value = allData.ioport_3_config;
        document.getElementById("ioport4_config").value = allData.ioport_4_config;
        document.getElementById("ioport1_value").value = allData.ioport_1_value;
        document.getElementById("ioport2_value").value = allData.ioport_2_value;
        document.getElementById("ioport3_value").value = allData.ioport_3_value;
        document.getElementById("ioport4_value").value = allData.ioport_4_value;
        
        document.getElementById("chn1aout").defaultValue = allData.chn1_aout;
        document.getElementById("chn2aout").defaultValue = allData.chn2_aout;
        document.getElementById("chn3aout").defaultValue = allData.chn3_aout;
        document.getElementById("chn4aout").defaultValue = allData.chn4_aout;
        
        var array = ["0 to 10V","-10 to 10V"];
        var valuearay = [0,1];
        var selectList = document.getElementById("dacgain");    
        for (var i = 0; i < array.length; i++) {
            var option = document.createElement("option");
            option.value = valuearay[i];
            option.text = array[i];
            option.innerHTML = array[i];
            selectList.add(option);
        }
        
        document.getElementById("dacgain").value = allData.dac_gain;
        
        if ( allData.ioport_1_config == "INPUT") {
            $("#ioport1_value").css("opacity", "0.2");
            document.getElementById('ioport1_value').disabled = true;       
        }
        else {
            $("#ioport1_value").css("opacity", "1");
            document.getElementById('ioport1_value').disabled = false;            
        }
        if ( allData.ioport_2_config == "INPUT") {
            $("#ioport2_value").css("opacity", "0.2");
            document.getElementById('ioport2_value').disabled = true;       
        }
        else {
            $("#ioport2_value").css("opacity", "1");
            document.getElementById('ioport2_value').disabled = false;            
        }
        if ( allData.ioport_3_config == "INPUT") {
            $("#ioport3_value").css("opacity", "0.2");
            document.getElementById('ioport3_value').disabled = true;       
        }
        else {
            $("#ioport3_value").css("opacity", "1");
            document.getElementById('ioport3_value').disabled = false;            
        }
        if ( allData.ioport_4_config == "INPUT") {
            $("#ioport4_value").css("opacity", "0.2");
            document.getElementById('ioport4_value').disabled = true;       
        }
        else {
            $("#ioport4_value").css("opacity", "1");
            document.getElementById('ioport4_value').disabled = false;            
        }        

        var elements = ["supplyport1","supplyport2","supplyport3","supplyport4"];
        var array = ["High Imp.","5V"];
        var valuearay = [0,1];
        for (var j = 0; j < elements.length; j++) {
            var selectList = document.getElementById(elements[j]);    
            for (var i = 0; i < array.length; i++) {
                var option = document.createElement("option");
                option.value = valuearay[i];
                option.text = array[i];
                option.innerHTML = array[i];
                selectList.add(option);
            }
        }        
        
        document.getElementById("supplyport1").value = allData.supplyport_1;
        document.getElementById("supplyport2").value = allData.supplyport_2;
        document.getElementById("supplyport3").value = allData.supplyport_3;
        document.getElementById("supplyport4").value = allData.supplyport_4;        
        
        first_time_refresh = true;        
    }
    
    if ("chn1_aout" in allData) { $("#chn1_aout").html(allData.chn1_aout); }
    if ("chn2_aout" in allData) { $("#chn2_aout").html(allData.chn2_aout); }
    if ("chn3_aout" in allData) { $("#chn3_aout").html(allData.chn3_aout); }
    if ("chn4_aout" in allData) { $("#chn4_aout").html(allData.chn4_aout); }
    if ("dac_gain" in allData) { 
        if (allData.dac_gain == 0) {
            $("#dac_gain").html("0 to 10 V"); 
        }
        else {
            $("#dac_gain").html("-10 to 10 V"); 
        }
    }    
    
    if ("ioport_1_name" in allData) { $("#ioport_1_name").html(allData.ioport_1_name); }    
    if ("ioport_2_name" in allData) { $("#ioport_2_name").html(allData.ioport_2_name); }    
    if ("ioport_3_name" in allData) { $("#ioport_3_name").html(allData.ioport_3_name); }    
    if ("ioport_4_name" in allData) { $("#ioport_4_name").html(allData.ioport_4_name); }    
    if ("ioport_1_config" in allData) { $("#ioport1config").html(allData.ioport_1_config); }    
    if ("ioport_2_config" in allData) { $("#ioport2config").html(allData.ioport_2_config); }    
    if ("ioport_3_config" in allData) { $("#ioport3config").html(allData.ioport_3_config); }    
    if ("ioport_4_config" in allData) { $("#ioport4config").html(allData.ioport_4_config); }    
    if ("ioport_1_value" in allData) { $("#ioport1value").html(allData.ioport_1_value); }    
    if ("ioport_2_value" in allData) { $("#ioport2value").html(allData.ioport_2_value); }    
    if ("ioport_3_value" in allData) { $("#ioport3value").html(allData.ioport_3_value); }    
    if ("ioport_4_value" in allData) { $("#ioport4value").html(allData.ioport_4_value); }    

    if ("ioport_1_config" in allData) {
        if ( allData.ioport_1_config == "INPUT") {
            $("#ioport1_value").css("opacity", "0.2");
            document.getElementById('ioport1_value').disabled = true;       
        }
        else {
            $("#ioport1_value").css("opacity", "1");
            document.getElementById('ioport1_value').disabled = false;            
        }
    }
    if ("ioport_2_config" in allData) {
        if ( allData.ioport_2_config == "INPUT") {
            $("#ioport2_value").css("opacity", "0.2");
            document.getElementById('ioport2_value').disabled = true;       
        }
        else {
            $("#ioport2_value").css("opacity", "1");
            document.getElementById('ioport2_value').disabled = false;            
        }
    }
    if ("ioport_3_config" in allData) {
        if ( allData.ioport_3_config == "INPUT") {
            $("#ioport3_value").css("opacity", "0.2");
            document.getElementById('ioport3_value').disabled = true;       
        }
        else {
            $("#ioport3_value").css("opacity", "1");
            document.getElementById('ioport3_value').disabled = false;            
        }
    }
    if ("ioport_4_config" in allData) {    
        if ( allData.ioport_4_config == "INPUT") {
            $("#ioport4_value").css("opacity", "0.2");
            document.getElementById('ioport4_value').disabled = true;       
        }
        else {
            $("#ioport4_value").css("opacity", "1");
            document.getElementById('ioport4_value').disabled = false;            
        }
    }
    
    if ("supplyport_1" in allData) {
        if (allData.supplyport_1 == 0) {
            $("#supplyport_1").html("High Imp."); 
        }
        else {
            $("#supplyport_1").html("5V"); 
        }
    }
    if ("supplyport_2" in allData) {
        if (allData.supplyport_2 == 0) {
            $("#supplyport_2").html("High Imp."); 
        }
        else {
            $("#supplyport_2").html("5V"); 
        }
    }
    if ("supplyport_3" in allData) {
        if (allData.supplyport_3 == 0) {
            $("#supplyport_3").html("High Imp."); 
        }
        else {
            $("#supplyport_3").html("5V"); 
        }
    }
    if ("supplyport_4" in allData) {
        if (allData.supplyport_4 == 0) {
            $("#supplyport_4").html("High Imp."); 
        }
        else {
            $("#supplyport_4").html("5V"); 
        }
    }
    
} 

function sendCommand(command, value, event ) {
    var data = {}
    var tmp_value;
    
    data['command'] = "";
    switch (command) {
        case 'ioportvalue':           
            if (value >=1 && value <= 4) {
                var el = "ioport"+value+"_value"
                tmp_value = document.getElementById(el).value;
                if (tmp_value == "High") { tmp_value = "1" } else { tmp_value = "0"} 
                data['command'] = "IOPO0"+value+":VALU " + tmp_value;
            }
            break;            
            
        case 'ioportconfig':           
            if (value >=1 && value <= 4) {
                var el = "ioport"+value+"_config"
                tmp_value = document.getElementById(el).value;
                if (tmp_value == "INPUT") { tmp_value = "1" } else { tmp_value = "0"} 
                data['command'] = "IOPO0"+value+":CONFI " + tmp_value;
            }
            break;     
    
        case 'aout':
            if ( event.which == 13 || event.keyCode == 13 ) {
                var el = "chn"+value+"aout"
                tmp_value = document.getElementById(el).value;
                data['command'] = "CHAN0"+value+":AOUT " + tmp_value;
            }
            else if (event.charCode >= 48 && event.charCode <= 57) {
                return;
            }                
            break;            
            
        case 'dacgain':           
            tmp_value = document.getElementById("dacgain").value;
            data['command'] = "ODAC:GAIN " + tmp_value;
            break;     
            
        case 'supplyport':           
            if (value >=1 && value <= 4) {
                var el = "supplyport"+value
                tmp_value = document.getElementById(el).value;
                data['command'] = "SUPP0"+value+":VALU " + tmp_value;
            }
            break;            
            
            supplyport
            
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