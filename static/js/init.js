$(document).ready(function() {
						   
			$('.flexslider-top').flexslider({
			animation: "slide",
			slideshow: true,
			slideshowSpeed: 5000,
			animationSpeed: 600, 
			controlNav: false,
			prevText: 'Prev',
			nextText: 'Next',
			useCSS: false
									
									});		
			
				$('.flexslider-testimonials').flexslider({
			animation: "fade",
			slideshow: true,
			slideshowSpeed: 5000,
			animationSpeed: 600, 
			controlNav: false,
			prevText: 'Prev',
			nextText: 'Next',
			useCSS: false
									
									});	
			
			
	$(".gal-img a[data-rel^='prettyPhoto']").prettyPhoto({
						animation_speed: 'normal',
						autoplay_slideshow: true,
						slideshow: 3000
					});

	

$('.toggle_container').hide();
$('h4.trigger:first').addClass('active').next().show();

$('h4.trigger').click(function(){
  if( $(this).next().is(':hidden') ) {
  $('h4.trigger').removeClass('active').next().slideUp(); 
$(this).toggleClass('active').next().slideDown();
  } else {
   $('h4.trigger').removeClass('active').next().slideUp();
 }
  return false; 
 });			

 $('#tweets').tweet({
				modpath: 'twitter/',
				count: 3,
				username : 'flashuser',
				loading_text: 'loading tweets...'
	                         });
	
	});

