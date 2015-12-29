(function($) {
  'use strict';

  $(function() {
    var $fullText = $('.admin-fullText');
    $('#admin-fullscreen').on('click', function() {
      $.AMUI.fullscreen.toggle();
    });

    $(document).on($.AMUI.fullscreen.raw.fullscreenchange, function() {
      $fullText.text($.AMUI.fullscreen.isFullscreen ? '退出全屏' : '开启全屏');
    });
  });
})(jQuery);


    formToJson = function(formObj) {
       var o = {};
       var a = formObj.serializeArray();
       $.each(a, function() {
           if(this.value){
               if (o[this.name]) {
                   if (!o[this.name].push) {
                       o[this.name]=[ o[this.name] ];
                   }
                       o[this.name].push(this.value || null);
               } else {
                       o[this.name]=this.value || null;
               }
           }
       });
       alert(JSON.stringify(o));
       return o;
    };