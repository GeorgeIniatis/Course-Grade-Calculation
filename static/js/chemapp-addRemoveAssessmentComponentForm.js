$(document).ready(function(){
	$.ajaxSetup({ cache: false });
    $('.assessmentComponent-formset').formset({
        addText: 'Add',
        deleteText: 'Remove'
    });
});