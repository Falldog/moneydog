//Const
var QUERY_TYPE_OUT = 'out';
var QUERY_TYPE_IN  = 'in';
var QUERY_TYPE_CATEGORY_OUT = 'category_out';
var QUERY_TYPE_CATEGORY_IN  = 'category_in';
var QUERY_TYPE_SEARCH       = 'search';
var QUERY_TYPE_SUMMARY_OUT  = 'summary_out';
var QUERY_TYPE_SUMMARY_IN   = 'summary_in';

//Query result key from JSON
var QJ_KEY_KEY      = 'key';
var QJ_KEY_PRICE    = 'price';
var QJ_KEY_CATEGORY = 'category';
var QJ_KEY_DESC     = 'description';
var QJ_KEY_TIME     = 'date';

var MAX_ADD_NUM = 10;
var g_query_type = QUERY_TYPE_OUT;
var g_category = new Array();
var g_eventMgr = new CEventMgr();


//Class
function CCategory(key, description)
{
    this.key = key;
    this.description = description;
}

//Global function
function IsBrowseTrade()
{
    if(g_query_type==QUERY_TYPE_OUT || g_query_type==QUERY_TYPE_IN)
        return true;
    return false;
}

function IsBrowseCategory()
{
    if(g_query_type==QUERY_TYPE_CATEGORY_OUT || g_query_type==QUERY_TYPE_CATEGORY_IN)
        return true;
    return false;
}

function IsBrowseSummary()
{
    if(g_query_type==QUERY_TYPE_SUMMARY_OUT || g_query_type==QUERY_TYPE_SUMMARY_IN)
        return true;
    return false;
}

function AssignCategory2Select( select )
{
    select.children().remove();
    for(var i =0 ; i < g_category.length ; i++ ){
        var s = '<option value="'+g_category[i].key+'">'+g_category[i].description+'</option>';
        select.append(s);
    }
}

function Get_CategoryKey(desc){
    for( var i=0 ; i < g_category.length ; i++ ){
        if( g_category[i].description == desc )
            return g_category[i].key;
    }
    return '';
}

