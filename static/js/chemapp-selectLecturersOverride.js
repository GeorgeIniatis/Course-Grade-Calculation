 $(document).ready(function(){
	 $.ajaxSetup({ cache: false });
	 $("#id_lecturers").mousedown(function(e){
        e.preventDefault();

        var select = this;
        var scroll = select .scrollTop;

        e.target.selected = !e.target.selected;

        setTimeout(function(){select.scrollTop = scroll;}, 0);

        $(select ).focus();

	}).mousemove(function(e){e.preventDefault()});
 });
