/* Solves issues with images filling div's. Adds a img.wide or img.tall class to img element. */
$(window).load(function(){
 $('.container').find('img').each(function(){
  var imgClass = (this.width/this.height > 1) ? 'wide' : 'tall';
  $(this).addClass(imgClass);
 })
})