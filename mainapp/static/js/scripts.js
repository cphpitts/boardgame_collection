$(document).ready(function() {

    var $header = $('header');
    var $sticky = $header.before($header.clone().addClass("sticky"));

    $(window).on("scroll", function(){
      var scrollFromTop = $(window).scrollTop();
      $("body").toggleClass("scroll", (scrollFromTop > 350));
    });

    // SMOOTH SCROLL

    $('.menu li a[href^="#"]').on('click', function(e){
      e.preventDefault();

      var target = $(this.hash);

      if (target.length) {
        $('html, body').stop().animate({
          scrollTop: target.offset().top -60
        }, 1000);
      }
    });

    // MASONRY

    $('.grid').masonry({
      // OPTIONS
      columnWidth: 120,
      itemSelector: '.grid-item',
      fitWidth: true,
      gutter: 1
    });

    // SLIDER

    $('.slider').slick({
      autoplay: true,
      autoplaySpeed: 1500,
      arrows: true,
      centerMode: true,
      prevArrow: '<button type="button" class="slick-prev"></button>',
      nextArrow: '<button type="button" class="slick-next"></button>',
      slidesToShow: 3
    });

});