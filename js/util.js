//$(function() {
    /*-------------- Message Box -----------------*/
    function Init_MessageBox(){
        $('body').append('<div id="m_MessageBox" title="Message"></div>');
        $('#m_MessageBox').dialog({
            autoOpen: false,
            bgiframe: true,
            resizable: false,
            height:200,
            modal: true,
            overlay: {
                backgroundColor: '#000',
                opacity: 0.5
            },
            buttons: {
                'OK': function() {
                    $(this).dialog('close');
                }
            }
        });
    }
    function MessageBox( msg ){
        $('#m_MessageBox').text(msg);
        $('#m_MessageBox').dialog('open');
    }
    

    function Get_TodayStr(){
        var now = new Date();
        var y = now.getFullYear(); 
        var m = (now.getMonth()+1);
        var d = now.getDate();
        var str = '';
        str += y;
        str +=  '-' + ((m < 10)? '0'+m : m);
        str +=  '-' + ((d < 10)? '0'+d : d);
        return str;
    }
//})
