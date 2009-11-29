function CCateSum(despt, sum)
{
    this.description = despt;
    this.sum = parseInt(sum);
}

function Analytics_SortCateSum(a,b)
{
    return b.sum - a.sum;//return -1,0,1
}


/* function CAnalytics()
{
    this.CateAddTrade = Analytics_CateAddTrade
}
 */

function Analytics_CateAddTrade(list, descpt, value)
{
    var i;
    for( i=0 ; i < list.length ; i++ ){
        if( list[i].description == descpt ){
            list[i].sum += value;
            break;
        }
    }
    if( i>=list.length ){
        list.push(new CCateSum(descpt, value));
    }
}

function RefreshAnalytics()
{
    var anal_arr = Array();
    var trs = $('#list_table tbody tr');
    for( var i=0 ; i< trs.length ; i++ )
    {
        var tr = trs.eq(i);
        var cate = tr.attr('category');
        var price = parseInt(tr.attr('price'));
        Analytics_CateAddTrade( anal_arr, cate, price );
    }
    
    //for( var i=0 ; i<anal_arr.length ; i++ ){
    //    alert( anal_arr[i].description + '\n'+ anal_arr[i].sum );
    //}
    anal_arr.sort( Analytics_SortCateSum );
    $('#analytics_table tbody td').remove();
    for( var i=0 ; i < anal_arr.length ; i++ ){
        $('#analytics_table tbody').append( '<tr description="'+anal_arr[i].description+'"><td>'+(i+1)+'</td><td>'+anal_arr[i].description+'</td><td>'+anal_arr[i].sum+'</td></tr>' );
    }
}