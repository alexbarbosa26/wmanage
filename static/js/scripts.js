$( document ).ready(function() {

    var filterBtn = $('#filter-btn');
    var filterForm = $('#filter-form');

    $(filterBtn).on('click', function() {
        filterForm.submit();
    });

    jQuery('form').preventDoubleSubmit();

    $('[data-toggle="tooltip"]').tooltip({boundary: 'window', delay:{"show":500, "hide":100}})
    
});