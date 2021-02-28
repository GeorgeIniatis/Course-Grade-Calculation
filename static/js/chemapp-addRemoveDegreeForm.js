$(document).ready(function(){
	$.ajaxSetup({ cache: false });
    $('.degree-formset').formset({
        addText: 'Add',
        deleteText: 'Remove'
    });
});
