function CCacheMgr()
{
    this.cache         = cache;
    this.cacheJsonData = cacheJsonData;
    this.get           = get;
    this.clear         = clear;
    
    var m_cache_data = new Object();//cache dict
    
    function cmd2str(cmd)
    {
        cmd = SortDictByKeys(cmd);
        var param = [];
        for(var x in cmd)
            param[param.length] = x + "=" + cmd[x];
        
        var s = "";
        for(var i=0 ; i < param.length ; i++)
        {
            s += param[i];
            if(i < param.length-1)
                s += ',';
        }
        return s;
    }
    
    function cache(cmd, data)
    {
        m_cache_data[cmd2str(cmd)] = data;
    }
    
    function cacheJsonData(json_data)
    {
        var jdata = JSON.parse(json_data);
        var data = jdata['data'];
        cache(jdata['cmd'], data);
        return data;
    }
    
    function get(cmd)
    {
        return m_cache_data[cmd2str(cmd)];
    }
    
    function clear()
    {
        m_cache_data = new Object();
    }
}