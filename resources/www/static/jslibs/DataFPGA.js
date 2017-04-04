/* DataFPGA.js
 * Electrometer data acquisition for web display
 * 1.0
 * 2016-10-03
 *
 * By Manuel Broseta, mbroseta@cells.es
 */

$(document).ready(function() {
    updater.start();
});

var updater = {
    socket: null,
    
    start: function() {
        var url = "ws://" + location.host + "/fpga";

        updater.socket = new WebSocket(url);
        updater.socket.onmessage = function(event) {
            updater.showMessage(JSON.parse(event.data));
        }
    },
    
    showMessage: function(jsondata) {
        refreshFPGAData(jsondata)
    }
};

function refreshTime() {
    var dt = new Date();
    var d = dt.toDateString(); 
    var h = dt.getHours();
    var mi = ('0'+dt.getMinutes()).slice(-2);
    var s = ('0'+dt.getSeconds()).slice(-2);
    document.getElementById("time").innerHTML = "<b>"+d+" "+h+":"+mi+":"+s+"</b>";
} 
setInterval("refreshTime();", 1000)

function refreshFPGAData(allData) {
    if ( allData.length != 0 ) {
        var content='';
        var data =''
        var col = 1
        
        var references = []
        references.push({item: 'WB-HRMY-CROSSBAR', value:'/static/doc/hrmy_crossbar_block.html'})
        references.push({item: 'WB-HRMY-AVERAGE', value:'/static/doc/AVERAGE_block.html'})
        references.push({item: 'WB-HRMY-FIFO', value:'/static/doc/em2_FIFO_block.html'})
        references.push({item: 'WB-FMC-ADC-CORE', value:'/static/doc/fmc_adc_18b_400ks_csr.html'})
        references.push({item: 'WB-HRMY-MEMORY', value:'/static/doc/hrmy_mem_block.html'})
        references.push({item: 'WB-HRMY-ID-GEN', value:'/static/doc/ID_GEN_block.html'})
        references.push({item: 'WB-FMC-FV-CONTROL', value:'/static/doc/fmc_adc_18b_FV_Ctrl_csr.html'})
        references.push({item: 'SPI', value:'/static/doc/em2_spi_config_csr.html'})
        references.push({item: 'WB-EM2-DIGITAL_IO', value:'/static/doc/em2_digital_io_csr.html'})
        references.push({item: 'EM2_DAC', value:'/static/doc/em2_DAC_csr.html'})
        
        $.each( allData, function( type, el){
            
            if (type == 'Last update') {
                data = "Last Updated FPGA data: " + el.DATE + "  " + el.TIME
            }
            else {
                $.each( el, function( index, item){
                    var table = ''
                    
                    if (col==1){
                        table += '<tr>';
                    }
                    else {
                        table += '<td></td>';
                    }
                    
                    table +='<td style="vertical-align:top"><table  border=1 frame=hsides rules=rows bordercolor="#222225">'
                    
                    var dname = item[0]
                    for(var i = 0; i < references.length; i++) {
                        if (item[0].indexOf(references[i].item) >-1) { 
                            dname = '<a href="'+references[i].value+'">'+item[0]+'</a>'
                            break
                        }
                    }
                    
                    table+='<tr><td  class="table_cell_title" colspan="2" >'+dname+'</td></tr>';
                    var dadd = item[1]
                    table+='<tr><td  class="table_cell_title" colspan="2" style="font-size: 12px">0x'+(dadd.start_add).toString(16)+' - 0x'+(dadd.end_add).toString(16)+'</td></tr>';
                    $.each( item[2], function( att, value){
                        if (index == 'Last update') {
                            table+='<tr><td  class="table_cell_title2" style="font-size: 12px">&nbsp'+att+'</td><td  class="table_cell_value">'+value+'</td></tr>';                                       
                        }
                        else {
                            var a = parseInt(value);
                            var hexString = a.toString(16);

                            table+='<tr class="selectable"><td  class="table_cell_title2" style="font-size: 12px">&nbsp'+att+'</td><td  class="table_cell_value" contenteditable="true" onchange="sendCommand("fpga",this)">0x'+hexString+'</input></td></tr>';                                       
                        }
                        
                        
                    });
                    
                    content+= table;
                    content+='</td></table>'
                    
                    if (col>3) {
                        content += '</tr>'
                        col = 1
                    }
                    else {
                        col += 1
                    }
                });
            }
        });
        
        /* insert the html string*/
        $("#content").html( content );
        /*$("#data").html( data );*/
    }
    else
    {        
        var content='';
        var data ='No FPGA data found'
        
        var table = '<td style="vertical-align:top"><table  border=1 frame=hsides rules=rows bordercolor="#222225">'
        
        var references = []
        references.push({item: 'WB-HRMY-CROSSBAR', value:'/static/doc/hrmy_crossbar_block.html'})
        references.push({item: 'WB-HRMY-AVERAGE', value:'/static/doc/AVERAGE_block.html'})
        references.push({item: 'WB-HRMY-FIFO', value:'/static/doc/em2_FIFO_block.html'})
        references.push({item: 'WB-FMC-ADC-CORE', value:'/static/doc/fmc_adc_18b_400ks_csr.html'})
        references.push({item: 'WB-HRMY-MEMORY', value:'/static/doc/hrmy_mem_block.html'})
        references.push({item: 'WB-HRMY-ID-GEN', value:'/static/doc/ID_GEN_block.html'})
        references.push({item: 'WB-FMC-FV-CONTROL', value:'/static/doc/fmc_adc_18b_FV_Ctrl_csr.html'})
        references.push({item: 'SPI', value:'/static/doc/em2_spi_config_csr.html'})
        references.push({item: 'WB-EM2-DIGITAL_IO', value:'/static/doc/em2_digital_io_csr.html'})
        references.push({item: 'EM2_DAC', value:'/static/doc/em2_DAC_csr.html'})
        
        for(var i = 0; i < references.length; i++) {
            dname = '<a href="'+references[i].value+'">'+references[i].item+'</a>'
            table+='<tr><td  class="table_cell_title2" colspan="2" style="    text-align: center;">'+dname+'</td></tr>';
        }
        
        table+='</td></table>'                    
        
        /* insert the html string*/
        $("#content").html( table );
        /*$("#data").html( data );*/
    }
}
