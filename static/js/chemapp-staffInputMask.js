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
    $("#id_staffID").mask('0000000');
});