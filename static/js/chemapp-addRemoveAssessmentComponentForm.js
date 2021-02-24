$(document).ready(function(){
	$.ajaxSetup({ cache: false });
    $('.assessmentComponent-formset').formset({
        addText: 'Add',
        deleteText: 'Remove'
    });

    $('#check_all').click(function(){
        $('input:checkbox').prop('checked',true);
    });

});