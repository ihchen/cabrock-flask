$(document).ready(function() {
    // Upload Image (create form on modal)
    $('.admin-page-buttons .glyphicon-plus').click(function() {
        var modal = $('#admin-modal');
        var header = modal.find('.modal-header');
        var body = modal.find('.modal-body');
        var footer = modal.find('.modal-footer');

        // Form elements
        var inputTitle = `
            <div class="form-group required">
                <label for="inputTitle">Title</label>
                <input id="inputTitle" type="text" class="form-input form-control" name="name" required />
            </div>
        `;
        var inputCategory = `
            <div class="form-group">
                <label for="inputCategory">Category</label><br />
                <select id="inputCategory" name="category">
                    <option value=''>---------</option>`+
                    (function() {
                        var categoryOptions = ``;
                        categoryList.forEach(function(item) {
                            if(item == currentCategory)
                                categoryOptions += `<option selected="selected">`+item+`</option>`;
                            else
                                categoryOptions += `<option>`+item+`</option>`;
                        })
                        return categoryOptions;
                    })()
                    +`
                </select>
            </div>
        `;
        var inputMedium = `
            <div class="form-group">
                <label for="inputMedium">Medium</label>
                <input id="inputMedium" type="text" class="form-input form-control" name="medium" />
            </div>
        `;
        var inputDimensions = `
            <div class="form-group">
                <label for="inputDimensions">Dimensions</label>
                <input id="inputDimensions" type="text" class="form-input form-control" name="dimensions" />
            </div>
        `;
        var inputYear = `
            <div class="form-group">
                <label for="inputYear">Year</label>
                <input id="inputYear" type="text" class="form-input form-control" name="year" />
            </div>
        `;
        var inputImage = `
            <div class="form-group required">
                <label for="inputImage">Image File</label>
                <input id="inputImage" type="file" name="file" required />
                <p class="help-block">.jpg files only</p>
            </div>
        `;
        var hiddenURL = `<input type="hidden" name="currentURL" value="`+currentURL+`" />`;
        var form = `<form id="uploadPaintingForm" method="POST" action="`+uploadPaintingURL+`" enctype="multipart/form-data">`+inputTitle+inputCategory+inputMedium+inputDimensions+inputYear+inputImage+hiddenURL+`</form>`;

        // Set Modal content
        header.html(`
            <button type="button" class="close" data-dismiss="modal" aria-label="Close">&times;</button>
            <h4>Upload Painting</h4>
        `);
        body.html(form);
        footer.html(`
            <button type="button" data-dismiss="modal" class="btn btn-default">Cancel</button>
            <button type="submit" form="uploadPaintingForm" class="btn btn-primary">Upload</button>
        `);
    })

    // Sort Image. URL needs to be set in HTML before this script is uploaded
    createSortable('image-grid', '.image-item', '.glyphicon-move', 500, function(evt) {
        if(evt.oldIndex != evt.newIndex) {
            $.post({
                url: updatePaintingOrderURL,
                data: {oldIndex: evt.oldIndex, newIndex: evt.newIndex},
                success: function(return_data) {
                    ajaxSuccessAlert(return_data);
                }
            })
        }
    })

    // Edit Image
    $('.image-admin .glyphicon-pencil').click(function() {
        var editBtn = $(this);
        var saveBtn = $(this).next('.glyphicon-floppy-disk');

        var thumbnail = editBtn.parent('.image-admin').prev('a');
        var uniqueID = thumbnail.attr('data-id');   // Using filepath because id will get switched around if sorting done
        // Get caption info
        var caption = thumbnail.children('.caption');
        var captionTitle = caption.children('.caption-title');
        var captionDetails = caption.children('.caption-detail');

        //Replace edit button with save button
        editBtn.addClass('hidden');
        saveBtn.removeClass('hidden');

        // Disable hover functionality and keep details displayed
        thumbnail.removeClass('hover');
        caption.css('opacity', '1')
        // Prevent thumbnail from opening modal on click
        thumbnail.attr('data-toggle', 'offbox');    // Prevent modal from opening
        thumbnail.click(function(evt) {     // Prevent link from taking you to image
            evt.preventDefault();
        })

        // Change info to inputs
        captionTitle.html('<input type="text" name="title" value="'+captionTitle.html()+'" />');
        captionDetails.children('.detail-item').each(function() {
            $(this).html('<textarea type="text" name="'+$(this).attr('data-type')+'" placeholder="'+$(this).attr('data-type')+'" rows="0">'+$(this).html().replace(/"/g, '&quot;')+'</textarea>');
        })

        // Save changes
        saveBtn.click(function() {
            // Get updated information
            details = {
                filename: uniqueID,
                name: captionTitle.children('input').val(),
            }
            captionDetails.children('.detail-item').children('textarea').each(function() {
                details[$(this).attr('name')] = $(this).val();
            })

            // Send ajax post request to update database
            $.post({
                url: updatePaintingDetailsURL,
                data: details,
                success: function(return_data) {
                    ajaxSuccessAlert(return_data);
                }
            })

            // Update page
            captionTitle.html(details.name)
            captionDetails.children('.detail-item').each(function() {
                $(this).html(details[$(this).attr('data-type')]);
            })
            newFooter = ""
            if(details.medium != "") newFooter += details.medium;
            if(details.dimensions != "") newFooter += "<br />"+details.dimensions;
            if(details.year != "") newFooter += "<br />"+details.year;
            thumbnail.attr('data-title', details.name)
            thumbnail.attr('data-footer', newFooter);

            // Revert functionality back to default
            editBtn.removeClass('hidden')
            saveBtn.addClass('hidden')

            thumbnail.addClass('hover');
            caption.removeAttr('style');
            thumbnail.attr('data-toggle', 'lightbox');
        })
    })

    // Delete Image
    $('.image-admin .glyphicon-trash').click(function() {
        var thumbnail = $(this).parent('.image-admin').prev('a');
        var uniqueID = thumbnail.attr('data-id');   //Uses filename as unique id
        var name = thumbnail.attr('data-title');

        if(confirm('Are you sure you want to delete "'+name+'"?')) {
            // Send ajax request to delete item from database
            $.post({
                url: deletePaintingURL,
                data: {filename: uniqueID},
                success: function(return_data) {
                    ajaxSuccessAlert(return_data);
                }
            })
            // Update page
            thumbnail.parent('.image-item').remove();
        }
    })
})
