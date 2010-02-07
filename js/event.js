__CEventMgr_Actions = new Object();
function CEventMgr()
{
    this.bind    = bind;
    this.invoke  = invoke;
    
    function bind(msg, func)
    {
        if( msg in __CEventMgr_Actions ){
            __CEventMgr_Actions[msg].push(func)
        }
        else{
            __CEventMgr_Actions[msg] = new Array();
            __CEventMgr_Actions[msg].push(func);
        }
    }
    
    function invoke(msg)
    {
        func = __CEventMgr_Actions[msg];
        if( func ){
            for( var i=0 ; i<func.length ; i++ )
                func[i]();
        }
    }
}