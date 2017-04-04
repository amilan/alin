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
    $('#chn1_cafilter').on('change keypress focusout', function(event) {
        sendCommand('chn1_cafilter', event);
    });       

    $('#chn2_cafilter').on('change keypress focusout', function(event) {
        sendCommand('chn2_cafilter', event);
    }); 
    
    $('#chn3_cafilter').on('change keypress focusout', function(event) {
        sendCommand('chn3_cafilter', event);
    }); 
    
    $('#chn4_cafilter').on('change keypress focusout', function(event) {
        sendCommand('chn4_cafilter', event);
    }); 
    
    $('#chn1_caPrefilter').on('change keypress focusout', function(event) {
        sendCommand('chn1_caPrefilter', event);
    });       
    
    $('#chn2_caPrefilter').on('change keypress focusout', function(event) {
        sendCommand('chn2_caPrefilter', event);
    }); 
    
    $('#chn3_caPrefilter').on('change keypress focusout', function(event) {
        sendCommand('chn3_caPrefilter', event);
    }); 
    
    $('#chn4_caPrefilter').on('change keypress focusout', function(event) {
        sendCommand('chn4_caPrefilter', event);
    }); 
    
    $('#chn1_caPostfilter').on('change keypress focusout', function(event) {
        sendCommand('chn1_caPostfilter', event);
    });       
    
    $('#chn2_caPostfilter').on('change keypress focusout', function(event) {
        sendCommand('chn2_caPostfilter', event);
    }); 
    
    $('#chn3_caPostfilter').on('change keypress focusout', function(event) {
        sendCommand('chn3_caPostfilter', event);
    }); 
    
    $('#chn4_caPostfilter').on('change keypress focusout', function(event) {
        sendCommand('chn4_caPostfilter', event);
    }); 

    $('#chn1_carange').on('change keypress focusout', function(event) {
        sendCommand('chn1_carange', event);
    });       
    
    $('#chn2_carange').on('change keypress focusout', function(event) {
        sendCommand('chn2_carange', event);
    }); 
    
    $('#chn3_carange').on('change keypress focusout', function(event) {
        sendCommand('chn3_carange', event);
    }); 
    
    $('#chn4_carange').on('change keypress focusout', function(event) {
        sendCommand('chn4_carange', event);
    });  
    
    $('#chn1_catigain').on('change keypress focusout', function(event) {
        sendCommand('chn1_catigain', event);
    });       
    
    $('#chn2_catigain').on('change keypress focusout', function(event) {
        sendCommand('chn2_catigain', event);
    }); 
    
    $('#chn3_catigain').on('change keypress focusout', function(event) {
        sendCommand('chn3_catigain', event);
    }); 
    
    $('#chn4_catigain').on('change keypress focusout', function(event) {
        sendCommand('chn4_catigain', event);
    });         
    
    $('#chn1_cavgain').on('change keypress focusout', function(event) {
        sendCommand('chn1_cavgain', event);
    });       
    
    $('#chn2_cavgain').on('change keypress focusout', function(event) {
        sendCommand('chn2_cavgain', event);
    }); 
    
    $('#chn3_cavgain').on('change keypress focusout', function(event) {
        sendCommand('chn3_cavgain', event);
    }); 
    
    $('#chn4_cavgain').on('change keypress focusout', function(event) {
        sendCommand('chn4_cavgain', event);
    });         
    
    $('#chn1_cainv').on('change keypress focusout', function(event) {
        sendCommand('chn1_cainv', event);
    });       
    
    $('#chn2_cainv').on('change keypress focusout', function(event) {
        sendCommand('chn2_cainv', event);
    }); 
    
    $('#chn3_cainv').on('change keypress focusout', function(event) {
        sendCommand('chn3_cainv', event);
    }); 
    
    $('#chn4_cainv').on('change keypress focusout', function(event) {
        sendCommand('chn4_cainv', event);
    });             
    
    $('#chn1_satmax').on('change keypress focusout', function(event) {
        sendCommand('chn1_satmax', event);
    });       
    
    $('#chn2_satmax').on('change keypress focusout', function(event) {
        sendCommand('chn2_satmax', event);
    }); 
    
    $('#chn3_satmax').on('change keypress focusout', function(event) {
        sendCommand('chn3_satmax', event);
    }); 
    
    $('#chn4_satmax').on('change keypress focusout', function(event) {
        sendCommand('chn4_satmax', event);
    });        
    
    $('#chn1_satmin').on('change keypress focusout', function(event) {
        sendCommand('chn1_satmin', event);
    });       
    
    $('#chn2_satmin').on('change keypress focusout', function(event) {
        sendCommand('chn2_satmax', event);
    }); 
    
    $('#chn3_satmin').on('change keypress focusout', function(event) {
        sendCommand('chn3_satmax', event);
    }); 
    
    $('#chn4_satmin').on('change keypress focusout', function(event) {
        sendCommand('chn4_satmin', event);
    });    
    
    $('#chn1_offset').on('change keypress focusout', function(event) {
        sendCommand('chn1_offset', event);
    });       
    
    $('#chn2_offset').on('change keypress focusout', function(event) {
        sendCommand('chn2_offset', event);
    }); 
    
    $('#chn3_offset').on('change keypress focusout', function(event) {
        sendCommand('chn3_offset', event);
    }); 
    
    $('#chn4_offset').on('change keypress focusout', function(event) {
        sendCommand('chn4_offset', event);
    });      
    
    $('#trigMode').on('change keypress focusout', function(event) {
        sendCommand('trigMode', event);
    });       
    
    $('#trigDelay').on('change keypress focusout', function(event) {
        sendCommand('trigDelay', event);
    }); 
    
    $('#trigInput').on('change keypress focusout', function(event) {
        sendCommand('trigInput', event);
    }); 
    
    $('#trigPol').on('change keypress focusout', function(event) {
        sendCommand('trigPol', event);
    });         
    
    $('#acqRange').on('change keypress focusout', function(event) {
        sendCommand('acqRange', event);
    });       
    
    $('#acqFilter').on('change keypress focusout', function(event) {
        sendCommand('acqFilter', event);
    }); 
    
    $('#acqTime').on('change keypress focusout', function(event) {
        sendCommand('acqTime', event);
    }); 
    
    $('#acqLowTime').on('change keypress focusout', function(event) {
        sendCommand('acqLowTime', event);
    });       
    
    $('#trigNTriggers').on('change keypress focusout', function(event) {
        sendCommand('trigNTriggers', event);
    });   

    $('#swtrigButton').on('click', function(event) {
        sendCommand('swtrigButton',event);
    });        
    
    $('#acqStartButton').on('click', function(event) {
        sendCommand('acqStartButton',event);
    });        
    
    $('#acqStopButton').on('click', function(event) {
        sendCommand('acqStopButton',event);
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
        
        
        var input_array = ["DIO_1", "DIO_2", "DIO_3", "DIO_4", "DIFF_IO_1", "DIFF_IO_2", "DIFF_IO_3", "DIFF_IO_4", "DIFF_IO_5", "DIFF_IO_6", "DIFF_IO_7", "DIFF_IO_8", "DIFF_IO_9"]
        var selectList = document.getElementById("trigInput");    
        for (var i = 0; i < input_array.length; i++) {
            var option = document.createElement("option");
            option.value = input_array[i];
            option.text = input_array[i];
            option.innerHTML = input_array[i];
            selectList.add(option);
        }    
        
        var tmode_array = ["SOFTWARE","HARDWARE","AUTOTRIGGER"];
        var selectList = document.getElementById("trigMode");    
        for (var i = 0; i < tmode_array.length; i++) {
            var option = document.createElement("option");
            option.value = tmode_array[i];
            option.text = tmode_array[i];
            option.innerHTML = tmode_array[i];
            selectList.add(option);
        }
        
        var tpol_array = ["FALLING","RISING"];
        var selectList = document.getElementById("trigPol");    
        for (var i = 0; i < tpol_array.length; i++) {
            var option = document.createElement("option");
            option.value = tpol_array[i];
            option.text = tpol_array[i];
            option.innerHTML = tpol_array[i];
            selectList.add(option);
        }        

        
        first_time_refresh = true;        
    }

    if ("chn1_cafilter" in allData) { 
        $("#chn1cafilter").html(allData.chn1_cafilter); 
        document.getElementById("chn1_cafilter").value = allData.chn1_cafilter;                
    }
    if ("chn2_cafilter" in allData) { 
        $("#chn2cafilter").html(allData.chn2_cafilter); 
        document.getElementById("chn2_cafilter").value = allData.chn2_cafilter;        
    }
    if ("chn3_cafilter" in allData) {
        $("#chn3cafilter").html(allData.chn3_cafilter); 
        document.getElementById("chn3_cafilter").value = allData.chn3_cafilter;        
    }
    if ("chn4_cafilter" in allData) {
        $("#chn4cafilter").html(allData.chn4_cafilter); 
        document.getElementById("chn4_cafilter").value = allData.chn4_cafilter;        
    }
    if ("chn1_caprefilter" in allData) {
        $("#chn1caPrefilter").html(allData.chn1_caprefilter); 
        document.getElementById("chn1_caPrefilter").value = allData.chn1_caprefilter;        
    }
    if ("chn2_caprefilter" in allData) {
        $("#chn2caPrefilter").html(allData.chn2_caprefilter); 
        document.getElementById("chn2_caPrefilter").value = allData.chn2_caprefilter;        
    }
    if ("chn3_caprefilter" in allData) {
        $("#chn3caPrefilter").html(allData.chn3_caprefilter); 
        document.getElementById("chn3_caPrefilter").value = allData.chn3_caprefilter;        
    }
    if ("chn4_caprefilter" in allData) {
        $("#chn4caPrefilter").html(allData.chn4_caprefilter); 
        document.getElementById("chn4_caPrefilter").value = allData.chn4_caprefilter;        
    }    
    if ("chn1_capostfilter" in allData) { 
        $("#chn1caPostfilter").html(allData.chn1_capostfilter); 
        document.getElementById("chn1_caPostfilter").value = allData.chn1_capostfilter;        
    }    
    if ("chn2_capostfilter" in allData) {
        $("#chn2caPostfilter").html(allData.chn2_capostfilter); 
        document.getElementById("chn2_caPostfilter").value = allData.chn2_capostfilter;        
    }    
    if ("chn3_capostfilter" in allData) {
        $("#chn3caPostfilter").html(allData.chn3_capostfilter); 
        document.getElementById("chn3_caPostfilter").value = allData.chn3_capostfilter;        
    }    
    if ("chn4_capostfilter" in allData) {
        $("#chn4caPostfilter").html(allData.chn4_capostfilter); 
        document.getElementById("chn4_caPostfilter").value = allData.chn4_capostfilter;        
    }        
    if ("chn1_carange" in allData) {
        $("#chn1carange").html(allData.chn1_carange); 
        document.getElementById("chn1_carange").value = allData.chn1_carange;
    }
    if ("chn2_carange" in allData) { 
        $("#chn2carange").html(allData.chn2_carange); 
        document.getElementById("chn2_carange").value = allData.chn2_carange;                
    }
    if ("chn3_carange" in allData) {
        $("#chn3carange").html(allData.chn3_carange); 
        document.getElementById("chn3_carange").value = allData.chn3_carange;
    }
    if ("chn4_carange" in allData) {
        $("#chn4carange").html(allData.chn4_carange); 
        document.getElementById("chn4_carange").value = allData.chn4_carange;           
    }
    if ("chn1_catigain" in allData) {
        $("#chn1catigain").html(allData.chn1_catigain); 
        document.getElementById("chn1_catigain").value = allData.chn1_catigain;
    }
    if ("chn2_catigain" in allData) {
        $("#chn2catigain").html(allData.chn2_catigain); 
        document.getElementById("chn2_catigain").value = allData.chn2_catigain;        
    }
    if ("chn3_catigain" in allData) {
        $("#chn3catigain").html(allData.chn3_catigain); 
        document.getElementById("chn3_catigain").value = allData.chn3_catigain;
    }
    if ("chn4_catigain" in allData) {
        $("#chn4catigain").html(allData.chn4_catigain); 
        document.getElementById("chn4_catigain").value = allData.chn4_catigain;   
    }
    if ("chn1_cavgain" in allData) {
        $("#chn1cavgain").html(allData.chn1_cavgain); 
        document.getElementById("chn1_cavgain").value = allData.chn1_cavgain;
    }
    if ("chn2_cavgain" in allData) {
        $("#chn2cavgain").html(allData.chn2_cavgain); 
        document.getElementById("chn2_cavgain").value = allData.chn2_cavgain;        
    }
    if ("chn3_cavgain" in allData) {
        $("#chn3cavgain").html(allData.chn3_cavgain); 
        document.getElementById("chn3_cavgain").value = allData.chn3_cavgain;
    }
    if ("chn4_cavgain" in allData) {
        $("#chn4cavgain").html(allData.chn4_cavgain); 
        document.getElementById("chn4_cavgain").value = allData.chn4_cavgain;   
    }
    if ("chn1_satmax" in allData) {
        $("#chn1satmax").html(allData.chn1_satmax); 
        document.getElementById("chn1_satmax").defaultValue = parseInt(allData.chn1_satmax);
    }
    if ("chn2_satmax" in allData) {
        $("#chn2satmax").html(allData.chn2_satmax); 
        document.getElementById("chn2_satmax").defaultValue = parseInt(allData.chn2_satmax);
    }
    if ("chn3_satmax" in allData) {
        $("#chn3satmax").html(allData.chn3_satmax); 
        document.getElementById("chn3_satmax").defaultValue = parseInt(allData.chn3_satmax);
    }
    if ("chn4_satmax" in allData) {
        $("#chn4satmax").html(allData.chn4_satmax); 
        document.getElementById("chn4_satmax").defaultValue = parseInt(allData.chn4_satmax);
    }    
    if ("chn1_satmin" in allData) {
        $("#chn1satmin").html(allData.chn1_satmin); 
        document.getElementById("chn1_satmin").defaultValue = parseInt(allData.chn1_satmin);
    }
    if ("chn2_satmin" in allData) {
        $("#chn2satmin").html(allData.chn2_satmin); 
        document.getElementById("chn2_satmin").defaultValue = parseInt(allData.chn2_satmin);
    }
    if ("chn3_satmin" in allData) {
        $("#chn3satmin").html(allData.chn3_satmin); 
        document.getElementById("chn3_satmin").defaultValue = parseInt(allData.chn3_satmin);
    }
    if ("chn4_satmin" in allData) {
        $("#chn4satmin").html(allData.chn4_satmin); 
        document.getElementById("chn4_satmin").defaultValue = parseInt(allData.chn4_satmin);
    }    
    if ("chn1_offset" in allData) {
        $("#chn1offset").html(allData.chn1_offset); 
        document.getElementById("chn1_offset").defaultValue = parseInt(allData.chn1_offset);
    }
    if ("chn2_offset" in allData) {
        $("#chn2offset").html(allData.chn2_offset); 
        document.getElementById("chn2_offset").defaultValue = parseInt(allData.chn2_offset);
    }
    if ("chn3_offset" in allData) {
        $("#chn3offset").html(allData.chn3_offset); 
        document.getElementById("chn3_offset").defaultValue = parseInt(allData.chn3_offset);
    }
    if ("chn4_offset" in allData) {
        $("#chn4offset").html(allData.chn4_offset); 
        document.getElementById("chn4_offset").defaultValue = parseInt(allData.chn4_offset);
    }    

    if ("acq_trig_mode" in allData) {
        $("#acq_trig_mode").html(allData.acq_trig_mode); 
        document.getElementById("trigMode").value = allData.acq_trig_mode;        
    }
    
    if ("acq_trig_pol" in allData) {
        $("#acq_trig_pol").html(allData.acq_trig_pol); 
        document.getElementById("trigPol").value = allData.acq_trig_pol;        
    }
    if ("acq_trig_delay" in allData) {
        $("#acq_trig_delay").html(allData.acq_trig_delay); 
        document.getElementById("trigDelay").defaultValue = allData.acq_trig_delay;                
    }
    if ("acq_trig_input" in allData) {
        $("#acq_trig_input").html(allData.acq_trig_input); 
        document.getElementById("trigInput").value = allData.acq_trig_input;        
    }
    if ("acq_time" in allData) {
        $("#acq_time").html(allData.acq_time); 
        document.getElementById("acqTime").defaultValue = allData.acq_time;        
    }
    if ("acq_lowtime" in allData) {
        $("#acq_lowtime").html(allData.acq_lowtime); 
        document.getElementById("acqLowTime").defaultValue = allData.acq_lowtime;        
    }
    if ("acq_trig_ntriggers" in allData) {
        $("#acq_trig_ntriggers").html(allData.acq_trig_ntriggers); 
        document.getElementById("trigNTriggers").defaultValue = allData.acq_trig_ntriggers;         
    }
    if ("acq_range" in allData) {
        $("#acq_range").html(allData.acq_range); 
        document.getElementById("acqRange").value = allData.acq_range;        
    }
    if ("acq_filter" in allData) {
        $("#acq_filter").html(allData.acq_filter); 
        document.getElementById("acqFilter").value = allData.acq_filter;                
    }
    if ("acq_state" in allData) {$("#acq_state").html(allData.acq_state); }

    if ("chn1_cainv" in allData) {
        $("#chn1cainv").html(allData.chn1_cainv); 
        document.getElementById("chn1_cainv").value = allData.chn1_cainv;
    }
    if ("chn2_cainv" in allData) {
        $("#chn2cainv").html(allData.chn2_cainv); 
        document.getElementById("chn2_cainv").value = allData.chn2_cainv;
    }
    if ("chn3_cainv" in allData) {
        $("#chn3cainv").html(allData.chn3_cainv); 
        document.getElementById("chn3_cainv").value = allData.chn3_cainv;
    }
    if ("chn4_cainv" in allData) {
        $("#chn4cainv").html(allData.chn4_cainv); 
        document.getElementById("chn4_cainv").value = allData.chn4_cainv;            
    }

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
    var elsToCtrl = ['trigMode', 'trigDelay', 'trigInput', 'trigPol', 'acqRange', 'acqFilter', 'acqTime', 'acqLowTime', 'trigNTriggers', 'chn1_cafilter', 'chn2_cafilter', 'chn3_cafilter', 'chn4_cafilter', 'chn1_caPostfilter', 'chn2_caPostfilter', 'chn3_caPostfilter', 'chn4_caPostfilter', 'chn1_caPrefilter', 'chn2_caPrefilter', 'chn3_caPrefilter', 'chn4_caPrefilter', 'chn1_carange', 'chn2_carange', 'chn3_carange', 'chn4_carange', 'chn1_catigain', 'chn2_catigain', 'chn3_catigain', 'chn4_catigain', 'chn1_cavgain', 'chn2_cavgain', 'chn3_cavgain', 'chn4_cavgain', 'chn1_cainv', 'chn2_cainv', 'chn3_cainv', 'chn4_cainv','chn1_offset','chn2_offset','chn3_offset','chn4_offset', 'chn1_satmax', 'chn2_satmax', 'chn3_satmax', 'chn4_satmax', 'chn1_satmin', 'chn2_satmin', 'chn3_satmin', 'chn4_satmin'];
    
    if (document.getElementById('acq_state').innerHTML == "ACQUIRING" || document.getElementById('acq_state').innerHTML == "RUNNING") {
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
        $("#acq_state").css("background-color", "#2ADE2A");
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
    var alertmsg1_flag = false;
    var alertmsg2_flag = false;
    
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
            alertmsg1_flag = true;
            var text = calculateRange(tmp1, tmp2);
            $("#"+key).html(text+"*");            
            $("#"+key).css("color", "red");
        }
        else {
            $("#"+key).html(idx_val);            
            $("#"+key).css("color", "white"); 
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
            alertmsg2_flag = true;
            tmp = document.getElementById(key).innerHTML;
            
            var tmp1_num = parseFloat(tmp1.replace(/[^\d\+]/g,""));
            var tmp2_num = parseFloat(tmp2.replace(/[^\d\+]/g,""));
            var text = idx_val;
            
            if (tmp1_num > tmp2_num) {
                text = tmp2;
            }
            else {
                text = tmp1;
            }
            $("#"+key).html(text+"**");
            $("#"+key).css("color", "red");            
        }
        else {
            $("#"+key).html(idx_val);
            $("#"+key).css("color", "white"); 
        }
    }
    
    if ( alertmsg1_flag == false ) {
        $("#alertmsg1").html("&nbsp");
    }    
    else {
        $("#alertmsg1").html("*Signal to Noise level not optimized!!&nbsp&nbsp");
    }
    
    if ( alertmsg2_flag == false ) {
        $("#alertmsg2").html("&nbsp");
    }    
    else {
        $("#alertmsg2").html("**Filters set at two different values!!&nbsp&nbsp");
    }
    
}

function calculateRange(tigain, vgain) {
    
    var tig_value = {"10K": 10e3,
        "1M": 1e6,
        "100M": 100e6,
        "1G": 1e9,
        "10G": 10e9,        
    };
    
    var vg_value = {'1': 1,
        '10': 10,
        '50': 50,
        '100': 100,
        'sat': 1000,
    };
    
    var calculated_range = 10 / (tig_value[tigain.toUpperCase()] * vg_value[vgain.toUpperCase()]);
    var text = ""
    
    if (calculated_range >= 1e-3 ) {
        text = "1mA";
    }
    else if (calculated_range >= 100e-6 ) {
        text = "100uA";
    }
    else if (calculated_range >= 10e-6 ) {
        text = "10uA";
    }
    else if (calculated_range >= 1e-6 ) {
        text = "1uA";
    }
    else if (calculated_range >= 100e-9 ) {
        text = "100nA";
    }
    else if (calculated_range >= 10e-9 ) {
        text = "10nA";
    }
    else if (calculated_range >= 1e-9 ) {
        text = "1nA";
    }
    else {
        text = "100pA";
    }
    
    return text;    
}

function sendCommand(command, event ) {
    var data = {}
    var channel;
    var exclude_elem = ['acqStartButton','acqStopButton','swtrigButton'];
    
    console.log("COMMAND = "+command);
    if ( exclude_elem.indexOf(command) == -1 ) {
        var tmp_value = document.getElementById(command).value;
        console.log("VALUE = "+tmp_value);
    }
    
    data['command'] = "";
    switch (command) {
        case 'chn1_cafilter':
        case 'chn2_cafilter':
        case 'chn3_cafilter':
        case 'chn4_cafilter':
            channel = command.replace('chn','').replace('_cafilter','');
            data['command'] = "CHAN0"+channel+":CABO:FILTER " + tmp_value;
            channel = 2;
            break;
            
        case 'acqFilter':
            data['command'] = "ACQU:FILTER " + tmp_value;
            break;

        case 'chn1_caPrefilter':
        case 'chn2_caPrefilter':
        case 'chn3_caPrefilter':
        case 'chn4_caPrefilter':
            channel = command.replace('chn','').replace('_caPrefilter','');            
            data['command'] = "CHAN0"+channel+":CABO:PREFILTER " + tmp_value;
            break;

        case 'chn1_caPostfilter':
        case 'chn2_caPostfilter':
        case 'chn3_caPostfilter':
        case 'chn4_caPostfilter':            
            channel = command.replace('chn','').replace('_caPostfilter','');                        
            data['command'] = "CHAN0"+channel+":CABO:POSTFILTER " + tmp_value;
            break;            
            
        case 'chn1_carange':
        case 'chn2_carange':
        case 'chn3_carange':
        case 'chn4_carange':            
            channel = command.replace('chn','').replace('_carange','');                        
            data['command'] = "CHAN0"+channel+":CABO:RANGE " + tmp_value;
            break;
            
        case 'acqRange':
            data['command'] = "ACQU:RANGE " + tmp_value;
            break;
            
        case 'chn1_catigain':
        case 'chn2_catigain':
        case 'chn3_catigain':
        case 'chn4_catigain':
            channel = command.replace('chn','').replace('_catigain','');                        
            data['command'] = "CHAN0"+channel+":CABO:TIGAIN " + tmp_value;
            break;
            
        case 'chn1_cavgain':
        case 'chn2_cavgain':
        case 'chn3_cavgain':
        case 'chn4_cavgain':
            channel = command.replace('chn','').replace('_cavgain','');                        
            data['command'] = "CHAN0"+channel+":CABO:VGAIN " + tmp_value;
            break;            
            
        case 'chn1_cainv':
        case 'chn2_cainv':
        case 'chn3_cainv':
        case 'chn4_cainv':
            if (tmp_value == "On") { tmp_value = "1" } else { tmp_value = "0"} 
            channel = command.replace('chn','').replace('_cainv','');                        
            data['command'] = "CHAN0"+channel+":CABO:INVE " + tmp_value;
            break;
            
        case 'chn1_offset':
        case 'chn2_offset':
        case 'chn3_offset':
        case 'chn4_offset':
            if ( event.which == 0 || event.which == 13 || event.keyCode == 13 ) {
                channel = command.replace('chn','').replace('_offset','');
                if ( parseFloat(tmp_value) < 0 ) {
                    return;
                }
                data['command'] = "CHAN0"+channel+":CABO:OFFS " + tmp_value;
            }
            else if (event.charCode >= 48 && event.charCode <= 57) {
                return;
            }                
            break;
            
        case 'swtrigButton':
            data['command'] = "TRIG:SWSE 1"
            break;
            
        case 'trigMode':
            data['command'] = "TRIG:MODE " + tmp_value
            break;
            
        case 'trigDelay':
            if ( event.which == 0 || event.which == 13 || event.keyCode == 13 ) {
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
            data['command'] = "TRIG:INPUT " + tmp_value
            break;
            
        case 'trigPol':
            data['command'] = "TRIG:POLA " + tmp_value
            break;            
            
        case 'acqTime':
            if ( event.which == 0 || event.which == 13 || event.keyCode == 13 ) {
                if ( parseFloat(tmp_value) < 1 ) {
                    return;
                }                
                data['command'] = "ACQU:TIME " + tmp_value
            }
            else if (event.charCode >= 48 && event.charCode <= 57) {
                return;
            }                
            break;
            
        case 'acqLowTime':
            if ( event.which == 0 || event.which == 13 || event.keyCode == 13 ) {
                if ( parseFloat(tmp_value) < 1 ) {
                    return;
                }                
                data['command'] = "ACQU:LOWT " + tmp_value
            }
            else if (event.charCode >= 48 && event.charCode <= 57) {
                return;
            }                
            break;
            
        case 'trigNTriggers':
            if ( event.which == 0 || event.which == 13 || event.keyCode == 13 ) {
                if ( parseFloat(tmp_value) < 0 ) {
                    return;
                }                
                data['command'] = "ACQU:NTRI " + tmp_value
            }
            else if (event.charCode >= 48 && event.charCode <= 57) {
                return;
            }                
            break;            
            
        case 'acqStartButton':
            data['command'] = "ACQU:START 1"
            break;

        case 'acqStopButton':
            data['command'] = "ACQU:STOP 1"
            break;
            
        case 'chn1_satmax':
        case 'chn2_satmax':
        case 'chn3_satmax':
        case 'chn4_satmax':            
            if ( event.which == 0 || event.which == 13 || event.keyCode == 13 ) {
                channel = command.replace('chn','').replace('_satmax','');
                if ( parseFloat(tmp_value) < 0 ) {
                    return;
                }
                data['command'] = "CHAN0"+channel+":CABO:SMAX " + tmp_value;
            }
            else if (event.charCode >= 48 && event.charCode <= 57) {
                return;
            }                
            break;
            
        case 'chn1_satmin':
        case 'chn2_satmin':
        case 'chn3_satmin':
        case 'chn4_satmin':
            if ( event.which == 0 || event.which == 13 || event.keyCode == 13 ) {
                channel = command.replace('chn','').replace('_satmin','');                
                if ( parseFloat(tmp_value) < 0 ) {
                    return;
                }
                data['command'] = "CHAN0"+channel+":CABO:SMIN " + tmp_value;
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