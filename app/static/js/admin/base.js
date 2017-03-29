// id does not need # when passed
function createSortable(id, draggable, handle, animation, update_fn) {
    Sortable.create(document.getElementById(id), {
        draggable: draggable,
        handle: handle,
        animation: animation,
        onEnd: function(evt) {
            update_fn(evt);
        },
    })
}

function ajaxSuccessAlert(return_data) {
    var alert;
    if(return_data.success) {
        alert = $('.admin-alert.alert-success')[0];
    }
    else {
        alert = $('.admin-alert.alert-danger')[0];
        alert.innerHTML = '<a class="close" data-dismiss="alert">&times;</a>Update Unsuccessful: '+return_data.exception;
    }
    alert.style.display = "block";
    setTimeout(function() {
        alert.style.display = "none";
    }, 2000);
}

function createCategoryFormContents(name='', header='', description='', thumbsize=false) {
    var inputName = `
        <div class="form-group required">
            <label for="inputName">Category Name</label>
            <input id="inputName" type="text" class="form-input form-control" name="name" value="`+name+`" required />
        </div>
    `;
    var inputHeader = `
        <div class="form-group">
            <label for="inputHeader">Header</label>
            <input id="inputHeader" type="text" class="form-input form-control" name="header" value="`+header+`" />
        </div>
    `;
    var inputDescription = `
        <div class="form-group">
            <label for="inputDescription">Description</label>
            <textarea id="inputDescription" class="form-input form-control" name="description">`+description+`</textarea>
        </div>
    `;
    var inputThumbsize = `
        <div class="form-group">
            <label for="inputThumbsize">Use Large Thumbnails: </label>
            <input id="inputThumbsize" type="checkbox" class="checkbox-inline" name="thumbsize" value="large" `+(function(){if(thumbsize)return`checked`;})()+`/>
        </div>
    `;
    var hiddenURL = `<input type="hidden" name="currentURL" value="`+currentURL+`" />`;
    var form = inputName+inputHeader+inputDescription+inputThumbsize+hiddenURL;

    return form;
}

function deleteCategoryWithAjax(category) {
    if(confirm('Are you sure you want to delete the "'+categoryName+'" category?')) {
        $.post({
            url: deleteCategoryURL,
            data: {name: category, currentURL: currentURL},
            success: function(return_data) {
                if(return_data.redirect)
                    window.location.href = return_data.redirect;
                else
                    ajaxSuccessAlert(return_data);
            }
        })
        $('.admin.dropdown-item a').each(function() {
            if($(this).html() == category)
                $(this).parent('.admin').remove();
        })
    }
}

$(document).ready(function() {
    // Url needs to be set in the HTML before importing this script
    createSortable('painting-dropdown', '.dropdown-item', '.glyphicon-menu-hamburger', 150, function(evt) {
        if(evt.oldIndex != evt.newIndex) {
            $.post({
                url: updateCategoryOrderURL,
                data: {'oldIndex': evt.oldIndex, 'newIndex': evt.newIndex},
                success: function(return_data) {
                    ajaxSuccessAlert(return_data);
                }
            })
        }
    })
    // Add a new category
    $('.nav-item.admin .glyphicon-plus').click(function() {
        var modal = $('#admin-modal');
        var header = modal.find('.modal-header');
        var body = modal.find('.modal-body');
        var footer = modal.find('.modal-footer');

        // Set Modal content
        header.html(`
            <button type="button" class="close" data-dismiss="modal" aria-label="Close">&times;</button>
            <h4>Add New Category</h4>
        `);
        body.html(`<form id="addNewCategoryForm" method="POST" action="`+addNewCategoryURL+`">`+createCategoryFormContents()+`</form>`);
        footer.html(`
            <button type="button" data-dismiss="modal" class="btn btn-default">Cancel</button>
            <button type="submit" form="addNewCategoryForm" class="btn btn-primary">Submit</button>
        `);
    })
    // Delete Category
    $('.dropdown-item.admin .glyphicon-trash').click(function() {
        categoryName = $(this).prev('a').html();
        deleteCategoryWithAjax(categoryName);
    })
})
