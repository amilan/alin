/* DataMain.js
 * Electrometer data acquisition for web display
 * 1.0
 * 2016-09-28
 *
 * By Manuel Broseta, mbroseta@cells.es
 */
var acq_plot;
var plot1;
var plot2;
var plot3;
var plot4;

var data1 = [];
var data2 = [];
var data3 = [];
var data4 = [];

var acq_data1 = [];
var acq_data2 = [];
var acq_data3 = [];
var acq_data4 = [];
var acq_ndata = 0;

var max_plot_points = 100;

var SHOW_GRAPHS = true;
var MAX_GRAPHS_LEN = 50;

var data1_range = "1mA"
var data1_range_max = 0.1;
var data1_range_min = -0.1;
var data1_unit = "mA";

var data2_range = "1mA"
var data2_range_max = 0.1;
var data2_range_min = -0.1;
var data2_unit = "mA";

var data3_range = "1mA"
var data3_range_max = 0.1;
var data3_range_min = -0.1;
var data3_unit = "mA";

var data4_range = "1mA"
var data4_range_max = 0.1;
var data4_range_min = -0.1;
var data4_unit = "mA";

var acq_table_scrolled = false;

var VOLTAGE_SATURATION_MAX = 90;
var sat1_max = VOLTAGE_SATURATION_MAX;
var sat2_max = VOLTAGE_SATURATION_MAX;
var sat3_max = VOLTAGE_SATURATION_MAX;
var sat4_max = VOLTAGE_SATURATION_MAX;

function refreshTime() {
    var dt = new Date();
    var d = dt.toDateString(); 
    var h = dt.getHours();
    var mi = ('0'+dt.getMinutes()).slice(-2);
    var s = ('0'+dt.getSeconds()).slice(-2);
    document.getElementById("time").innerHTML = "<b>"+d+" "+h+":"+mi+":"+s+"</b>";
} 
setInterval("refreshTime();", 1000)
    
function drawPlot(p_plot, p_data, p_unit, p_min, p_max, p_color) {
    var N = p_data[0].length; 
    var tick_array = []
    tick_array = Array.apply(null, {length: N}).map(Number.call, Number)
    var secs = tick_array.length.toString()
   
    var options = {      
        title: {
            text:'Current', 
            fontSize:'12pt',
            textColor: '#ffffff',
        },
        
        height: 200,                          // Define the height of the plot
        axes:{
            xaxis:{
                //ticks: tick_array,
                min: tick_array[1],
                max: tick_array[tick_array.length-1]+3,
                label:'time (last '+secs+' secs)',
                labelRenderer: $.jqplot.CanvasAxisLabelRenderer,  // Define the format for the text on the label
                labelOptions:{
                    formatString : '%.2f',
                    fontSize: '14pt',
                    textColor: '#ffffff',
                },                            
                renderer:$.jqplot.DateAxisRenderer,
                tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                tickOptions:{
                    show: false,                // Set this option to true to show xaxis label
                    formatString:'%H:%M:%S',  // Define the format of the axis of X
                    fontSize: '10pt',               // Define the size of the text
                    textColor: '#ffffff',
                angle: -45                      // Define the angle of the position of the text in the axis X
                }      
            },
            
            yaxis:{
                numberTicks: 5,
                label: p_unit,
                min: p_min,
                max: p_max,
                labelRenderer: $.jqplot.CanvasAxisLabelRenderer,  // Define the format for the text on the label
                labelOptions:{
                    formatString : '%.2f',
                    fontSize: '12pt',
                    textColor: '#ffffff',
                },
                tickRenderer: $.jqplot.CanvasAxisTickRenderer,  // Define the format for the text on the axis Y
                tickOptions:{
                    formatString : '%.2f',
                    fontSize: '8pt',
                    textColor: '#ffffff',
                }
            }
        },
        series:[{                                   // Define the format (colors, style ...) of the plot
            lineWidth:4,
            color:p_color, //#ff0000
            showMarker:false,
            fill: true,
            fillAndStroke: true,
            fillColor:p_color,
            fillAlpha: 0.4,
            markerOptions: { style:'diamond' },    
            pointLabels:{
                formatString : '%.1f',
                    show:false,
            }
        }],
        highlighter: {
            show: true,
            sizeAdjust: 10,
            tooltipAxes:'y',
            formatString:'<div style="font-size: 14px;background-color: #ffffcc; color: black">%f '+p_unit+'</div>'
                
        },
        grid: {                     // Define the "Grid", in this case we have a black background
            drawGridLines: false,
            background: "black",
            shadow: false
        },
    };
    
    var data_array = [];
    for (var i = 0; i < p_data[0].length; i++) {
        if (p_unit == "uA" ){
            data_array.push(p_data[0][i] * 1000);
        }
        else if (p_unit == "nA" ) {
            data_array.push(p_data[0][i] * 1000000);
        }
        else if (p_unit == "pA" ){
            data_array.push(p_data[0][i] * 1000000000);
        }
        else {
            data_array.push(p_data[0][i]);
        }
    };
    
    return $.jqplot (p_plot, [data_array], options);
}

function drawAcquisitionGraphs(p_plot, p_data1, p_data2, p_data3, p_data4)  {
    var xmax = 0;
    var txmax = 0;
    var tick_array = []
    
    var data_plot = [];
    var ymin = -0.001;
    var ymax = 0.001;
    var tmin = 0;
    var tmax = 0;
    
    var scroll_data = false;
    
    /* Build data array */
    if (p_data1.length  != 0) { data_plot.push(p_data1) } else { data_plot.push([]) }
    if (p_data2.length  != 0) { data_plot.push(p_data2) } else { data_plot.push([]) }
    if (p_data3.length  != 0) { data_plot.push(p_data3) } else { data_plot.push([]) }
    if (p_data4.length  != 0) { data_plot.push(p_data4) } else { data_plot.push([]) }
    
    /* Y-Axis limtis: Calculate max and min values */
    /* Get the maximum and minimum values of the four plots */
    for (var i = 0; i < data_plot.length; i++) {
        if (data_plot[i].length  != 0) { 
            tmax = Math.max.apply(Math, data_plot[i]);
            if ( tmax > ymax ) { ymax = tmax }
            tmin = Math.min.apply(Math, data_plot[i]);
            if ( tmin < ymin || ymin == 0) { ymin = tmin }
            txmax = ((data_plot[i].length/2)*2)+2;
            if ( txmax > xmax ) { xmax = txmax }
        }
    }
    
    /* Apply small corrections to yaxis limtis to display a lit bit more of the calculated numbers*/
    if (( ymin != 0 && ymin > -0.001 ) || ( ymin == 0 )) { ymin = -0.001 } else if ( ymin> 0 ) { ymin = ymin -(ymin*0.2)} else { ymin = ymin + (ymin*0.2)}
    if ( ymax != 0.001 ) { ymax = ymax+(ymax*0.2)}
    
    /* X-Axis limtis: Calculate the array of ticks to display */
    var start_val = 0;
    if (( xmax  > max_plot_points ) || ( xmax  > (max_plot_points/2) )) { 
        start_val = parseInt((xmax - max_plot_points)/2)*2;
        if ( start_val < 0 ) { start_val = 0 }
        i = start_val;
        xmax = xmax +2;
        while (i <= xmax ) {
            tick_array.push(i); 
            i += 4;
        }
    }
    
    else {
        i = start_val;
        while (i <= xmax ) {
            tick_array.push(i);
            i += 2;
        }        
    }
    
    /* Curves options */
    var options = {            
        height: 300,        
        axes:{
            xaxis:{
                ticks: tick_array,
                min: 0,
                max: xmax,
                label:'samples',
                labelRenderer: $.jqplot.DateAxisRenderer,  // Define the format for the text on the label
                labelOptions:{
                    formatString : '%.0f',
                    fontSize: '14pt',
                    textColor: '#ffffff',                        
                },                            
                tickOptions:{
                    show: true,                // Set this option to true to show xaxis label
                    textColor: '#ffffff',
                }      
            },
            
            yaxis:{
                numberTicks: 9,
                label: 'Current (mA)',                        
                min: ymin,
                max: ymax,
                labelRenderer: $.jqplot.CanvasAxisLabelRenderer,  // Define the format for the text on the label
                labelOptions:{
                    formatString : '%.2f',
                    fontSize: '12pt',
                    textColor: '#ffffff',                    
                },
                tickRenderer: $.jqplot.CanvasAxisTickRenderer,  // Define the format for the text on the axis Y
                tickOptions:{
                    formatString : '%f',
                    fontSize: '8pt',
                    textColor: '#ffffff',                    
                }
            }
        },

        series:[{                                   // Define the format (colors, style ...) of the plot
            lineWidth:4,
            showMarker:true,
            markerOptions: { style:'diamond' }, 
        }],
        seriesColors: [ '#FF0000', '#00FF00', '#00FFFF', '#FFFF00'],
        grid: {                     // Define the "Grid", in this case we have a black background
            drawGridLines: false,
            background: "black",
            shadow: false
        },
        highlighter: {
            show: true,
            sizeAdjust: 10,
            formatString:'<div style="font-size: 14px;background-color: #ffffcc; color: black"> sample: %i<br>current: %f mA</div>'
        },
        legend:{ 
            show:true, 
            showLabels: true,
            placement: "outsideGrid",
            location: "s",
            renderer: jQuery.jqplot.EnhancedLegendRenderer,
            rendererOptions: {
                numberColumns: 4,
                numberRows: 1,
            },                   
            labels: ['Channel 1', 'Channel2', 'Channel3', 'Channel4'],
        },                    
    };
    
    return $.jqplot (p_plot, data_plot, options);
}

function refreshData(allData) {
    if ("cacbtemp" in allData) { $("#cacbtemp").html(allData.cacbtemp); }
    if ("cafetemp" in allData) { $("#cafetemp").html(allData.cafetemp); }
    
    if ("acq_trig_mode" in allData) { $("#acq_trig_mode").html(allData.acq_trig_mode); }
    if ("acq_trig_pol" in allData) { $("#acq_trig_pol").html(allData.acq_trig_pol); }
    if ("acq_trig_delay" in allData) { $("#acq_trig_delay").html(allData.acq_trig_delay); }
    if ("acq_trig_input" in allData) { $("#acq_trig_input").html(allData.acq_trig_input); }
    if ("acq_time" in allData) { $("#acq_time").html(allData.acq_time); }
    if ("acq_ntriggers" in allData) { $("#acq_ntriggers").html(allData.acq_ntriggers); }
    if ("acq_range" in allData) { $("#acq_range").html(allData.acq_range); }
    if ("acq_filter" in allData) { $("#acq_filter").html(allData.acq_filter); }
    if ("acq_state" in allData) { $("#acq_state").html(allData.acq_state); }

    if ("acq_state" in allData) { 
        if (allData.acq_state == "ACQUIRING" || allData.acq_state == "RUNNING") {
            $("#acq_state").css("background-color", "#00FFFF");
            $("#acq_state").css("color", "black");
        }
        else {
            $("#acq_state").css("background-color", "#FF0000");
            $("#acq_state").css("color", "white");                    
        }          
    }
    
    if ("acq_ndata" in allData) { 
        acq_ndata = parseInt(allData.acq_ndata);
        $("#acq_ndata").html(acq_ndata);
    }
    if ("acq_chan01" in allData) { acq_data1 = allData.acq_chan01; }
    if ("acq_chan02" in allData) { acq_data2 = allData.acq_chan02; }
    if ("acq_chan03" in allData) { acq_data3 = allData.acq_chan03; }
    if ("acq_chan04" in allData) { acq_data4 = allData.acq_chan04; }

    if (acq_ndata != 0) {
        var text = '<table  border=1 frame=hsides rules=rows bordercolor="#222225"><caption>&nbsp;</caption><tbody>';
        if (acq_ndata > 0 ) {
            for (var i = 0; i<acq_ndata; i++) {
                text += "<tr class='selectable'>" 
                text += "<td class='table_cell_title4' width='200px'>"+(i+1)+"</td>"
                if ( i < acq_data1.length ) {
                    text += "<td class='table_cell_value'>"+acq_data1[i] +"</td>"
                }
                else {
                    text += "<td class='table_cell_value'></td>"
                }
                if ( i < acq_data2.length ) {
                    text += "<td class='table_cell_value'>"+acq_data2[i] +"</td>"
                }
                else {
                    text += "<td class='table_cell_value'></td>"
                }
                if ( i < acq_data3.length ) {
                    text += "<td class='table_cell_value'>"+acq_data3[i] +"</td>"
                }
                else {
                    text += "<td class='table_cell_value'></td>"
                }
                if ( i < acq_data4.length ) {
                    text += "<td class='table_cell_value'>"+acq_data4[i] +"</td>"
                }
                else {
                    text += "<td class='table_cell_value'></td>";
                }
                text += "</tr>" ;
            }
        }
        text += '</tbody></table>';
        $("#acq_table").html(text);
        
        if ( !acq_table_scrolled ) {
            var elem = document.getElementById('acq_table');
            elem.scrollTop = elem.scrollHeight;
        }
    }

    if ("ioport_1_name" in allData) { $("#ioport_1_name").html(allData.ioport_1_name); }
    if ("ioport_2_name" in allData) { $("#ioport_2_name").html(allData.ioport_2_name); }
    if ("ioport_3_name" in allData) { $("#ioport_3_name").html(allData.ioport_3_name); }
    if ("ioport_4_name" in allData) { $("#ioport_4_name").html(allData.ioport_4_name); }
    if ("ioport_5_name" in allData) { $("#ioport_5_name").html(allData.ioport_5_name); }
    if ("ioport_6_name" in allData) { $("#ioport_6_name").html(allData.ioport_6_name); }
    if ("ioport_7_name" in allData) { $("#ioport_7_name").html(allData.ioport_7_name); }
    if ("ioport_8_name" in allData) { $("#ioport_8_name").html(allData.ioport_8_name); }
    if ("ioport_9_name" in allData) { $("#ioport_9_name").html(allData.ioport_9_name); }
    if ("ioport_10_name" in allData) { $("#ioport_10_name").html(allData.ioport_10_name); }
    if ("ioport_11_name" in allData) { $("#ioport_11_name").html(allData.ioport_11_name); }
    if ("ioport_12_name" in allData) { $("#ioport_12_name").html(allData.ioport_12_name); }
    if ("ioport_13_name" in allData) { $("#ioport_13_name").html(allData.ioport_13_name); }
    
    if ("ioport_1_config" in allData) { $("#ioport_1_config").html(allData.ioport_1_config); }
    if ("ioport_2_config" in allData) { $("#ioport_2_config").html(allData.ioport_2_config); }
    if ("ioport_3_config" in allData) { $("#ioport_3_config").html(allData.ioport_3_config); }
    if ("ioport_4_config" in allData) { $("#ioport_4_config").html(allData.ioport_4_config); }
    if ("ioport_5_config" in allData) { $("#ioport_5_config").html(allData.ioport_5_config); }
    if ("ioport_6_config" in allData) { $("#ioport_6_config").html(allData.ioport_6_config); }
    if ("ioport_7_config" in allData) { $("#ioport_7_config").html(allData.ioport_7_config); }
    if ("ioport_8_config" in allData) { $("#ioport_8_config").html(allData.ioport_8_config); }
    if ("ioport_9_config" in allData) { $("#ioport_9_config").html(allData.ioport_9_config); }
    if ("ioport_10_config" in allData) { $("#ioport_10_config").html(allData.ioport_10_config); }
    if ("ioport_11_config" in allData) { $("#ioport_11_config").html(allData.ioport_11_config); }
    if ("ioport_12_config" in allData) { $("#ioport_12_config").html(allData.ioport_12_config); }
    if ("ioport_13_config" in allData) { $("#ioport_13_config").html(allData.ioport_13_config); }
    
    if ("ioport_1_value" in allData) { $("#ioport_1_value").html(allData.ioport_1_value); }
    if ("ioport_2_value" in allData) { $("#ioport_2_value").html(allData.ioport_2_value); }
    if ("ioport_3_value" in allData) { $("#ioport_3_value").html(allData.ioport_3_value); }
    if ("ioport_4_value" in allData) { $("#ioport_4_value").html(allData.ioport_4_value); }
    if ("ioport_5_value" in allData) { $("#ioport_5_value").html(allData.ioport_5_value); }
    if ("ioport_6_value" in allData) { $("#ioport_6_value").html(allData.ioport_6_value); }
    if ("ioport_7_value" in allData) { $("#ioport_7_value").html(allData.ioport_7_value); }
    if ("ioport_8_value" in allData) { $("#ioport_8_value").html(allData.ioport_8_value); }
    if ("ioport_9_value" in allData) { $("#ioport_9_value").html(allData.ioport_9_value); }
    if ("ioport_10_value" in allData) { $("#ioport_10_value").html(allData.ioport_10_value); }
    if ("ioport_11_value" in allData) { $("#ioport_11_value").html(allData.ioport_11_value); }
    if ("ioport_12_value" in allData) { $("#ioport_12_value").html(allData.ioport_12_value); }
    if ("ioport_13_value" in allData) { $("#ioport_13_value").html(allData.ioport_13_value); }
    
    if ("supplyport_1" in allData) {
        if (allData.supplyport_1 == 0) {
            $("#supplyport_1").html("High Impedance"); 
        }
        else {
            $("#supplyport_1").html("5V"); 
        }
    }
    if ("supplyport_2" in allData) {
        if (allData.supplyport_2 == 0) {
            $("#supplyport_2").html("High Impedance"); 
        }
        else {
            $("#supplyport_2").html("5V"); 
        }
    }
    if ("supplyport_3" in allData) {
        if (allData.supplyport_3 == 0) {
            $("#supplyport_3").html("High Impedance"); 
        }
        else {
            $("#supplyport_3").html("5V"); 
        }
    }
    if ("supplyport_4" in allData) {
        if (allData.supplyport_4 == 0) {
            $("#supplyport_4").html("High Impedance"); 
        }
        else {
            $("#supplyport_4").html("5V"); 
        }
    }
    
    if ("chn1_cafilter" in allData) { $("#chn1_cafilter").html(allData.chn1_cafilter); }
    if ("chn1_caprefilter" in allData) { $("#chn1_caprefilter").html(allData.chn1_caprefilter); }
    if ("chn1_capostfilter" in allData) { $("#chn1_capostfilter").html(allData.chn1_capostfilter); }
    if ("chn1_cainv" in allData) { $("#chn1_cainv").html(allData.chn1_cainv); }
    if ("chn1_carange" in allData) { $("#chn1_carange").html(allData.chn1_carange); }
    if ("chn1_carangeset" in allData) { 
        if ( allData.chn1_carangeset != data1_range ) {
            data1 = [];
        }
        data1_range = allData.chn1_carangeset;
    }
    if ("chn1_catigain" in allData) { $("#chn1_catigain").html(allData.chn1_catigain); }
    if ("chn1_cavgain" in allData) { $("#chn1_cavgain").html(allData.chn1_cavgain); }
    if ("chn1_catemp" in allData) { $("#chn1_catemp").html(allData.chn1_catemp); }
    if ("chn1_offset" in allData) { $("#chn1_offset").html(allData.chn1_offset); }
    if ("chn1_insvoltage" in allData) { 
        /*$("#chn1_insvoltage").html(parseFloat(allData.chn1_insvoltage) + " V" ); */
        $("#chn1_satvoltage").html( ((Math.abs(parseFloat(allData.chn1_insvoltage))*100)/10).toFixed(2) + "%" );
    }
    if ("chn1_avgcurrent" in allData) { $("#chn1_avgcurrent").html(currentDisplay(data1_range, allData.chn1_avgcurrent)); }
    if ("chn1_inscurrent" in allData) { 
        $("#chn1_inscurrent").html(currentDisplay(data1_range, allData.chn1_inscurrent)); 
        if (data1.length<MAX_GRAPHS_LEN) {
            data1.push(parseFloat(allData.chn1_inscurrent));
        } else {
            data1.shift();
            data1.push(parseFloat(allData.chn1_inscurrent));
        }
    }
    
    if ("chn2_cafilter" in allData) { $("#chn2_cafilter").html(allData.chn2_cafilter); }
    if ("chn2_caprefilter" in allData) { $("#chn2_caprefilter").html(allData.chn2_caprefilter); }
    if ("chn2_capostfilter" in allData) { $("#chn2_capostfilter").html(allData.chn2_capostfilter); }
    if ("chn2_cainv" in allData) { $("#chn2_cainv").html(allData.chn2_cainv); }
    if ("chn2_carange" in allData) { $("#chn2_carange").html(allData.chn2_carange); }
    if ("chn2_carangeset" in allData) { 
        if ( allData.chn2_carangeset != data2_range ) {
            data2 = [];
        }
        data2_range = allData.chn2_carangeset;
    }
    if ("chn2_catigain" in allData) { $("#chn2_catigain").html(allData.chn2_catigain); }
    if ("chn2_cavgain" in allData) { $("#chn2_cavgain").html(allData.chn2_cavgain); }
    if ("chn2_catemp" in allData) { $("#chn2_catemp").html(allData.chn2_catemp); }
    if ("chn2_offset" in allData) { $("#chn2_offset").html(allData.chn2_offset); }
    if ("chn2_insvoltage" in allData) { 
        /*$("#chn2_insvoltage").html(parseFloat(allData.chn2_insvoltage) + " V" );*/
        $("#chn2_satvoltage").html( ((Math.abs(parseFloat(allData.chn2_insvoltage))*100)/10).toFixed(2) + "%" );
    }
    if ("chn2_avgcurrent" in allData) { $("#chn2_avgcurrent").html(currentDisplay(data2_range, allData.chn2_avgcurrent)); }
    if ("chn2_inscurrent" in allData) { 
        $("#chn2_inscurrent").html(currentDisplay(data2_range, allData.chn2_inscurrent)); 
        if (data2.length<MAX_GRAPHS_LEN) {
            data2.push(parseFloat(allData.chn2_inscurrent));
        } else {
            data2.shift();
            data2.push(parseFloat(allData.chn2_inscurrent));
        }
    }
    
    if ("chn3_cafilter" in allData) { $("#chn3_cafilter").html(allData.chn3_cafilter); }
    if ("chn3_caprefilter" in allData) { $("#chn3_caprefilter").html(allData.chn3_caprefilter); }
    if ("chn3_capostfilter" in allData) { $("#chn3_capostfilter").html(allData.chn3_capostfilter); }
    if ("chn3_cainv" in allData) { $("#chn3_cainv").html(allData.chn3_cainv); }
    if ("chn3_carange" in allData) { $("#chn3_carange").html(allData.chn3_carange); }
    if ("chn3_carangeset" in allData) { 
        if ( allData.chn3_carangeset != data3_range ) {
            data3 = [];
        }
        data3_range = allData.chn3_carangeset;
    }
    if ("chn3_catigain" in allData) { $("#chn3_catigain").html(allData.chn3_catigain); }
    if ("chn3_cavgain" in allData) { $("#chn3_cavgain").html(allData.chn3_cavgain); }
    if ("chn3_catemp" in allData) { $("#chn3_catemp").html(allData.chn3_catemp); }
    if ("chn3_offset" in allData) { $("#chn3_offset").html(allData.chn3_offset); }
    if ("chn3_insvoltage" in allData) {
        /*$("#chn3_insvoltage").html(parseFloat(allData.chn3_insvoltage) + " V" );*/
        $("#chn3_satvoltage").html( ((Math.abs(parseFloat(allData.chn3_insvoltage))*100)/10).toFixed(2) + "%");
    }
    if ("chn3_avgcurrent" in allData) { $("#chn3_avgcurrent").html(currentDisplay(data3_range, allData.chn3_avgcurrent)); }
    if ("chn3_inscurrent" in allData) { 
        $("#chn3_inscurrent").html(currentDisplay(data3_range, allData.chn3_inscurrent)); 
        if (data3.length<MAX_GRAPHS_LEN) {
            data3.push(parseFloat(allData.chn3_inscurrent));
        } else {
            data3.shift();
            data3.push(parseFloat(allData.chn3_inscurrent));
        }
    }
    
    if ("chn4_cafilter" in allData) { $("#chn4_cafilter").html(allData.chn4_cafilter); }
    if ("chn4_caprefilter" in allData) { $("#chn4_caprefilter").html(allData.chn4_caprefilter); }
    if ("chn4_capostfilter" in allData) { $("#chn4_capostfilter").html(allData.chn4_capostfilter); }
    if ("chn4_cainv" in allData) { $("#chn4_cainv").html(allData.chn4_cainv); }
    if ("chn4_carange" in allData) { $("#chn4_carange").html(allData.chn4_carange); }
    if ("chn4_carangeset" in allData) { 
        if ( allData.chn4_carangeset != data4_range ) {
            data4 = [];
        }
        data4_range = allData.chn4_carangeset;
    }
    if ("chn4_catigain" in allData) { $("#chn4_catigain").html(allData.chn4_catigain); }
    if ("chn4_cavgain" in allData) { $("#chn4_cavgain").html(allData.chn4_cavgain); }
    if ("chn4_catemp" in allData) { $("#chn4_catemp").html(allData.chn4_catemp); }
    if ("chn4_offset" in allData) { $("#chn4_offset").html(allData.chn4_offset); }
    if ("chn4_insvoltage" in allData) { 
        /*$("#chn4_insvoltage").html(parseFloat(allData.chn4_insvoltage) + " V" );*/
        $("#chn4_satvoltage").html( ((Math.abs(parseFloat(allData.chn4_insvoltage))*100)/10).toFixed(2) + "%" );
    }
    if ("chn4_avgcurrent" in allData) { $("#chn4_avgcurrent").html(currentDisplay(data4_range, allData.chn4_avgcurrent)); }
    if ("chn4_inscurrent" in allData) { 
        $("#chn4_inscurrent").html(currentDisplay(data4_range, allData.chn4_inscurrent)); 
        if (data4.length<MAX_GRAPHS_LEN) {
            data4.push(parseFloat(allData.chn4_inscurrent));
        } else {
            data4.shift();
            data4.push(parseFloat(allData.chn4_inscurrent));
        }
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
    
    if ("chn1_satmax" in allData) { sat1_max = parseFloat(allData.chn1_satmax); }
    if ("chn2_satmax" in allData) { sat2_max = parseFloat(allData.chn2_satmax); }
    if ("chn3_satmax" in allData) { sat3_max = parseFloat(allData.chn3_satmax); }
    if ("chn4_satmax" in allData) { sat4_max = parseFloat(allData.chn4_satmax); }
    
    if ("fv_instant" in allData) { $("#fv_instant").html(allData.fv_instant); }
    if ("fv_avg" in allData) { $("#fv_avg").html(allData.fv_avg); }
    if ("fv_max" in allData) { $("#fv_max").html(allData.fv_max); }
    if ("fv_min" in allData) { $("#fv_min").html(allData.fv_min); }
    if ("fv_led" in allData) { $("#fv_led").html(allData.fv_led); }
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
    
    if ("diags_mactreq_0" in allData) { $("#diags_mactreq_0").html(allData.diags_mactreq_0); }
    if ("diags_mlen_0" in allData) { $("#diags_mlen_0").html(allData.diags_mlen_0); }    
    if ("diags_msgnact_0" in allData) { $("#diags_msgnact_0").html(allData.diags_msgnact_0); }    
    if ("diags_uploadmsg_0" in allData) { $("#diags_uploadmsg_0").html(allData.diags_uploadmsg_0); }    
    if ("diags_dwloadmsg_0" in allData) { $("#diags_dwloadmsg_0").html(allData.diags_dwloadmsg_0); }    
    
    if ("diags_mactreq_1" in allData) { $("#diags_mactreq_1").html(allData.diags_mactreq_1); }
    if ("diags_mlen_1" in allData) { $("#diags_mlen_1").html(allData.diags_mlen_1); }    
    if ("diags_msgnact_1" in allData) { $("#diags_msgnact_1").html(allData.diags_msgnact_1); }    
    if ("diags_uploadmsg_1" in allData) { $("#diags_uploadmsg_1").html(allData.diags_uploadmsg_1); }    
    if ("diags_dwloadmsg_1" in allData) { $("#diags_dwloadmsg_1").html(allData.diags_dwloadmsg_1); }    
    
    if ("diags_mactreq_2" in allData) { $("#diags_mactreq_2").html(allData.diags_mactreq_2); }
    if ("diags_mlen_2" in allData) { $("#diags_mlen_2").html(allData.diags_mlen_2); }    
    if ("diags_msgnact_2" in allData) { $("#diags_msgnact_2").html(allData.diags_msgnact_2); }    
    if ("diags_uploadmsg_2" in allData) { $("#diags_uploadmsg_2").html(allData.diags_uploadmsg_2); }    
    if ("diags_dwloadmsg_2" in allData) { $("#diags_dwloadmsg_2").html(allData.diags_dwloadmsg_2); }    
    
    if ("diags_vaux" in allData) { $("#diags_vaux").html(allData.diags_vaux); }    
    if ("diags_vcc" in allData) { $("#diags_vcc").html(allData.diags_vcc); }    
    if ("diags_viso" in allData) { $("#diags_viso").html(allData.diags_viso); }    
    if ("diags_vs" in allData) { $("#diags_vs").html(allData.diags_vs); }    
    if ("diags_vspec" in allData) { $("#diags_vspec").html(allData.diags_vspec); }
    if ("diags_12v" in allData) { $("#diags_12v").html(allData.diags_12v); }

    if ("psb_vaux" in allData) { 
        $("#psb_vaux").html(allData.psb_vaux);
        if (allData.psb_vaux == "On") {
            $("#psb_vaux").css("background-color", "#00FF00");
            $("#psb_vaux").css("color", "black");                                        
        }
        else {
            $("#psb_vaux").css("background-color", "#FF0000");
            $("#psb_vaux").css("color", "white");                    
        }
    }

    if ("psb_vcc" in allData) { 
        $("#psb_vcc").html(allData.psb_vcc);
        if (allData.psb_vcc == "On") {
            $("#psb_vcc").css("background-color", "#00FF00");
            $("#psb_vcc").css("color", "black");                                        
        }
        else {
            $("#psb_vcc").css("background-color", "#FF0000");
            $("#psb_vcc").css("color", "white");                    
        }
    }

    if ("psb_viso" in allData) { 
        $("#psb_viso").html(allData.psb_viso);
        if (allData.psb_viso == "On") {
            $("#psb_viso").css("background-color", "#00FF00");
            $("#psb_viso").css("color", "black");                                        
        }
        else {
            $("#psb_viso").css("background-color", "#FF0000");
            $("#psb_viso").css("color", "white");                    
        }
    }
        
    if ("psb_vs" in allData) { 
        $("#psb_vs").html(allData.psb_vs);
        if (allData.psb_vs == "On") {
            $("#psb_vs").css("background-color", "#00FF00");
            $("#psb_vs").css("color", "black");                                        
        }
        else {
            $("#psb_vs").css("background-color", "#FF0000");
            $("#psb_vs").css("color", "white");                    
        }
    }

    if ("version" in allData) { $("#version").html("<b>&nbsp"+allData.version+"&nbsp</b>"); }
    if ("identification" in allData) { $("#identification").html("<b>&nbsp"+allData.identification+"&nbsp</b>"); }
    if ("mac" in allData) { $("#mac").html("<b>&nbsp"+allData.mac+"&nbsp</b>"); }
    if ("fwversion" in allData) { $("#fwversion").html("<b>&nbsp"+allData.fwversion+"&nbsp</b>"); }
    
    /* If web graphs are enabled */
    if (SHOW_GRAPHS == true) {
        
        /* 1. Display General current grahs */
        if ("chn1_carange_value" in allData) { 
            data1_range_max = parseInt(allData.chn1_carange_value);
            data1_range_min = Math.abs(data1_range_max) * -1;
        }
        if ("chn1_carange_unit" in allData) { data1_unit = allData.chn1_carange_unit; }
        if (plot1) {
            plot1.destroy();
        }
        plot1 = drawPlot('chart1', [data1], data1_unit, data1_range_min, data1_range_max, '#FF0000');
        
        if ("chn2_carange_value" in allData) { 
            data2_range_max = parseInt(allData.chn2_carange_value);
            data2_range_min = Math.abs(data2_range_max) * -1;
        }
        if ("chn2_carange_unit" in allData) { data2_unit = allData.chn2_carange_unit; }
        if (plot2) {
            plot2.destroy();
        }
        plot2 = drawPlot('chart2', [data2], data2_unit, data2_range_min, data2_range_max, '#00FF00');
        
        if ("chn3_carange_value" in allData) { 
            data3_range_max = parseInt(allData.chn3_carange_value);
            data3_range_min = Math.abs(data3_range_max) * -1;
        }
        if ("chn3_carange_unit" in allData) { data3_unit = allData.chn3_carange_unit; }
        if (plot3) {
            plot3.destroy();
        }
        plot3 = drawPlot('chart3', [data3], data3_unit, data3_range_min, data3_range_max, '#00FFFF');
        
        if ("chn4_carange_value" in allData) { 
            data4_range_max = parseInt(allData.chn4_carange_value);
            data4_range_min = Math.abs(data4_range_max) * -1;
        }
        if ("chn4_carange_unit" in allData) { data4_unit = allData.chn4_carange_unit; }
        if (plot4) {
            plot4.destroy();
        }
        plot4 = drawPlot('chart4', [data4], data4_unit, data4_range_min, data4_range_max, '#FFFF00');

        /* 2. Display Acquisition grahs */
        if (acq_ndata == 0) {
            document.getElementById("graphs_acqrow").style.display = "none";
            $("#acq_table").html("");
            acq_data1 = [];
            acq_data2 = [];
            acq_data3 = [];
            acq_data4 = [];
            setUserScroll(false);
            document.getElementById("acq_results").style.display = "none";
        }
        else {
            document.getElementById("acq_results").style.display = "inline";
            document.getElementById("graphs_acqrow").style.display = "table-row"; 
            if (acq_plot) {
                acq_plot.destroy();
            }
            acq_plot = drawAcquisitionGraphs('acq_chart', acq_data1, acq_data2, acq_data3, acq_data4);                                    
        }                
    }
    else {
        document.getElementById("graphs_row").style.display = "none";
        document.getElementById("graphs_acqrow").style.display = "none";
    }        
    
    try {
        checkSettings();
    }
    catch (err) {
        console.log("checkSettings() Error");
    } 
} 

function checkSettings() {
    var alertmsg1_flag = false;
    var alertmsg2_flag = false;
    var alertsatmsg_flag = false;
    
    /* range_vals: tigain, vgain */
    var range_vals = { '1mA': ['10k','1'], '100uA': ['10k', '10'], '10uA': ['1M', '1'], '1uA': ['1M', '10'],'100nA': ['100M', '1'], '10nA': ['1G', '1'], '1nA': ['10G', '1'], '100pA': ['10G', '10']};
    var range_els = { 'chn1_carange': ['chn1_catigain',  'chn1_cavgain'], 'chn2_carange': ['chn2_catigain', 'chn2_cavgain'], 'chn3_carange': ['chn3_catigain', 'chn3_cavgain'], 'chn4_carange': ['chn4_catigain', 'chn4_cavgain' ]};
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
            $("#"+key).css("color", "#ccb95c"); 
        }
    }
    
    /* filter_vals: postfilter, prefilter */
    var filter_vals = {'3200Hz': ['3200Hz', '3500Hz'], '100Hz': ['100Hz', '100Hz'], '10Hz': ['10Hz', '10Hz'], '1Hz': ['1Hz', '1Hz'], '0.5Hz': ['1Hz', '0.5Hz']};
    var filter_els = { 'chn1_cafilter': ['chn1_capostfilter', 'chn1_caprefilter'], 'chn2_cafilter': ['chn2_capostfilter', 'chn2_caprefilter'], 'chn3_cafilter': ['chn3_capostfilter', 'chn3_caprefilter'],'chn4_cafilter': ['chn4_capostfilter', 'chn4_caprefilter']};
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
            $("#"+key).css("color", "#ccb95c"); 
        }
    }
    
    
    var_voltagesat = ["chn1_satvoltage","chn2_satvoltage","chn3_satvoltage","chn4_satvoltage"]
    max_val = [sat1_max, sat2_max, sat3_max, sat4_max];    
    
    for (var j = 0; j < var_voltagesat.length; j++) {
        tmp = document.getElementById(var_voltagesat[j]).innerHTML;

        if ( parseFloat(tmp) > max_val[j] ) {
            alertsatmsg_flag = true;
            $("#"+var_voltagesat[j]).html(tmp+"***");
            $("#"+var_voltagesat[j]).css("color", "red");
        }
        else {
            $("#"+var_voltagesat[j]).css("color", "#ccb95c"); 
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
    
    if ( alertsatmsg_flag == false ) {
        $("#alertsatmsg").html("&nbsp");
    }    
    else {
        $("#alertsatmsg").html("***Current amplifer could be saturating!!&nbsp&nbsp");
    }
    
}

function dateToString(date) {
    var month = date.getMonth() + 1;
    var day = date.getDate();
    var dateOfString = date.getFullYear();
    dateOfString += (("" + month).length < 2 ? "0" : "") + month;
    dateOfString += (("" + day).length < 2 ? "0" : "") + day;
    return dateOfString;
}

function timeToString(date) {
    var secs = date.getSeconds();
    var min = date.getMinutes();
    var hours = date.getHours();
    var timeOfString = (("" + hours).length < 2 ? "0" : "") + hours;
    timeOfString += (("" + min).length < 2 ? "0" : "") + min;
    timeOfString += (("" + secs).length < 2 ? "0" : "") + secs;
    return timeOfString;
}


function saveData(){
    var currentdate = new Date(); 
    var date = dateToString(currentdate );
    var time = timeToString(currentdate);
    var name = window.location.hostname;
    var filename = date + "_" + time + "_" + name + ".csv";
    
    var data_dict = {"EquipmentName": name,
                    "Date": date,
                    "Time": time, 
                    "TriggerMode": document.getElementById("acq_trig_mode").innerHTML,
                    "TriggerDelay": document.getElementById("acq_trig_delay").innerHTML,
                    "TriggerInput": document.getElementById("acq_trig_input").innerHTML,
                    "TriggerPolarity": document.getElementById("acq_trig_pol").innerHTML,
                    "AcquisitionTime": document.getElementById("acq_time").innerHTML,
                    "AcquisitionTriggers": document.getElementById("acq_ntriggers").innerHTML,
                    "AcquisitionNData": document.getElementById("acq_ndata").innerHTML,
                    "Channel1_Filter": document.getElementById("chn1_cafilter").innerHTML,
                    "Channel1_PreFilter": document.getElementById("chn1_caprefilter").innerHTML,
                    "Channel1_PostFilter": document.getElementById("chn1_capostfilter").innerHTML,
                    "Channel1_Range": document.getElementById("chn1_carange").innerHTML,
                    "Channel1_TiGain": document.getElementById("chn1_catigain").innerHTML,
                    "Channel1_VGain": document.getElementById("chn1_cavgain").innerHTML,
                    "Channel1_Inversion": document.getElementById("chn1_cainv").innerHTML,
                    "Channel1_Offset": document.getElementById("chn1_offset").innerHTML, 
                    "Channel2_Filter": document.getElementById("chn2_cafilter").innerHTML,
                    "Channel2_PreFilter": document.getElementById("chn2_caprefilter").innerHTML,
                    "Channel2_PostFilter": document.getElementById("chn2_capostfilter").innerHTML,
                    "Channel2_Range": document.getElementById("chn2_carange").innerHTML,
                    "Channel2_TiGain": document.getElementById("chn2_catigain").innerHTML,
                    "Channel2_VGain": document.getElementById("chn2_cavgain").innerHTML,
                    "Channel2_Inversion": document.getElementById("chn2_cainv").innerHTML,
                    "Channel2_Offset": document.getElementById("chn2_offset").innerHTML,                 
                    "Channel3_Filter": document.getElementById("chn3_cafilter").innerHTML,
                    "Channel3_PreFilter": document.getElementById("chn3_caprefilter").innerHTML,
                    "Channel3_PostFilter": document.getElementById("chn3_capostfilter").innerHTML,
                    "Channel3_Range": document.getElementById("chn3_carange").innerHTML,
                    "Channel3_TiGain": document.getElementById("chn3_catigain").innerHTML,
                    "Channel3_VGain": document.getElementById("chn3_cavgain").innerHTML,
                    "Channel3_Inversion": document.getElementById("chn3_cainv").innerHTML,
                    "Channel3_Offset": document.getElementById("chn3_offset").innerHTML,                 
                    "Channel4_Filter": document.getElementById("chn4_cafilter").innerHTML,
                    "Channel4_PreFilter": document.getElementById("chn4_caprefilter").innerHTML,
                    "Channel4_PostFilter": document.getElementById("chn4_capostfilter").innerHTML,
                    "Channel4_Range": document.getElementById("chn4_carange").innerHTML,
                    "Channel4_TiGain": document.getElementById("chn4_catigain").innerHTML,
                    "Channel4_VGain": document.getElementById("chn4_cavgain").innerHTML,
                    "Channel4_Inversion": document.getElementById("chn4_cainv").innerHTML,
                    "Channel4_Offset": document.getElementById("chn4_offset").innerHTML,                 
                }
                
    var col1 = Object.keys(data_dict);

    if (data_dict["Channel1_Range"] == 'AUTO' ) {
        data_dict["Channel1_TiGain"] = "";
        data_dict["Channel1_VGain"] = "";
    }
    else {
        data_dict["Channel1_Range"] = calculateRange(data_dict["Channel1_TiGain"], data_dict["Channel1_VGain"]);
    }
    
    if (data_dict["Channel2_Range"] == 'AUTO' ) {
        data_dict["Channel2_TiGain"] = "";
        data_dict["Channel2_VGain"] = "";
    }
    else {
        data_dict["Channel2_Range"] = calculateRange(data_dict["Channel2_TiGain"], data_dict["Channel2_VGain"]);
    }
    
    if (data_dict["Channel3_Range"] == 'AUTO' ) {
        data_dict["Channel3_TiGain"] = "";
        data_dict["Channel3_VGain"] = "";
    }
    else {
        data_dict["Channel3_Range"] = calculateRange(data_dict["Channel3_TiGain"], data_dict["Channel3_VGain"]);
    }
    
    if (data_dict["Channel4_Range"] == 'AUTO' ) {
        data_dict["Channel4_TiGain"] = "";
        data_dict["Channel4_VGain"] = "";
    }
    else {
        data_dict["Channel4_Range"] = calculateRange(data_dict["Channel4_TiGain"], data_dict["Channel4_VGain"]);
    }
    
    var col2 = [];
    for (var key in data_dict) {
        if (data_dict.hasOwnProperty(key)) {
            col2.push(data_dict[key]);
        }
    }
    
    var col3 = [];                
    var col4 = ['Channel1_Data (mA)'];
    col4 = col4.concat(acq_data1);
    var col5 = ['Channel2_Data (mA)'];
    col5 = col5.concat(acq_data2);
    var col6 = ['Channel3_Data (mA)'];
    col6 = col6.concat(acq_data3);
    var col7 = ['Channel4_Data (mA)'];
    col7 = col7.concat(acq_data4);
    
    /* Max_length is the length of the longest column */
    master_array = [col1, col2, col3, col4, col5, col6, col7]
    var max_len = 0;
    for (var i = 0; i < master_array.length; i++) {
        if (master_array[i].length >= max_len) {
            max_len = master_array[i].length;
        }
    }
    
    var parts = [];
    for (var rownum = 0; rownum < max_len; rownum++) {
        var row = '';
        for (var colnum = 0; colnum < master_array.length; colnum++) {
            if (rownum < master_array[colnum].length) {
                row += master_array[colnum][rownum]+",";
            }
            else {
                row += ",";
            }
        }
        parts.push(row+",\n");
    }
    
    var blob = new Blob(parts);            
    saveAs(blob, filename); 
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
    
    var calculated_range = 10 / (tig_value[tigain] * vg_value[vgain]);
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

function currentDisplay(range, data) {
    
    var rep = { "1mA" : [2, 1e-3, " uA", 1999.99 ], /* 1mA is represented as 1XXX.XX uA */
                "100uA" : [3, 1e-3, " uA", 199.999 ], /* 100uA is represented as 1XX.XXX uA */
                "10uA" : [4, 1e-3, " uA", 19.9999], /* 10uA is represented as 1X.XXXX uA */
                "1uA" : [2, 1e-6, " nA", 1999.99], /* 1uA is represented as 1XXX.XX nA */
                "100nA" : [3, 1e-6, " nA", 199.999], /* 100nA is represented as 1XX.XXX nA */
                "10nA" : [4, 1e-6, " nA" , 19.9999], /* 10nA is represented as 1X.XXXX uA */
                "1nA" : [2, 1e-9, " pA", 1999.99], /* 100uaA is represented as 1XXX.XX uA */
                "100pA" : [3, 1e-9, " pA", 199.999 ], /* 100uaA is represented as 1XXX.XXX uA */
    };
    
    var num = parseFloat(data);
    var text = "";
    
    try {
        num = num / rep[range][1];
        if ((num >= -Math.abs(rep[range][3])) && (num <= Math.abs(rep[range][3]))) {
            text += num.toFixed(rep[range][0]) + rep[range][2];
        }
        else {
            text += num.toExponential(3) + rep[range][2];
        }
    }
    catch (err) {
        console.log("Error calculatind current display data");
    } 
    
    return text;
}    

function setUserScroll(){
    var elem = document.getElementById('acq_table');
    var elemheight = $("#acq_table").height();
    
    if ((elemheight + elem.scrollTop) == elem.scrollHeight) {
        acq_table_scrolled=false;
    }
    else {
        acq_table_scrolled=true;
    }
}

$(document).ready(function() {
    updater.start();
    
    // Get the element with id="defaultOpen" and click on it
    document.getElementById("defaultOpen").click();    
});

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

function openTab(evt, tabName) {
    // Declare all variables
    var i, tabcontent, tablinks;
    
    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    
    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    
    // Show the current tab, and add an "active" class to the link that opened the tab
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}
