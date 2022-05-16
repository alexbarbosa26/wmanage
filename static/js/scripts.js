$( document ).ready(function() {

    var filterBtn = $('#filter-btn');
    var filterForm = $('#filter-form');

    $(filterBtn).on('click', function() {
        filterForm.submit();
    });

    jQuery('form').preventDoubleSubmit();
    
});