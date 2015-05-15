$(document).ready(function(){
  $('.thumbnail').hover(function() {
    $(this).find('.battle').show();
  }, function() {
    $(this).find('.battle').hide();
  });
});
