$(document).ready(function() {

  // smooth scrolling
    $("a").click(function(event) {
      if (this.hash !== "") {
       event.preventDefault();
       var linkOffset = 0;
       $("html, body").animate({
         scrollTop: $(this.hash).offset().top - $(".navbar").height() + linkOffset
       }, 600);
      }
    });
    
    // Responsive Menu Toggle
    $('.user-link.responsive-toggle').on('click', function () {
        var menu = $('.responsive-profile-menu');
        menu.toggleClass('open');
    });

    // Tooltip Run
    $(function () {
        $('[data-toggle="tooltip"]').tooltip();
    });

});
