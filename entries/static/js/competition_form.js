$(document).ready(function() {
	var editing = $('h1#title').text() !== 'Add competition';

	// Deal with session visibility
	$('#session_group_2').hide(0);
	$('#session_group_3').hide(0);

	var currentSessionGroup = 1;

	if ($('#id_session_3_time').val() !== "" || $('#id_session_4_time').val() !== "") {
		currentSessionGroup = 2;

		$('#session_group_2').show(0);
	}

	if ($('#id_session_5_time').val() !== "" || $('#id_session_6_time').val() !== "") {
		currentSessionGroup = 3;

		$('#session_group_3').show(0);
		$('#add_sessions').remove();
	}

	// Add date pickers to relevant fields
	$('#id_session_1_time').datetimepicker({format: 'Y-m-d h:i:s'});
	$('#id_session_2_time').datetimepicker({format: 'Y-m-d h:i:s'});
	$('#id_session_3_time').datetimepicker({format: 'Y-m-d h:i:s'});
	$('#id_session_4_time').datetimepicker({format: 'Y-m-d h:i:s'});
	$('#id_session_5_time').datetimepicker({format: 'Y-m-d h:i:s'});
	$('#id_session_6_time').datetimepicker({format: 'Y-m-d h:i:s'});

	// Add more sessions on button click
	$('#add_sessions').on('click', function(e) {
		e.preventDefault();

		$('#session_group_' + ++currentSessionGroup).show(0);

		if (currentSessionGroup >= 3) {
			$(this).remove();
		}
	});

	// Set input fields to disabled if appropriate
	$('#id_novice_team_size').prop('disabled', !$('#id_has_novices').checked);
	$('#id_junior_team_size').prop('disabled', !$('#id_has_juniors').checked);

	// Enable/disable inputs when appropriate
	$('#id_has_novices').change(function(e) {
		$('#id_novice_team_size').prop('disabled', !this.checked);
	});
	$('#id_has_juniors').change(function(e) {
		$('#id_junior_team_size').prop('disabled', !this.checked);
	});
});