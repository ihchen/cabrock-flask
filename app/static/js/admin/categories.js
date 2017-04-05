$(document).ready(function() {
    $('.admin-page-buttons .glyphicon-pencil').on('click', function() {
        var modal = $('#admin-modal');
        var header = modal.find('.modal-header');
        var body = modal.find('.modal-body');
        var footer = modal.find('.modal-footer');

        // Set Modal content
        header.html(`
            <button type="button" class="close" data-dismiss="modal" aria-label="Close">&times;</button>
            <h4>Edit Category: "`+categoryName+`"</h4>
        `);
        body.html(`<form id="editCategoryForm" method="POST" action="`+editCategoryURL+`">`+createCategoryFormContents(
            name=categoryName,
            header=categoryHeader,
            description=categoryDescription,
            thumbsize=categoryThumbsize
        )+`<input type="hidden" value="`+categoryName+`" name="id" /></form>`); // Use old category name as id in case order switched around
        footer.html(`
            <button type="button" data-dismiss="modal" class="btn btn-default">Cancel</button>
            <button type="button" class="btn btn-primary" onclick="deleteCategoryWithAjax('`+categoryName+`')">Delete</button>
            <button type="submit" form="editCategoryForm" class="btn btn-primary">Submit</button>
        `);
    })
})
