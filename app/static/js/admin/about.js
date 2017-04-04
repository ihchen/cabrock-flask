function editAboutComponent(component, editBtn) {
    var saveBtn = editBtn.next();
    var content = editBtn.prev();

    //Swap buttons
    editBtn.addClass('hidden');
    saveBtn.removeClass('hidden');

    //Turn into input
    if(component == 'quotee') {
        content.html(`<input type="text" name="`+component+`" value="`+content.html()+`" />`);
    }
    else {
        content.html(`<textarea name="`+component+`">`+content.html()+`</textarea>`);
        autosize($('textarea'));
    }

    //On save click
    saveBtn.click(function() {
        var newContent = content.children().val();
        if(component == 'description') {
            newContent = newContent.replace(/[\r\n|\r|\n]+/g, '</p><p>');
            newContent = "<p>"+newContent+"</p>";
        }
        //Send ajax to update db
        $.post({
            url: updateAboutURL,
            data: {component: component, content: newContent},
            success: function(return_data) {
                ajaxSuccessAlert(return_data);
            }
        })

        //Update Page
        content.html(newContent);
        saveBtn.addClass('hidden');
        editBtn.removeClass('hidden');
    });
}

$(document).ready(function() {
    // Edit Quote
    $('blockquote.admin > .glyphicon-pencil').click(function() {
        editAboutComponent('quote', $(this));
    });
    // Edit Quotee
    $('footer.admin > .glyphicon-pencil').click(function() {
        editAboutComponent('quotee', $(this));
    });
    // Edit Description
    $('div.admin > .glyphicon-pencil').click(function() {
        editAboutComponent('description', $(this));
    });
})
