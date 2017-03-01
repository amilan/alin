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

var tmode_array = [["SOFTWARE",0],["HARDWARE",1]];
var tpol_array = [["FALLING",0],["RISING",1]];
var input_array = [["DIO_1", 0], ["DIO_2", 1], ["DIO_3", 2], ["DIO_4", 3], ["DIFF_IO_1", 4], ["DIFF_IO_2", 5], ["DIFF_IO_3", 6],["DIFF_IO_4", 7],["DIFF_IO_5", 8],["DIFF_IO_6", 9],["DIFF_IO_7", 10],["DIFF_IO_8", 11],["DIFF_IO_9", 12]]

password=prompt("Enter Password To view Page"," ");
if (password != pass1) 
{
    alert('Incorrect password!!!');
    window.close();
}

$( document ).ready(function() {
    $('#chn1_cafilter').on('change keypress', function() {
        sendCommand('filter',1);
    });    
    $('#chn2_cafilter').on('change keypress', function() {
        sendCommand('filter',2);
    });
    $('#chn3_cafilter').on('change keypress', function() {
        sendCommand('filter',3);
    });
    $('#chn4_cafilter').on('change keypress', function() {
        sendCommand('filter',4);
    });

    $('#chn1_caPrefilter').on('change keypress', function() {
        sendCommand('prefilter',1);
    });        
    $('#chn2_caPrefilter').on('change keypress', function() {
        sendCommand('prefilter',2);
    });        
    $('#chn3_caPrefilter').on('change keypress', function() {
        sendCommand('prefilter',3);
    });        
    $('#chn4_caPrefilter').on('change keypress', function() {
        sendCommand('prefilter',4);
    });   
    
    
    $('#chn1_caPostfilter').on('change keypress', function() {
        sendCommand('postfilter',1);
    });        
    $('#chn2_caPostfilter').on('change keypress', function() {
        sendCommand('postfilter',2);
    });        
    $('#chn3_caPostfilter').on('change keypress', function() {
        sendCommand('postfilter',3);
    });        
    $('#chn4_caPostfilter').on('change keypress', function() {
        sendCommand('postfilter',4);
    });  
    
    $('#chn1_carange').on('change keypress', function() {
        sendCommand('range',1);
    });        
    $('#chn2_carange').on('change keypress', function() {
        sendCommand('range',2);
    });        
    $('#chn3_carange').on('change keypress', function() {
        sendCommand('range',3);
    });        
    $('#chn4_carange').on('change keypress', function() {
        sendCommand('range',4);
    });        
    
    $('#chn1_catigain').on('change keypress', function() {
        sendCommand('tigain',1);
    });        
    $('#chn2_catigain').on('change keypress', function() {
        sendCommand('tigain',2);
    });        
    $('#chn3_catigain').on('change keypress', function() {
        sendCommand('tigain',3);
    });        
    $('#chn4_catigain').on('change keypress', function() {
        sendCommand('tigain',4);
    });        
    
    $('#chn1_cavgain').on('change keypress', function() {
        sendCommand('vgain',1);
    });        
    $('#chn2_cavgain').on('change keypress', function() {
        sendCommand('vgain',2);
    });        
    $('#chn3_cavgain').on('change keypress', function() {
        sendCommand('vgain',3);
    });        
    $('#chn4_cavgain').on('change keypress', function() {
        sendCommand('vgain',4);
    });      
    
    $('#chn1_cainv').on('change keypress', function() {
        sendCommand('inversion',1);
    });            
    $('#chn2_cainv').on('change keypress', function() {
        sendCommand('inversion',2);
    });            
    $('#chn3_cainv').on('change keypress', function() {
        sendCommand('inversion',3);
    });            
    $('#chn4_cainv').on('change keypress', function() {
        sendCommand('inversion',4);
    });            
        
    $('#chn1_satmax').on('change keypress', function(event) {
        sendCommand('satmax', 1, event);
    });        
    
    $('#chn2_satmax').on('change keypress', function(event) {
        sendCommand('satmax', 2, event);
    });        
    
    $('#chn3_satmax').on('change keypress', function(event) {
        sendCommand('satmax', 3, event);
    });        
    
    $('#chn4_satmax').on('change keypress', function(event) {
        sendCommand('satmax', 4, event);
    });            
    
    $('#chn1_satmin').on('change keypress', function(event) {
        sendCommand('satmin', 1, event);
    });        
    
    $('#chn2_satmin').on('change keypress', function(event) {
        sendCommand('satmin', 2, event);
    });        
    
    $('#chn3_satmin').on('change keypress', function(event) {
        sendCommand('satmin', 3, event);
    });        
    
    $('#chn4_satmin').on('change keypress', function(event) {
        sendCommand('satmin', 4, event);
    });            
    
    $('#chn1_offset').on('change keypress', function(event) {
        sendCommand('offset', 1, event);
    });        
    
    $('#chn2_offset').on('change keypress', function(event) {
        sendCommand('offset', 2, event);
    });        

    $('#chn3_offset').on('change keypress', function(event) {
        sendCommand('offset', 3, event);
    });        
    
    $('#chn4_offset').on('change keypress', function(event) {
        sendCommand('offset', 4, event);
    });        
    
    $('#swtrigButton').on('click', function() {
        sendCommand('swtrig', 0);
    });    
    
    $('#trigMode').on('change keypress', function() {
        sendCommand('trigMode', 0);
    });    
    
    $('#trigDelay').on('change keypress', function(event) {
        sendCommand('trigDelay', 0, event);
    });    

    $('#trigInput').on('change keypress', function() {
        sendCommand('trigInput', 0);
    });    
    
    $('#trigPol').on('change keypress', function() {
        sendCommand('trigPol', 0);
    });  
    
    $('#acqRange').on('change keypress', function() {
        sendCommand('range', 0);
    });  
    
    $('#acqFilter').on('change keypress', function() {
        sendCommand('filter', 0);
    }); 
    
    $('#acqTime').on('change keypress', function(event) {
        sendCommand('acqTime', 0, event);
    });
    
    $('#acqStartButton').on('click', function() {
        sendCommand('startAcq',0);
    });

    $('#acqStopButton').on('click', function() {
        sendCommand('stopAcq',0);
    });
    
    updater.start();
});

function refreshData(allData) {
    if (first_time_refresh == false ) {
        var elements = ["chn1_cafilter","chn2_cafilter","chn3_cafilter","chn4_cafilter","acqFilter"];
        var array = ["3200Hz","100Hz","10Hz","1Hz","0.5Hz"];
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
        
        var elements = ["chn1_caPostfilter","chn2_caPostfilter","chn3_caPostfilter","chn4_caPostfilter"];
        var array = ["3200Hz","100Hz","10Hz","1Hz"];
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
        
        var elements = ["chn1_caPrefilter","chn2_caPrefilter","chn3_caPrefilter","chn4_caPrefilter"];
        var array = ["3500Hz","100Hz","10Hz","1Hz","0.5Hz"];
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
        
        var elements = ["chn1_carange","chn2_carange","chn3_carange","chn4_carange","acqRange"];
        var array = ["AUTO","1mA","100uA","10uA","1uA","100nA","10nA","1nA","100pA"];
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
        
        var elements = ["chn1_catigain","chn2_catigain","chn3_catigain","chn4_catigain"];
        var array = ["10k","1M","100M","1G","10G"];
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
        
        var elements = ["chn1_cavgain","chn2_cavgain","chn3_cavgain","chn4_cavgain"];
        var array = ["1","10","50","100"];
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
        
        var elements = ["chn1_cainv","chn2_cainv","chn3_cainv","chn4_cainv"];
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
        
        var selectList = document.getElementById("trigInput");    
        for (var i = 0; i < input_array.length; i++) {
            var option = document.createElement("option");
            option.value = input_array[i][1];
            option.text = input_array[i][0];
            option.innerHTML = input_array[i][0];
            selectList.add(option);
        }    
        
        var selectList = document.getElementById("trigMode");    
        for (var i = 0; i < tmode_array.length; i++) {
            var option = document.createElement("option");
            option.value = tmode_array[i][1];
            option.text = tmode_array[i][0];
            option.innerHTML = tmode_array[i][0];
            selectList.add(option);
        }
        
        var selectList = document.getElementById("trigPol");    
        for (var i = 0; i < tpol_array.length; i++) {
            var option = document.createElement("option");
            option.value = tpol_array[i][1];
            option.text = tpol_array[i][0];
            option.innerHTML = tpol_array[i][0];
            selectList.add(option);
        }        

        document.getElementById("chn1_cafilter").value = allData.chn1_cafilter;        
        document.getElementById("chn2_cafilter").value = allData.chn2_cafilter;        
        document.getElementById("chn3_cafilter").value = allData.chn3_cafilter;        
        document.getElementById("chn4_cafilter").value = allData.chn4_cafilter;        
        document.getElementById("chn1_caPostfilter").value = allData.chn1_capostfilter;        
        document.getElementById("chn2_caPostfilter").value = allData.chn2_capostfilter;        
        document.getElementById("chn3_caPostfilter").value = allData.chn3_capostfilter;        
        document.getElementById("chn4_caPostfilter").value = allData.chn4_capostfilter;        
        document.getElementById("chn1_caPrefilter").value = allData.chn1_caprefilter;        
        document.getElementById("chn2_caPrefilter").value = allData.chn2_caprefilter;        
        document.getElementById("chn3_caPrefilter").value = allData.chn3_caprefilter;        
        document.getElementById("chn4_caPrefilter").value = allData.chn4_caprefilter;        
        
        document.getElementById("chn1_carange").value = allData.chn1_carange;
        document.getElementById("chn2_carange").value = allData.chn2_carange;        
        document.getElementById("chn3_carange").value = allData.chn3_carange;
        document.getElementById("chn4_carange").value = allData.chn4_carange;   
        document.getElementById("chn1_catigain").value = allData.chn1_catigain;
        document.getElementById("chn2_catigain").value = allData.chn2_catigain;        
        document.getElementById("chn3_catigain").value = allData.chn3_catigain;
        document.getElementById("chn4_catigain").value = allData.chn4_catigain;   
        document.getElementById("chn1_cavgain").value = allData.chn1_cavgain;
        document.getElementById("chn2_cavgain").value = allData.chn2_cavgain;        
        document.getElementById("chn3_cavgain").value = allData.chn3_cavgain;
        document.getElementById("chn4_cavgain").value = allData.chn4_cavgain;   
        
        document.getElementById("chn1_cainv").value = allData.chn1_cainv;
        document.getElementById("chn2_cainv").value = allData.chn2_cainv;
        document.getElementById("chn3_cainv").value = allData.chn3_cainv;
        document.getElementById("chn4_cainv").value = allData.chn4_cainv;            

        document.getElementById("chn1_satmax").defaultValue = parseInt(allData.chn1_satmax);
        document.getElementById("chn2_satmax").defaultValue = parseInt(allData.chn2_satmax);
        document.getElementById("chn3_satmax").defaultValue = parseInt(allData.chn3_satmax);
        document.getElementById("chn4_satmax").defaultValue = parseInt(allData.chn4_satmax);
        document.getElementById("chn1_satmin").defaultValue = parseInt(allData.chn1_satmin);
        document.getElementById("chn2_satmin").defaultValue = parseInt(allData.chn2_satmin);
        document.getElementById("chn3_satmin").defaultValue = parseInt(allData.chn3_satmin);
        document.getElementById("chn4_satmin").defaultValue = parseInt(allData.chn4_satmin);
                
        document.getElementById("chn1_offset").defaultValue = parseInt(allData.chn1_offset);
        document.getElementById("chn2_offset").defaultValue = parseInt(allData.chn2_offset);
        document.getElementById("chn3_offset").defaultValue = parseInt(allData.chn3_offset);
        document.getElementById("chn4_offset").defaultValue = parseInt(allData.chn4_offset);
        
        for (var i = 0; i < tmode_array.length; i++) {
            if (tmode_array[i][0] == allData.acq_trig_mode ) {
                document.getElementById("trigMode").value = tmode_array[i][1];        
            }
        }                
        for (var i = 0; i < tpol_array.length; i++) {
            if (tpol_array[i][0] == allData.acq_trig_pol ) {
                document.getElementById("trigPol").value = tpol_array[i][1];        
            }
        }        
        for (var i = 0; i < input_array.length; i++) {
            if (input_array[i][0] == allData.acq_trig_input ) {
                document.getElementById("trigInput").value = input_array[i][1];        
            }
        }
        
        document.getElementById("trigDelay").defaultValue = allData.acq_trig_delay;        
        document.getElementById("acqRange").value = allData.acq_range;
        document.getElementById("acqFilter").value = allData.acq_filter;        
        document.getElementById("acqTime").defaultValue = allData.acq_time; 

        first_time_refresh = true;        
    }
    
    if ("chn1_cafilter" in allData) { $("#chn1cafilter").html(allData.chn1_cafilter); }
    if ("chn2_cafilter" in allData) { $("#chn2cafilter").html(allData.chn2_cafilter); }
    if ("chn3_cafilter" in allData) { $("#chn3cafilter").html(allData.chn3_cafilter); }
    if ("chn4_cafilter" in allData) { $("#chn4cafilter").html(allData.chn4_cafilter); }
    if ("chn1_caprefilter" in allData) { $("#chn1caPrefilter").html(allData.chn1_caprefilter); }
    if ("chn2_caprefilter" in allData) { $("#chn2caPrefilter").html(allData.chn2_caprefilter); }
    if ("chn3_caprefilter" in allData) { $("#chn3caPrefilter").html(allData.chn3_caprefilter); }
    if ("chn4_caprefilter" in allData) { $("#chn4caPrefilter").html(allData.chn4_caprefilter); }    
    if ("chn1_capostfilter" in allData) { $("#chn1caPostfilter").html(allData.chn1_capostfilter); }    
    if ("chn2_capostfilter" in allData) { $("#chn2caPostfilter").html(allData.chn2_capostfilter); }    
    if ("chn3_capostfilter" in allData) { $("#chn3caPostfilter").html(allData.chn3_capostfilter); }    
    if ("chn4_capostfilter" in allData) { $("#chn4caPostfilter").html(allData.chn4_capostfilter); }        
    if ("chn1_carange" in allData) { $("#chn1carange").html(allData.chn1_carange); }
    if ("chn2_carange" in allData) { $("#chn2carange").html(allData.chn2_carange); }
    if ("chn3_carange" in allData) { $("#chn3carange").html(allData.chn3_carange); }
    if ("chn4_carange" in allData) { $("#chn4carange").html(allData.chn4_carange); }
    if ("chn1_catigain" in allData) { $("#chn1catigain").html(allData.chn1_catigain); }
    if ("chn2_catigain" in allData) { $("#chn2catigain").html(allData.chn2_catigain); }
    if ("chn3_catigain" in allData) { $("#chn3catigain").html(allData.chn3_catigain); }
    if ("chn4_catigain" in allData) { $("#chn4catigain").html(allData.chn4_catigain); }
    if ("chn1_cavgain" in allData) { $("#chn1cavgain").html(allData.chn1_cavgain); }
    if ("chn2_cavgain" in allData) { $("#chn2cavgain").html(allData.chn2_cavgain); }
    if ("chn3_cavgain" in allData) { $("#chn3cavgain").html(allData.chn3_cavgain); }
    if ("chn4_cavgain" in allData) { $("#chn4cavgain").html(allData.chn4_cavgain); }
    if ("chn1_satmax" in allData) { $("#chn1satmax").html(allData.chn1_satmax); }
    if ("chn2_satmax" in allData) { $("#chn2satmax").html(allData.chn2_satmax); }
    if ("chn3_satmax" in allData) { $("#chn3satmax").html(allData.chn3_satmax); }
    if ("chn4_satmax" in allData) { $("#chn4satmax").html(allData.chn4_satmax); }    
    if ("chn1_satmin" in allData) { $("#chn1satmin").html(allData.chn1_satmin); }
    if ("chn2_satmin" in allData) { $("#chn2satmin").html(allData.chn2_satmin); }
    if ("chn3_satmin" in allData) { $("#chn3satmin").html(allData.chn3_satmin); }
    if ("chn4_satmin" in allData) { $("#chn4satmin").html(allData.chn4_satmin); }    
    if ("chn1_offset" in allData) { $("#chn1offset").html(allData.chn1_offset); }
    if ("chn2_offset" in allData) { $("#chn2offset").html(allData.chn2_offset); }
    if ("chn3_offset" in allData) { $("#chn3offset").html(allData.chn3_offset); }
    if ("chn4_offset" in allData) { $("#chn4offset").html(allData.chn4_offset); }    

    if ("acq_trig_mode" in allData) {$("#acq_trig_mode").html(allData.acq_trig_mode); }
    if ("acq_trig_pol" in allData) {$("#acq_trig_pol").html(allData.acq_trig_pol); }
    if ("acq_trig_delay" in allData) {$("#acq_trig_delay").html(allData.acq_trig_delay); }
    if ("acq_trig_input" in allData) {$("#acq_trig_input").html(allData.acq_trig_input); }
    if ("acq_time" in allData) {$("#acq_time").html(allData.acq_time); }
    if ("acq_range" in allData) {$("#acq_range").html(allData.acq_range); }
    if ("acq_filter" in allData) {$("#acq_filter").html(allData.acq_filter); }
    if ("acq_state" in allData) {$("#acq_state").html(allData.acq_state); }

    if ("chn1_cainv" in allData) {$("#chn1cainv").html(allData.chn1_cainv); }
    if ("chn2_cainv" in allData) {$("#chn2cainv").html(allData.chn2_cainv); }
    if ("chn3_cainv" in allData) {$("#chn3cainv").html(allData.chn3_cainv); }
    if ("chn4_cainv" in allData) {$("#chn4cainv").html(allData.chn4_cainv); }

    if ("fv_maxlim" in allData) { $("#fv_maxlim").html(allData.fv_maxlim); }
    if ("fv_minlim" in allData) { $("#fv_minlim").html(allData.fv_minlim); }
    
    if ("fv_relay" in allData) { 
        if (allData.fv_relay == "1") {
            $("#fv_relay").html("On");
            $("#fv_relay").css("background-color", "#00FF00");
            $("#fv_relay").css("color", "black");                                        
        }
        else {
            $("#fv_relay").html("Off");
            $("#fv_relay").css("background-color", "#FF0000");
            $("#fv_relay").css("color", "white");                    
        }
    }
    
    checkAcquisition();
    
    checkChannelRange();
    
    try {
        checkSettingValues();
    }
    catch (err) {
        console.log("checkSettingValues() Error");
    } 
} 

function checkAcquisition() {
    var elsToCtrl = ['trigMode', 'trigDelay', 'trigInput', 'trigPol', 'acqRange', 'acqFilter', 'acqTime', 'chn1_cafilter', 'chn2_cafilter', 'chn3_cafilter', 'chn4_cafilter', 'chn1_caPostfilter', 'chn2_caPostfilter', 'chn3_caPostfilter', 'chn4_caPostfilter', 'chn1_caPrefilter', 'chn2_caPrefilter', 'chn3_caPrefilter', 'chn4_caPrefilter', 'chn1_carange', 'chn2_carange', 'chn3_carange', 'chn4_carange', 'chn1_catigain', 'chn2_catigain', 'chn3_catigain', 'chn4_catigain', 'chn1_cavgain', 'chn2_cavgain', 'chn3_cavgain', 'chn4_cavgain', 'chn1_cainv', 'chn2_cainv', 'chn3_cainv', 'chn4_cainv','chn1_offset','chn2_offset','chn3_offset','chn4_offset', 'chn1_satmax', 'chn2_satmax', 'chn3_satmax', 'chn4_satmax', 'chn1_satmin', 'chn2_satmin', 'chn3_satmin', 'chn4_satmin'];
    
    console.log("CHECK ACQUISITION = " + document.getElementById('acq_state').innerHTML);
    
    if (document.getElementById('acq_state').innerHTML == "ACQUIRING") {
        $("#acq_state").css("background-color", "#00FFFF");
        $("#acq_state").css("color", "black");
        document.getElementById("acqStartButton").style.display = "none";    
        document.getElementById("acqStopButton").style.display = "inline";                
        
        for (var i = 0; i < elsToCtrl.length; i++) {
            $("#"+elsToCtrl[i]).css("opacity", "0.2");
            document.getElementById(elsToCtrl[i]).disabled = true;            
        }
        
        if (document.getElementById("acq_trig_mode").innerHTML == "SOFTWARE") {
            document.getElementById("swtrigButton").disabled = false; 
        }            
    }
    else {
        $("#acq_state").css("background-color", "#FF0000");
        $("#acq_state").css("color", "white");                    
        document.getElementById("acqStartButton").style.display = "inline";    
        document.getElementById("acqStopButton").style.display = "none";                
        document.getElementById("swtrigButton").disabled = true;
        
        for (var i = 0; i < elsToCtrl.length; i++) {
            $("#"+elsToCtrl[i]).css("opacity", "1");
            document.getElementById(elsToCtrl[i]).disabled = false;            
        }
    }              
}

function checkChannelRange() {
    var elsToCtrl = {'chn1carange': ['chn1_catigain','chn1_cavgain'],
                    'chn2carange': ['chn2_catigain', 'chn2_cavgain'],
                    'chn3carange': ['chn3_catigain', 'chn3_cavgain'],
                    'chn4carange': ['chn4_catigain', 'chn4_cavgain'],
                    };
    
    var keys = Object.keys(elsToCtrl);
    
    for (var j = 0; j < keys.length; j++) {
        console.log("CHECK Channel Range" + document.getElementById(keys[j]).innerHTML);
        
        if (document.getElementById(keys[j]).innerHTML == "AUTO") {
            for (var i = 0; i < elsToCtrl[keys[j]].length; i++) {
                $("#"+elsToCtrl[keys[j]][i]).css("opacity", "0.2");
                document.getElementById(elsToCtrl[keys[j]][i]).disabled = true;            
            }
        }
        else {
            for (var i = 0; i < elsToCtrl.length; i++) {
                $("#"+elsToCtrl[keys[j]][i]).css("opacity", "1");
                document.getElementById(elsToCtrl[keys[j]][i]).disabled = false;            
            }
        }
    }
}


function checkSettingValues() {
    var alertmsg_flag = false;
    
    /* range_vals: tigain, vgain */
    var range_vals = { '1mA': ['10k','1'], '100uA': ['10k', '10'], '10uA': ['1M', '1'], '1uA': ['1M', '10'],'100nA': ['100M', '1'], '10nA': ['1G', '1'], '1nA': ['10G', '1'], '100pA': ['10G', '10']};
    var range_els = { 'chn1carange': ['chn1catigain',  'chn1cavgain'], 'chn2carange': ['chn2catigain', 'chn2cavgain'], 'chn3carange': ['chn3catigain', 'chn3cavgain'], 'chn4carange': ['chn4catigain', 'chn4cavgain' ]};
    var tmp, tmp1, tmp2;
    var keys = [];
    
    for (var key in range_els) {
        tmp = document.getElementById(key).innerHTML;
        tmp1 = document.getElementById(range_els[key][0]).innerHTML;
        tmp2 = document.getElementById(range_els[key][1]).innerHTML;
        
        var idx_val = "AUTO";
        for (var idx in range_vals) {
            if ( tmp.includes(idx) ) {
                idx_val = idx;
                break;
            }
        }
        
        if ((typeof range_vals[idx_val] != 'undefined') && idx_val != 'AUTO' && (range_vals[idx_val][0] != tmp1 || range_vals[idx_val][1] != tmp2 )) {
            alertmsg_flag = true;
            $("#"+key).html(idx_val+"*");            
            $("#"+key).css("color", "red");
        }
        else {
            $("#"+key).html(idx_val);            
            $("#"+key).css("color", "#ccb95c"); 
        }
    }
    
    /* filter_vals: postfilter, prefilter */
    var filter_vals = {'3200Hz': ['3200Hz', '3500Hz'], '100Hz': ['100Hz', '100Hz'], '10Hz': ['10Hz', '10Hz'], '1Hz': ['1Hz', '1Hz'], '0.5Hz': ['1Hz', '0.5Hz']};
    var filter_els = { 'chn1cafilter': ['chn1caPostfilter', 'chn1caPrefilter'], 'chn2cafilter': ['chn2caPostfilter', 'chn2caPrefilter'], 'chn3cafilter': ['chn3caPostfilter', 'chn3caPrefilter'],'chn4cafilter': ['chn4caPostfilter', 'chn4caPrefilter']};
    var keys = [];
    for (var key in filter_els) {
        tmp = document.getElementById(key).innerHTML;
        tmp1 = document.getElementById(filter_els[key][0]).innerHTML;
        tmp2 = document.getElementById(filter_els[key][1]).innerHTML;
        
        var idx_val = "undefined";
        for (var idx in filter_vals) {
            if ( tmp.includes(idx) ) {
                idx_val = idx;
                break;
            }
        }
        
        if ((typeof filter_vals[idx_val] != 'undefined') && (filter_vals[idx_val][0] != tmp1 || filter_vals[idx_val][1] != tmp2 )) {
            alertmsg_flag = true;
            tmp = document.getElementById(key).innerHTML;
            $("#"+key).html(idx_val+"*");
            $("#"+key).css("color", "red");            
        }
        else {
            $("#"+key).html(idx_val);
            $("#"+key).css("color", "#ccb95c"); 
        }
    }
    
    if ( alertmsg_flag == false ) {
        $("#alertmsg").html("&nbsp");
    }    
    else {
        $("#alertmsg").html("*Applied setting may differ from the real setting!!");
    }
}

function sendCommand(command, value, event ) {
    var data = {}
    var tmp_value;
    
    data['command'] = "";
    switch (command) {
        case 'filter':
            if (value >=1 && value <= 4) {
                var el = "chn"+value+"_cafilter"
                tmp_value = document.getElementById(el).value;
                data['command'] = "CHAN0"+value+":CABO:FILTER " + tmp_value;
            }
            else if (value == 0 )
            {
                tmp_value = document.getElementById("acqFilter").value;
                data['command'] = "ACQU:FILTER " + tmp_value;
            }
            break;

        case 'prefilter':
            if (value >=1 && value <= 4) {
                var el = "chn"+value+"_caPrefilter"
                tmp_value = document.getElementById(el).value;
                data['command'] = "CHAN0"+value+":CABO:PREFILTER " + tmp_value;
            }
            break;

        case 'postfilter':
            if (value >=1 && value <= 4) {
                var el = "chn"+value+"_caPostfilter"
                tmp_value = document.getElementById(el).value;
                data['command'] = "CHAN0"+value+":CABO:POSTFILTER " + tmp_value;
            }
            break;            
            
        case 'range':
            if (value >=1 && value <= 4) {
                var el = "chn"+value+"_carange"
                tmp_value = document.getElementById(el).value;
                data['command'] = "CHAN0"+value+":CABO:RANGE " + tmp_value;
            }
            else if (value == 0 )
            {
                tmp_value = document.getElementById("acqRange").value;
                data['command'] = "ACQU:RANGE " + tmp_value;
            }
            break;
            
        case 'tigain':
            if (value >=1 && value <= 4) {
                var el = "chn"+value+"_catigain"
                tmp_value = document.getElementById(el).value;
                data['command'] = "CHAN0"+value+":CABO:TIGAIN " + tmp_value;
            }
            break;
            
        case 'vgain':
            if (value >=1 && value <= 4) {
                var el = "chn"+value+"_cavgain"
                tmp_value = document.getElementById(el).value;
                data['command'] = "CHAN0"+value+":CABO:VGAIN " + tmp_value;
            }
            break;            
            
        case 'inversion':    
            if (value >=1 && value <= 4) {
                var el = "chn"+value+"_cainv"
                tmp_value = document.getElementById(el).value;
                if (tmp_value == "On") { tmp_value = "1" } else { tmp_value = "0"} 
                data['command'] = "CHAN0"+value+":CABO:INVE " + tmp_value;
            }
            break;
            
        case 'offset':
            if ( event.which == 13 || event.keyCode == 13 ) {
                var el = "chn"+value+"_offset"
                tmp_value = document.getElementById(el).value;
                if ( parseFloat(tmp_value) < 0 ) {
                    return;
                }
                data['command'] = "CHAN0"+value+":CABO:OFFS " + tmp_value;
            }
            else if (event.charCode >= 48 && event.charCode <= 57) {
                return;
            }                
            break;
            
        case 'swtrig':
            data['command'] = "TRIG:SWSE 1"
            break;
            
        case 'trigMode':
            tmp_value = document.getElementById("trigMode").value;
            data['command'] = "TRIG:MODE " + tmp_value
            break;
            
        case 'trigDelay':
            if ( event.which == 13 || event.keyCode == 13 ) {
                tmp_value = document.getElementById("trigDelay").value;
                if ( parseFloat(tmp_value) < 0 ) {
                    return;
                }
                data['command'] = "TRIG:DELAY " + tmp_value
            }
            else if (event.charCode >= 48 && event.charCode <= 57) {
                return;
            }                
            break;
            
        case 'trigInput':
            tmp_value = document.getElementById("trigInput").value;
            data['command'] = "TRIG:INPUT " + tmp_value
            break;
            
        case 'trigPol':
            tmp_value = document.getElementById("trigPol").value;
            data['command'] = "TRIG:POLA " + tmp_value
            break;            
            
        case 'acqTime':
            if ( event.which == 13 || event.keyCode == 13 ) {
                tmp_value = document.getElementById("acqTime").value;
                if ( parseFloat(tmp_value) < 1 ) {
                    return;
                }                
                data['command'] = "ACQU:TIME " + tmp_value
            }
            else if (event.charCode >= 48 && event.charCode <= 57) {
                return;
            }                
            break;
            
        case 'startAcq':
            data['command'] = "ACQU:START 1"
            break;

        case 'stopAcq':
            data['command'] = "ACQU:STOP 1"
            break;
            
        case 'satmax':
            if ( event.which == 13 || event.keyCode == 13 ) {
                var el = "chn"+value+"_satmax"
                tmp_value = document.getElementById(el).value;
                if ( parseFloat(tmp_value) < 0 ) {
                    return;
                }
                data['command'] = "CHAN0"+value+":CABO:SMAX " + tmp_value;
            }
            else if (event.charCode >= 48 && event.charCode <= 57) {
                return;
            }                
            break;
            
        case 'satmin':
            if ( event.which == 13 || event.keyCode == 13 ) {
                var el = "chn"+value+"_satmin"
                tmp_value = document.getElementById(el).value;
                if ( parseFloat(tmp_value) < 0 ) {
                    return;
                }
                data['command'] = "CHAN0"+value+":CABO:SMIN " + tmp_value;
            }
            else if (event.charCode >= 48 && event.charCode <= 57) {
                return;
            }                
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