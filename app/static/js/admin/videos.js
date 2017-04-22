function createVideoFormContent(name='', url='') {
    var csrftoken = `<input type="hidden" name="csrf_token" value="`+csrf_token+`" />`;
    var inputName = `
        <div class="form-group">
            <label for="inputName">Name</label>
            <input id="inputName" type="text" class="form-input form-control" name="name" value="`+name+`"/>
        </div>
    `;
    var inputEmbed = `
        <div class="form-group required">
            <label for="inputEmbed">Embed URL</label>
            <input id="inputEmbed" type="text" class="form-input form-control" name="embedurl" value="`+url+`" required />
        </div>
    `;
    return csrftoken+inputName+inputEmbed;
}

function checkYoutubeEmbed(src) {
    return /youtube.com\/embed/.test(src);
}

$(document).ready(function() {
    $('.temp-iframe').each(function() {
        var src = $(this).data('src');
        if(checkYoutubeEmbed(src))
            $(this).replaceWith(`<iframe class="embed-responsive-item" src="`+src+`" allowfullscreen></iframe>`);
    });

    // Prep popovers
    $('[data-toggle="popover"]').popover();
    $('.video-admin .glyphicon-pencil').each(function() {
        var iframeContainer = $(this).parent('.video-admin').prev();
        var oldurl = iframeContainer.children('.temp-iframe').data('src')
                    || iframeContainer.children('iframe').attr('src');
        var form = `<form method="POST" action="`+editVideoURL+`">`+createVideoFormContent(
                        name=$(this).attr('data-title'),
                        url=oldurl
                    )+`<input type="hidden" name="oldurl" value="`+oldurl+`" />
                    <button type="submit" class="btn btn-primary edit-btn">Update</button></form>`;
        $(this).attr('data-content', form);
    })
    // Prep sortable
    createSortable('video-grid', '.video-item', '.glyphicon-move', 500, function(evt) {
        if(evt.oldIndex != evt.newIndex) {
            $.post({
                url: updateVideoOrderURL,
                data: {'oldIndex': evt.oldIndex, 'newIndex': evt.newIndex},
                success: function(return_data) {
                    ajaxSuccessAlert(return_data);
                }
            })
        }
    })
    // Add video
    $('.page-header .glyphicon-plus').on('click', function() {
        var modal = $('#admin-modal');
        var header = modal.find('.modal-header');
        var body = modal.find('.modal-body');
        var footer = modal.find('.modal-footer');

        var form = `<form id="addVideoForm" method="POST" action="`+addVideoURL+`">`+createVideoFormContent()+`</form>`;

        // Set Modal content
        header.html(`
            <button type="button" class="close" data-dismiss="modal" aria-label="Close">&times;</button>
            <h4>Add Video</h4>
        `);
        body.html(form);
        footer.html(`
            <button type="button" data-dismiss="modal" class="btn btn-default">Cancel</button>
            <button type="submit" form="addVideoForm" class="btn btn-primary">Submit</button>
        `);
    })
    // Delete video
    $('.video-admin .glyphicon-trash').on('click', function() {
        if(confirm('Are you sure you want to delete this video?')) {
            $.post({
                url: deleteVideoURL,
                data: {url: $(this).parent('.video-admin').prev().children('iframe').attr('src')},
                success: function(return_data) {
                    ajaxSuccessAlert(return_data);
                }
            })
            $(this).parents('.video-item').remove();
        }
    })
})
