$(document).ready(function(){
	$.ajaxSetup({ cache: false });
    $('input[name="academicYearTaught"]').mask('00-00');
});