function CAddDialog()
{
    
    this.Initial               = Initial;
    this.onAddInsertFieldClick = onAddInsertFieldClick;
    this.RemoveAll             = RemoveAll;
    
    Initial();
    
    //********************************************************
    // Function declear
    //********************************************************
    function Initial()
    {
        $('#add_input_field').click( onAddInsertFieldClick );
        $('#dialog_add').dialog({
            autoOpen: false,
            bgiframe: true,
            resizable: false,
            height:600,
            width:800,
            modal: true,
            resizable: true,
            overlay: {
                backgroundColor: '#000',
                opacity: 0.5
            },
            buttons: {
                'Add':  onAddClick,
                Cancel: onCancelClick
            },
            close: function(event, ui) {
                $('#ui-datepicker-div').hide()
            }
        });
    }
    
    function RemoveAll(){
        $('#add_table thead tr').remove();
        $('#add_table tbody tr').remove();
    }
    function onAddComplete(){
        MessageBox('Success!!!');
        $('#dialog_add').dialog('close');
        RemoveAll();
        g_eventMgr.invoke('Refresh Page');
    }
    function onAddCallback(){
        var perc = 100.0 / $('#add_table tbody tr').length;
        var bar = $('#add_progressbar');
        var v = bar.progressbar('option', 'value');
        bar.progressbar('option', 'value', v+perc);
        
        if( bar.progressbar('option', 'value') > 99 )
            onAddComplete();
    }
    function onAddClick(){
        $('#add_progressbar').css('display', 'block');
        var trs = $('#add_table tbody tr');
        if( IsBrowseTrade() )
        {
            for( var i=0 ; i < trs.length ; i++ ){
                var tr = trs.eq(i);
                var cmd = '&item_price='      +tr.find('.add_price').val()+
                          '&item_description='+tr.find('.add_description').val()+
                          '&item_category_id='+tr.find('.add_category').attr('value')+
                          '&item_date='       +tr.find('.add_time').val();
                cmd = 'list_add?type=' + g_query_type + cmd;
                $.get( cmd, onAddCallback );
            }
        }
        else//Category In/Out
        {
            for( var i=0 ; i < trs.length ; i++ ){
                var tr = trs.eq(i);
                var cmd = '&item_description='+tr.find('.add_description').val();
                cmd = 'list_add?type=' + g_query_type + cmd;
                $.get( cmd, onAddCallback );
            }
        }
    }
    function onCancelClick(){
        $(this).dialog('close');
    }
    function onAddInsertFieldClick(){
        if( IsBrowseTrade() )
        {
            if( g_category.length == 0 ){
                MessageBox('﹟ゼ更Category!');
                return
            }
            
            var add_tr_len = $('#add_table tbody tr').length;
            if( add_tr_len >= MAX_ADD_NUM ){
                MessageBox('计秖笷! 单近!');
                return;
            }
            
            //$('#add_table').css('display','block');
            $('#add_table tbody').append( $("#add_example tbody").html() );
            var new_tr = $('#add_table tbody tr').eq(add_tr_len);
            AssignCategory2Select( new_tr.find('.add_category') );
            new_tr.find('.remove_add_filed').click( function(){
                                             $(this).parent().parent().remove();//Remove this <tr>
                                             });
            var new_tr_date = '';
            if( $('#add_table tbody tr').length > 1)
                new_tr_date = $('#add_table tbody tr').eq(add_tr_len-1).find('.add_time').val();
            else if( new_tr_date=='' ){
                new_tr_date = Get_TodayStr();
            }
            new_tr.find('.add_time').datepicker({ dateFormat: 'yy-mm-dd' })
                                    .val( new_tr_date );
        }
        else // Category In/Out
        {
            var add_tr_len = $('#add_table tbody tr').length;
            if( add_tr_len >= MAX_ADD_NUM ){
                MessageBox('计秖笷! 单近!');
                return;
            }
            $('#add_table tbody').append( $("#add_category_example tbody").html() );
            var new_tr = $('#add_table tbody tr').eq(add_tr_len);
            new_tr.find('.remove_add_filed').click( function(){
                                             $(this).parent().parent().remove();//Remove this <tr>
                                             });
            
        }
    }
        
}