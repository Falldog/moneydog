function CAnalytics()
{
    this.Refresh = Refresh;
    this.RefreshSummary = RefreshSummary;
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
    
    function __SumAddTradeByDay(list, date, value)
    {
        var d = parseInt(date.split('-')[2]) - 1;
        list[d] += value;
    }
    function __SumAddTradeByMonth(list, date, value)
    {
        var m = parseInt(date.split('-')[1]) - 1;
        list[m] += value;
    }
    function __SumAddTradeByYear(list, date, value, base_year)
    {
        var y = parseInt(date.split('-')[0]) - base_year;
        list[y] += value;
    }
    
    function Refresh(group)
    {
        if(!group) // type : year, month, day(default)
            group = 'day';
        
        var max = 0;
        var sum = 0;
        
        var anal_arr = Array();
        var trs = $('#list_table tbody tr');
        
        var sumOfResult = Array(0);
        var begin_y = 0;
        var end_y = 0;
        if(group == 'year' && trs.length>0)
        {
            item_first = trs.eq(0);
            item_last = trs.eq(trs.length-1);
            end_y = parseInt(item_first.attr('time').split('-')[0]);
            begin_y = parseInt(item_last.attr('time').split('-')[0]);
            if(begin_y==end_y)
                group = 'month';
        }
        
        if(group == 'year')
        {
            sumOfResult = Array(end_y-begin_y+1);
            for( var i=0 ; i<end_y-begin_y+1 ; i++ ) sumOfResult[i]=0;
            
            for( var i=0 ; i< trs.length ; i++ )
            {
                var tr = trs.eq(i);
                var cate = tr.attr('category');
                var price = parseInt(tr.attr('price'));
                __CategoryAddTrade( anal_arr, cate, price );
                __SumAddTradeByYear(sumOfResult, tr.attr('time'), price, begin_y);
                
                if( price > max ) max = price;
                sum += price;
            }
        }
        else if(group == 'month')
        {
            sumOfResult = Array(12);
            for( var i=0 ; i< 12 ; i++ ) sumOfResult[i]=0;
            
            for( var i=0 ; i< trs.length ; i++ )
            {
                var tr = trs.eq(i);
                var cate = tr.attr('category');
                var price = parseInt(tr.attr('price'));
                __CategoryAddTrade( anal_arr, cate, price );
                __SumAddTradeByMonth(sumOfResult, tr.attr('time'), price);
                
                if( price > max ) max = price;
                sum += price;
            }
        }
        else if(group == 'day')
        {
            sumOfResult = Array(31);
            for( var i=0 ; i< 31 ; i++ ) sumOfResult[i]=0;
            
            for( var i=0 ; i< trs.length ; i++ )
            {
                var tr = trs.eq(i);
                var cate = tr.attr('category');
                var price = parseInt(tr.attr('price'));
                __CategoryAddTrade( anal_arr, cate, price );
                __SumAddTradeByDay(sumOfResult, tr.attr('time'), price);
                
                if( price > max ) max = price;
                sum += price;
            }
        }

        
        //analytics_table
        anal_arr.sort( __SortCateSum );
        $('#analytics_table tbody tr').remove();
        for( var i=0 ; i < anal_arr.length ; i++ ){
            $('#analytics_table tbody').append( '<tr description="'+anal_arr[i].description+'" sum="'+anal_arr[i].sum+'"><td>'+(i+1)+'</td><td>'+anal_arr[i].description+'</td><td>'+IntAddComma(anal_arr[i].sum)+'</td></tr>' );
        }
        
        //analytics_sum_table
        $('#analytics_sum_table tbody tr').remove();
        $('#analytics_sum_table tbody').append( '<tr sum="'+sum+'" max="'+max+'"><td>總值</td><td>'+IntAddComma(sum)+'</td></tr>' );
        $('#analytics_sum_table tbody').append( '<tr sum="'+sum+'" max="'+max+'"><td>最大值</td><td>'+IntAddComma(max)+'</td></tr>' );
        
        __AssignCss();
        _Refresh_Chart(anal_arr, sum);
        if(group=='year')
            _Refresh_SumOfYearChart(sumOfResult, begin_y, end_y);
        else if(group=='month')
            _Refresh_SumOfMonthChart(sumOfResult);
        else
            _Refresh_SumOfDaysChart(sumOfResult);
    }

    function RefreshSummary(jdata)
    {
        var sum = 0;
        var max_month = 0;
        var anal_arr = Array();
        var sumOfMonth = Array(12);
        for( var i=0 ; i< 12 ; i++ ) sumOfMonth[i]=0;
        
        for( var m=0 ; m< jdata.length ; m++ )
        {
            var month = jdata[m];
            for( var i=0 ; i < month.length ; i++ )
            {
                var item = month[i];
                var cate = item[QJ_KEY_CATEGORY];
                var price = parseInt(item[QJ_KEY_PRICE]);
                __CategoryAddTrade( anal_arr, cate, price );
                sumOfMonth[m] += price;
            }
            if( sumOfMonth[m] > max_month ) max_month = sumOfMonth[m];
            sum += sumOfMonth[m];
        }
        
        //analytics_table
        anal_arr.sort( __SortCateSum );
        $('#analytics_table tbody tr').remove();
        for( var i=0 ; i < anal_arr.length ; i++ ){
            $('#analytics_table tbody').append( 
                '<tr description="'+anal_arr[i].description+'" sum="'+anal_arr[i].sum+'">'
                +'<td>'+(i+1)+'</td>'
                +'<td><div class="category_desc">'+anal_arr[i].description+'</div></td>'
                +'<td>'+IntAddComma(anal_arr[i].sum)+'</td></tr>' );
        }
        
        //analytics_sum_table
        $('#analytics_sum_table tbody tr').remove();
        $('#analytics_sum_table tbody').append( '<tr sum="'+sum+'" max="'+max_month+'"><td>總值</td><td>'+IntAddComma(sum)+'</td></tr>' );
        $('#analytics_sum_table tbody').append( '<tr sum="'+sum+'" max="'+max_month+'"><td>最大值</td><td>'+IntAddComma(max_month)+'</td></tr>' );
        
        __AssignCss();
        _Refresh_Chart(anal_arr, sum);
        _Refresh_SumOfMonthChart(sumOfMonth);
    }
    
    
    function _Refresh_Chart(anal_arr, sum)
    {
        //Refresh Analytics Chart via Google CHART APIs
        var data = [['Category', 'Money']];
        for( var i=0 ; i < anal_arr.length ; i++ )
        {
            data[i+1] = [anal_arr[i].description, anal_arr[i].sum];
        }
        
        var gdata = google.visualization.arrayToDataTable(data);
        var div = document.getElementById('analytics_chart_pie');
        var chart = new google.visualization.PieChart(div);
        var options = {
          title: 'Category Pie',
          width: 500,
          height: 250,
        };
        chart.draw(gdata, options);
    }
    
    function _Refresh_SumOfDaysChart(sumOfDays)
    {
        //Refresh Analytics BarChart via Google CHART APIs
        var max = MaxOfArray(sumOfDays);
        var data = [['Days', 'Money']];
        for(var i=0 ; i < sumOfDays.length ; i++)
            data[i+1] = [String(i+1), sumOfDays[i]];
        __Refresh_DrawChart('Sum of Days', data, max, 'Days', 10);
    }
    
    function _Refresh_SumOfMonthChart(sumOfMonth)
    {
        //Refresh Analytics BarChart via Google CHART APIs
        var max = MaxOfArray(sumOfMonth);
        var data = [['Month', 'Money']];
        for(var i=0 ; i < sumOfMonth.length ; i++)
            data[i+1] = [String(i+1), sumOfMonth[i]];
        __Refresh_DrawChart('Sum of Month', data, max, 'Month');
    }
    function _Refresh_SumOfYearChart(sumOfYear, begin_y, end_y)
    {
        //Refresh Analytics BarChart via Google CHART APIs
        var max = MaxOfArray(sumOfYear);
        var data = [['Year', 'Money']];
        for(var i=0 ; i < sumOfYear.length ; i++)
            data[i+1] = [String(begin_y+i), sumOfYear[i]];
        __Refresh_DrawChart('Sum of Year', data, max, 'Year');
    }
    
    function __Refresh_DrawChart(title, data, max, h_axis_title, bar_groupWidth)
    {
        var gdata = google.visualization.arrayToDataTable(data);
        var div = document.getElementById('analytics_chart_columnsum');
        var chart = new google.visualization.ColumnChart(div);
        var options = {
          title: title,
          width: 500,
          height: 250,
          hAxis: {
                  title: h_axis_title, 
                  titleTextStyle: {color: 'black'}, 
                 },
          vAxis: {
                  viewWindow: {'max':max}, 
                 },
        };
        if(bar_groupWidth)
            options['bar'] = {'groupWidth':bar_groupWidth};
        chart.draw(gdata, options);
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


