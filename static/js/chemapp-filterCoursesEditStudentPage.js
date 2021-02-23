 $(document).ready(function(){
	 $.ajaxSetup({ cache: false });
	 $("#id_academicPlan").change(function () {
		var url = $("#edit_student_form").attr("filter_courses_url");
		var degree = $(this).val();

		$.ajax({
			url: url,
			data: {
				'degree': degree
			},
			success: function (data) {
				$("#id_courses").html(data);
			}
		});
	});
 });
