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
    
    function IsInt(n)
    {
        var intRegex = /^\d+$/;
        if(intRegex.test(n))
            return true;
        return false;
    }

    function IntAddComma(num)
    {
        if(!IsInt(num))
            return num;
            
        if( num < 1000 ) 
            return String(num);
        else{
            //calculate the number under 1000, plus the '0'
            n = num % 1000;//current num
            d = 100; //digital
            s = '';
            for( var i=0; i<3 ; i++){
                s += String(parseInt(n/d));
                n %= d;
                d /= 10;
            }
            return IntAddComma( parseInt(num/1000) ) + "," + s;
        }
    }
    
    function SortDictByKeys(dict)
    {
        var sorted = [];
        for(var key in dict) {
            sorted[sorted.length] = key;
        }
        sorted.sort();

        var tempDict = {};
        for(var i = 0; i < sorted.length; i++) {
            tempDict[sorted[i]] = dict[sorted[i]];
        }
        return tempDict;
    }
    
    //doesn't use the escape(), it will translate the chinese too.
    function ConverHTMLSymbol(s)
    {
        s = s.replace(/&/g, '%26');
        s = s.replace(/"/g, '%22');
        return s;
    }
    
    function MaxOfArray(l)
    {
        var _max = 0;
        for(var i=0 ; i < l.length ; i++)
            if( l[i] > _max )
                _max = l[i];
        return _max;
    }
    function MaxOfDict(d)
    {
        var _max = 0;
        for(var x in d)
            if( d[x] > _max )
                _max = d[x];
        return _max;
    }
//})
