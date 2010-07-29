function CAnalytics()
{
    this.Refresh = Refresh;
    this.Show    = Show;
    this.Hide    = Hide;
    
    //********************************************************
    // Function declear
    //********************************************************
    function Show()
    {
        $('#analytics_list').show();
    }
    function Hide()
    {
        $('#analytics_list').hide();
    }
    
    function __CCateSum(despt, sum)
    {
        this.description = despt;
        this.sum = parseInt(sum);
    }
    
    function __SortCateSum(a,b)
    {
        return b.sum - a.sum;//return -1,0,1
    }
    
    
    function __CategoryAddTrade(list, descpt, value)
    {
        var i;
        for( i=0 ; i < list.length ; i++ ){
            if( list[i].description == descpt ){
                list[i].sum += value;
                break;
            }
        }
        if( i>=list.length ){
            list.push(new __CCateSum(descpt, value));
        }
    }

    function Refresh()
    {
        var max = 0;
        var sum = 0;
        
        var anal_arr = Array();
        var trs = $('#list_table tbody tr');
        for( var i=0 ; i< trs.length ; i++ )
        {
            var tr = trs.eq(i);
            var cate = tr.attr('category');
            var price = parseInt(tr.attr('price'));
            __CategoryAddTrade( anal_arr, cate, price );
            
            if( price > max ) max = price;
            sum += price;
        }
        
        //analytics_table
        anal_arr.sort( __SortCateSum );
        $('#analytics_table tbody tr').remove();
        for( var i=0 ; i < anal_arr.length ; i++ ){
            $('#analytics_table tbody').append( '<tr description="'+anal_arr[i].description+'" sum="'+anal_arr[i].sum+'"><td>'+(i+1)+'</td><td>'+anal_arr[i].description+'</td><td>'+IntAddComma(anal_arr[i].sum)+'</td></tr>' );
        }
        
        //analytics_sum_table
        $('#analytics_sum_table tbody tr').remove();
        $('#analytics_sum_table tbody').append( '<tr sum="'+sum+'" max="'+max+'"><td>總值  </td><td>'+IntAddComma(sum)+'</td></tr>' );
        $('#analytics_sum_table tbody').append( '<tr sum="'+sum+'" max="'+max+'"><td>最大值</td><td>'+IntAddComma(max)+'</td></tr>' );
        
        __AssignCss();
        _Refresh_Chart(anal_arr, sum);
    }
    
    function _Refresh_Chart(anal_arr, sum)
    {
        //Refresh Analytics Chart via Google CHART APIs
        url = 'http://chart.apis.google.com/chart?';
        url += 'cht=p3'; //3D
        url += '&chs=500x150'; //size
        url += '&chco=3366CC'; //color
        detail = '&chd=t:'; // Ex: chd=t:30,10,60
        descript = '&chl='; //Ex: chl=Test|Type|Income
        for( var i=0 ; i < anal_arr.length ; i++ )
        {
            perc = parseInt(anal_arr[i].sum/sum*100);
            detail += perc
            descript += (anal_arr[i].description + ' ('+perc+'%)');
            if(i!=anal_arr.length-1){
                detail += ',';
                descript += '|';
            }
        }
        url += detail;
        url += descript;
        $('#img_analytics_chart').attr('src', url);
    }
    
    
    function __AssignCss()
    {
        //analytics_table
        $('#analytics_table tbody tr').alternate({odd:'ListTableTH_odd', even:'ListTableTH_even', hover:'ListTableTH_hover'});
        $('#analytics_table thead tr').addClass('ListTableTH_header');
        $('#analytics_table tbody tr').each( function(i){
            $(this).children().eq(0).addClass('AnalyticsTable_index');
            $(this).children().eq(1).addClass('AnalyticsTable_category');
            $(this).children().eq(2).addClass('AnalyticsTable_price');
        });
        
        //analytics_sum_table
        $('#analytics_sum_table tbody tr').alternate({odd:'ListTableTH_odd', even:'ListTableTH_even', hover:'ListTableTH_hover'});
        $('#analytics_sum_table thead tr').addClass('ListTableTH_header');
        $('#analytics_sum_table tbody tr').each( function(i){
            $(this).children().eq(0).addClass('AnalyticsTable_type');
            $(this).children().eq(1).addClass('AnalyticsTable_value');
        });
        
    }
}


