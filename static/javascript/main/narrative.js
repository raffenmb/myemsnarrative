// static/javascript/main/narrative.js

// variables from json scripts
var narrativePk = JSON.parse($("#narrative_pk").text());
var inputList = JSON.parse($("#input_list").text());

// other variables
var andor = "and";
var cursorPos = 0;

window.onload = function() {
	// open first input container
	open_input_box(Object.keys(inputList)[0]);

	// if user has no custom phrases, open available phrases in modal instead
	if ($("#empty_phrase_list_yours").length > 0) {
		$("#phrase_owner_ours").click();
	}
}

// toggle between ours and yours phrase list in modal
$('input[type=radio][name=phrase_owner]').change(function() {
	$("div[name=owner_list]").css("display", "none");
	$("#phrase_list_" + this.value).css("display", "flex");
	$("#phrase_list_search").focus();
});

// in a phrase box, substitute the user's input for the marker in the content
function add_to_phrase(input_id, phrase_id, marker, counter, last=false) {
	// replace the input marker with the user's response
	var phrase_content = $("#phrase_content_" + phrase_id).val();
	var response = $("#response_" + input_id).val();
	$("#phrase_content_" + phrase_id).val(phrase_content.replaceAll(marker, response));

	// hide the current input container and clear it
	$("#input_container_p_" + phrase_id + "_" + counter).css("display", "none");
	$("#input_container_p_" + phrase_id + "_" + counter).val("");

	// if there's another input container, open it and focus on the input box
	var next_counter = parseInt(counter) + 1;
	if ($("#input_container_p_" + phrase_id + "_" + next_counter).length) {
		$("#input_container_p_" + phrase_id + "_" + next_counter).css("display", "flex");
		$("#input_container_p_" + phrase_id + "_" + next_counter + " :input:first").focus();
	}

	// if it's the last container, submit it into the narrative
	if (last === true) {
		insert_phrase(phrase_id);
	}
}

// swap between and/or in input box
function change_andor(input_pk) {
	if (andor == "and") {
		andor = "or";
	}
	else {
		andor = "and";
	}
	update_user_response(input_pk);
}

// call functions selected by user in clean narrative modal
function clean_and_copy() {
	// find options selected by user to perform
	var checked_options = $("input[name=clean_up_choices]:checked");

	// create dictionary of checked options that's easier to use on Python side
	var to_execute = {"a_to_an": null, "pronouns": null, "remove_markers": null};
	for (var i=0; i < checked_options.length; i++) {
		var val = $(checked_options[i]).val();
		if (val == "a_to_an") {
			to_execute["a_to_an"] = true;
		}
		else if (val == "remove_markers") {
			to_execute["remove_markers"] = true;
		}
		else if (val == "pronouns") {
			var pronoun = $("#pronoun_choice").val();
			to_execute["pronouns"] = pronoun;
		}
	}

	// send the dictionary of checked options to the server side and receive the updated content
	$.ajax({
		type:"POST",
		url: "/clean-narrative/",
		data: {
			csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
			narrative_name: $("#narrative_name").val(),
			narrative_content: $("#narrative_content").val(),
			narrative_pk: narrativePk,
			input_list: JSON.stringify(inputList),
			to_execute: JSON.stringify(to_execute),
		},
		success: function(data) {
			var return_data = JSON.parse(data);

			// update narrative content in textarea 
			var new_content = return_data["content"];
			$("#narrative_content").val(new_content);

			// copy content to the clipboard
			navigator.clipboard.writeText(new_content);

			close_modal();
			display_message("Cleaned and copied narrative to clipboard")
		},
	});
}

// after saving option to an input, this adds a list item to the input box and selects it
function create_option_list_item(option, input_id) {
	// get index for new item's id
	var index = $("#narrative_options_" + input_id + " :input").length + 1;

	// create js element
	var option_input = $("<input type=checkbox name=options_" + input_id + " id=" + input_id + "_" + index + " hidden>");
	var option_label = $("<label class=narrative-option hover-shadow for=" + input_id + "_" + index + ">" + option + "</label>");
	
	// add value and onclick event to element
	option_input.val(option);
	option_input.attr("onClick", "update_user_response('" + input_id + "')");
	
	// append the checkbox label and input to the options list
	$("#narrative_options_" + input_id).append(option_input);
	$("#narrative_options_" + input_id).append(option_label);

	// check the new item so that it displays in the input box
	$("#" + input_id + "_" + index).prop("checked", true);
}

// delete the entire narrative
function delete_narrative(narrative_pk) {
	$("#delete_narrative").val(narrative_pk);
	submit_form();
}

// insert the phrase content into the narrative content at the current cursor position
function insert_phrase(phrase_id) {
	// create new string with content substring inserted at cursor position
	var content = $("#phrase_content_" + phrase_id).val();
	var txtarea = document.getElementById("narrative_content");
	var start = txtarea.selectionStart;
	var finish = txtarea.selectionEnd;
	var allText = txtarea.value;
	var scroll = txtarea.scrollTop;
	var sel = allText.substring(start, finish);
	var newText = allText.substring(0, start) + content + allText.substring(finish, allText.length);
	var caret = start + content.length;

	// insert new string into content and focus on it
	txtarea.value = newText;
	txtarea.focus();
	txtarea.setSelectionRange(caret, caret);
	txtarea.scrollTop = scroll;

	// close and save
	close_modal();
	save_narrative();

	// reset phrase box
	reset_phrase_box(phrase_id);
}

// open an input box by id, or the one following it
function open_input_box(input_id, next=false, remove=false) {
	// save original id
	var original_id = input_id;

	// get the next input box, and skip or remove the last one
	if (next) {
		// if there are more inputs left than what was just submitted/skipped
		if (Object.keys(inputList).length > 1) {
			// check if an input exists in the list after this one
			var nextIndex = Object.keys(inputList).indexOf(input_id)+1;
			var next_id = Object.keys(inputList)[nextIndex];
			// if one does exist
			if (next_id) {
				input_id = next_id;
				var input_box = $("#input_box_" + next_id);
			}
			// if not, go back to the first input
			else {
				input_id = Object.keys(inputList)[0];
				var input_box = $("#input_box_" + input_id);
			}
		}
		// otherwise, there's only one input left
		else if (Object.keys(inputList).length === 1) {
			input_id = Object.keys(inputList)[0];
			var input_box = $("#input_box_" + input_id);
		}

		// if user wants to remove the input altogether
		if (remove) {
			// if still in content, remove the marker from the content
			var new_content = $("#narrative_content").val().replaceAll(inputList[original_id]["marker"], "");
			$("#narrative_content").val(new_content);

			// remove the item's sidebar marker and modal
			delete inputList[original_id];
			$("#input_item_" + original_id).remove();

			// update changes to narrative and input_list on backend
			save_narrative();

			// if the last input was removed, hide the sidebar
			if (Object.keys(inputList).length <= 0) {
				// hide the sidebar
				$("#input_items_sidebar").empty();
				close_modal();
				return;
			}		
		}
	}
	// otherwise, get this input box
	else {
		var input_box = $("#input_box_" + input_id);
	}

	// open the input box and focus on the input field
	close_modal();
	input_box.css("display", "flex");
	$("#response_" + input_id).focus();
}

// open the phrase box from phrase list in modal
function open_phrase_box(phrase_id) {
	close_modal();

	// open the first input container
	$("#input_container_p_" + phrase_id + "_1").css("display", "flex");
	$("#phrase_box_" + phrase_id).css("display", "flex");

	// resize the content box to fit the text
	var content_el = document.getElementById("phrase_content_" + phrase_id);
	content_el.style.height = (content_el.scrollHeight) + "px";

	// focus on first input container
	$("#input_container_p_" + phrase_id + "_1 :input:first").focus();
}

// save cursor position and open phrase list modal
function open_phrase_list() {
	// save current cursor position
	var txtarea = document.getElementById("narrative_content");
	cursorPos = txtarea.selectionStart;

	// open phrase list modal and focus on selected field
	var modal = $("#phrases_list");
	modal.css("display", "flex");
	modal.find(".focus").focus();
}

// open modal to confirm user wants to save option from narrative page
function open_confirm_save_option(input_id) {
	// if the input field has a response in it, open modal
	if ($("#response_" + input_id).val()) {
		open_modal("input_save_option_" + input_id);
	}
	// otherwise, don't open modal and refocus on input field
	else {
		$("#response_" + input_id).focus();
	}
}

// remove any markers left over in narrative content and delete inputList
function remove_markers() {
	// remove all markers from narrative and replace it
	var narrative_content = $("#narrative_content").val();
	for (var id in inputList) {
		narrative_content = narrative_content.replaceAll(inputList[id]["marker"], "");
	}
	$("#narrative_content").val(narrative_content);

	// clear inputList and close any input container showing
	inputList = {};
	$(".narrative-input-container").css("display", "none");

	// remove input items sidebar
	$("#input_items_sidebar").empty();

	// save narrative to clear input list on DB side as well
	save_narrative();
	close_modal();
}

// clear all parts of a phrase box so it can be used again by user
function reset_phrase_box(phrase_id) {
	// reset the phrase content to the original
	var original_content = $("#original_p_content_" + phrase_id).val();
	$("#phrase_content_" + phrase_id).val(original_content);

	// uncheck the inputs that were clicked 
	var checkbox_inputs = $("#input_container_p_" + phrase_id + " :input[type=checkbox]:checked");
	for (var i=0; i < checkbox_inputs.length; i++) {
		$(checkbox_inputs[i]).prop("checked", false);
	}

	// clear the input textareas
	var input_textareas = $("#input_container_p_" + phrase_id + " :input[type=text]");
	for (var i=0; i < input_textareas.length; i++) {
		$(input_textareas[i]).val("");
	}

	// hide all input containers except first one
	$(".input-container-p").css("display", "none");
	$("#input_container_p_" + phrase_id + "_1").css("display", "flex");
}

// create and save a new option for an input with user's response in the current input box's input field
function save_option(input_id) {
	// get new option
	new_option = $("#response_" + input_id).val();

	// add new option to item in inputList on browser side before saving to server side
	inputList[input_id]["options"].push(new_option);

	// save option to backend
	$.ajax({
		type:"POST",
		url: "/save-option/",
		data: {
			csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
			input_id: input_id,
			new_option: new_option,
			narrative_name: $("#narrative_name").val(),
			narrative_content: $("#narrative_content").val(),
			narrative_pk: narrativePk,
			input_list: JSON.stringify(inputList),
		},
		success: function(data) {
			console.log("Saved option successfully.")
		},
	});

	// add item list button to modal 
	create_option_list_item(new_option, input_id);
	open_modal("input_box_" + input_id);
	$("#response_" + input_id).focus();

}

// save narrative to database and update inputList
function save_narrative(from_button=false) {
	// save content to DB
	$.ajax({
		type:"POST",
		url: "/save-narrative/",
		data: {
			csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
			narrative_name: $("#narrative_name").val(),
			narrative_content: $("#narrative_content").val(),
			narrative_pk: narrativePk,
			input_list: JSON.stringify(inputList),
		},
		success: function(data) {
			if (from_button) {
				display_message("Saved Narrative");
			}
		},
	});
}

// scroll narrative content to marker and flash where it is
function scroll_to_marker(marker) {
	// get index of marker in narrative content
	var textArea = document.getElementById("narrative_content");
	var start = textArea.value.indexOf(marker);
	var end = start + marker.length;
	textArea.focus();

	// scroll to marker
	const fullText = textArea.value;
	textArea.value = fullText.substring(0, end);
	textArea.scrollTop = textArea.scrollHeight;
	textArea.value = fullText;

	// focus on marker
	textArea.setSelectionRange(start, end);

	// after focusing on marker for split second, focus immediately after it in narrative content
	setTimeout(() => { textArea.setSelectionRange(end, end); }, 300);
}

// if response, add it to the narrative
function submit_input_response(input_id) {
	// get the user response and the input it relates to
	var response = $("#response_" + input_id).val();
	var input = inputList[input_id];

	// if there is a response, submit it
	if (response.length > 0) {
		// replace markers in the narrative with the response
		var new_content = $("#narrative_content").val().replaceAll(input["marker"], response);
		$("#narrative_content").val(new_content);

		// reset andor and move onto next question
		andor = "and";
		open_input_box(input_id, next=true, remove=true);
	}
	// otherwise, open skip or remove modal
	else {
		open_modal("input_skip_" + input_id);
	}
}

// if a user clicks an input's option, add it to the response input with proper grammar/syntax
function update_user_response(input_id) {
	var checked_options = $("input[name=options_" + input_id + "]:checked");
	var input_response = $("#response_" + input_id);
	var andor_btn = $("#andor_btn_" + input_id);
	var updated_response = "";

	for (var i=0; i < checked_options.length; i++) {
		// if there's only one option
		if (checked_options.length == 1) {
			updated_response = checked_options[i].value;
			andor_btn.css("display", "none");
			break;
		}
		// else there are multiple, prepend 'and' to last option
		else if (i == checked_options.length - 1) {
			updated_response += andor + " " + checked_options[i].value;
		}
		// if there are only two options add first option
		else if (checked_options.length == 2) {
			updated_response += checked_options[i].value + " ";
			andor_btn.css("display", "block");
		}
		// add comma to every other option
		else {
			updated_response += checked_options[i].value + ", ";
		}

	}

	// add updated response to the input and focus on it
	input_response.val(updated_response);
	input_response.focus();
}