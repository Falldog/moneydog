/**
* jQuery.Alternate
* Copyright (c) 2009 Brian Campbell - brian(at)briancampbell(dot)name
* Licensed under GPLv3
* Date: Feb 12, 2009
*
* @projectDescription Set alternating styles to sibling elements 
* http://alternate.briancampbell.name
*
* @author Brian Campbell
* @version 1.1
*
* @param {odd, even, hover}
* odd : class name for odd (1st, 3rd, 5th etc.) elements (default = "odd")
* even : class name for even (2nd, 4th, 6th etc.) elements (default = "even")
* hover : boolean (default = false)
* @return {jQuery} Returns the same jQuery object, for chaining.
*
* @example $('#my_table tbody tr').alternate({},function(){$(this).toggleClass('selected')});
*
* @$('#my_list li').alternate({odd:'light', even:'dark'});
*
* @$('#my_list dd').alternate({hover:true});
*
* All the parameters are optional.
*
* @example css
* .odd {background-color:lightgray}
* .even {background-color:white}
* .hover {background-color:darkgray; font-style:bold}
*
*/

(function($){
    
    function __AssignTRClass(_this, opts, i){
        if(i % 2 == 0 && opts.even.length){
            _this.removeClass(opts.odd)
                 .addClass(opts.even);
        } else if(opts.odd.length){
            _this.removeClass(opts.even)
                 .addClass(opts.odd);
        };
    }
    
    $.fn.alternate = function(options, fnClick) {
    
        var opts = $.extend({}, $.fn.alternate.defaults, options);
        
        return this.each(function(i) {
            
            /* Support $.meta plugin */
            var $this = $(this), o = $.meta ? $.extend({}, opts, $this.data()) : opts;
            
            /* Alternate <tr> class */
            __AssignTRClass($this, opts, i);
            
            /* Add optional onclick behavior */
            if(fnClick){
                $this.click(fnClick);
            };
            
            /* Add optional "hover" class */
            if(opts.hover!=''){
                $this.bind('mouseenter', function(e){
                    $(this).toggleClass(opts.hover);
                    if( $this.hasClass(opts.odd)  ) $this.removeClass(opts.odd);
                    if( $this.hasClass(opts.even) ) $this.removeClass(opts.even);
                });
                $this.bind('mouseleave', function(e){
                    $(this).toggleClass(opts.hover);
                    __AssignTRClass($this, opts, i);
                });
            };

        });

    };
    
    /* Public */
    $.fn.alternate.defaults = {
        odd   : 'odd',
        even  : 'even',
        hover : ''
    };

})(jQuery);
