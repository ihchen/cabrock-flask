$(document).ready(function() {
    // Modal gallery on click
    $(document).on('click', '[data-toggle="lightbox"]', function(event) {
        event.preventDefault();
        $(this).ekkoLightbox();
        // Hammer for mobile
        if(window.mobileAndTabletcheck) {
            var modal = document.getElementsByClassName('ekko-lightbox modal').item(0);
            var mc = new Hammer(modal);

            mc.on("swipeleft", function() {
                $('.ekko-lightbox-nav-overlay a:last-child').trigger('click');
            });
            mc.on("swiperight", function() {
                $('.ekko-lightbox-nav-overlay a:first-child').trigger('click');
            });

            $('.ekko-lightbox-nav-overlay a span').css('display', 'none');
        }
    })
    // Disable dragging of thumbnails
    $(document).on("dragstart", function(e) {
        if(e.target.nodeName.toUpperCase() == "A") {
            return false;
        }
    })
});
