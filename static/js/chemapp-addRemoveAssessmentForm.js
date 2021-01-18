$(document).ready(function(){
	$.ajaxSetup({ cache: false });
    $('.assessment-formset').formset({
        addText: 'Add assessment',
        deleteText: 'Remove'
    });
});