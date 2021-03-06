/*
Mask Usage
‘0’: {pattern: /\d/}
‘A’: {pattern: /[a-zA-Z0-9]/}
‘9’: {pattern: /\d/, optional: true}
‘S’: {pattern: /[a-zA-Z]/}
‘#’: {pattern: /\d/, recursive: true}
*/
$(document).ready(function(){
	$.ajaxSetup({ cache: false });
	$("#floatingCode").mask('SSSS_0000');
    $("#id_academicYearTaught").mask('00-00');
    $("#id_minimumPassGrade").mask('S0');
    $("#id_creditsWorth").mask('099');
    $("#id_minimumRequirementsForCredit").mask('0.09');
});