$(document).ready(function() {
    // Modal gallery on click
    $(document).on('click', '[data-toggle="lightbox"]', function(event) {
        event.preventDefault();
        $(this).ekkoLightbox();
    })
    // Disable dragging of thumbnails
    $(document).on("dragstart", function(e) {
        if(e.target.nodeName.toUpperCase() == "A") {
            return false;
        }
    })
});
