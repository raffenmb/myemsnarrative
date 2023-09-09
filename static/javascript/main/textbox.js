// static/javascript/main/textbox.js

// variables from json scripts
var tbType = $("#tb_type").val();
var textboxPk = JSON.parse($("#textbox_pk").text());
var inputList = JSON.parse($("#input_list").text());
var importList = JSON.parse($("#import_list").text());


// other variables
var cursorPos = 0;

window.onload = function() {
	// resize the phrase content box if content is larger than the textarea
	if (tbType === "Phrase") {
		var content_box = document.getElementById("textbox_content");
		content_box.style.height = content_box.scrollHeight + "px";
	}

	// if name is Untitled (as it is when created), show Untitled as a placeholder not text
	if ($("#textbox_name").val() == "Untitled") {
		$("#textbox_name").val("");
	}

	// if there is no name, focus on the name input
	if (!$("#textbox_name").val()) {
		$("#textbox_name").focus();
	}

	// if there are inputs, make them visible in the insert lists 
	if (Object.keys(inputList).length > 0) {
		$("#insert_input_list_filled").css("display", "flex");
		$("#insert_input_list_empty").css("display", "none");
	}

	// if there are import inputs, make them visible in the import list
	if (Object.keys(importList).length > 0) {
		$("#import_input_list_filled").css("display", "flex");
		$("#import_input_list_empty").css("display", "none");
	}
}

// add an option to the import options list for a certain input
function append_import_option(input_id, option_text) {
	var option_row = $("<li class='movable-list-item'></li>");
	option_row.text(option_text.trim());

	var btn_container = $("<div class='movable-item-btns'></div>");

	option_row.append(btn_container);
	$("#option_import_list_" + input_id).append(option_row);
}

// add an option to the options list for a certain input
function append_option(input_id, new_option=false) {
	// if this is called from the make_input_modal_copy() function
	if (new_option) {
		var option_text = new_option;
	}
	// otherwise this from modal, and need to check if enter button or "add" button were pressed
	else if (event.keyCode == 13 | event.composedPath()[0].tagName == "BUTTON") {
		var option_text = $("#option_input_" + input_id).val();
	}
	else {
		var option_text = false;
	}

	// if text is actually submitted, add option row to specified list
	if (option_text) {
		var option_row = $("<li class='movable-list-item'></li>");
		option_row.text(option_text.trim());

		var btn_container = $("<div class='movable-item-btns'></div>");
		var up_btn = $("<i class='fa-solid fa-angle-up' onclick='move_option_up(this)'></i>");
		var down_btn = $("<i class='fa-solid fa-angle-down' onclick='move_option_down(this)'></i>");
		var del_btn = $("<i class='fa-solid fa-xmark' onclick='delete_option(this)'></i>");

		btn_container.append(up_btn);
		btn_container.append(down_btn);
		btn_container.append(del_btn);
		option_row.append(btn_container);
		$("#option_list_" + input_id).append(option_row);

		$("#option_input_" + input_id).val("");
		$("#option_input_" + input_id).focus();
	}
}

// create an input from scratch, update the input lists, and create a new modal for it
function create_input() {
	if (validate_input("new")) {
		$.ajax({
			type:"POST",
			url: "/create-input/",
			data: {
				csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
				textbox_type: tbType, 
				textbox_pk: $("#textbox_pk").text(),
				textbox_name: $("#textbox_name").val(),
				textbox_content: $("#textbox_content").val(),
				input_name: $("#input_name_new").val(),
				input_options: get_options("option_list_new"),
			},
			success: function(returned_data) {
				var server_data = JSON.parse(returned_data);
				var new_input = $("#input_name_new").val();

				// update input variables
				inputList = server_data["input_list"];
				importList = server_data["import_list"];

				// update lists and create modal
				update_input_lists();
				make_input_modal_copy(new_input, inputList[new_input]);

				// clear new input modal and close it
				$("#input_name_new").val("");
				$("#option_list_new").empty();
				close_modal();

				// swap input lists off of empty text
				swap_input_list_content();
			},
		});
	}
}

// delete an input, update lists, and update content with deletion of markers
// only found in open_confirm_delete_input function on this page
function delete_input(input_id) {
	$.ajax({
		type:"POST",
		url: "/delete-input/",
		data: {
			csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
			input_pk: input_id,
			textbox_type: tbType, 
			textbox_pk: $("#textbox_pk").text(),
			textbox_name: $("#textbox_name").val(),
			textbox_content: $("#textbox_content").val(),
		},
		success: function(returned_data) {
			var server_data = JSON.parse(returned_data);

			// update input variables
			inputList = server_data["input_list"];
			importList = server_data["import_list"];

			// update lists and template content
			update_input_lists();
			$("#textbox_content").val(server_data["updated_content"]);

			// Create a modal for any import added without a modal
			for (var import_name in importList) {
				for (var i=0; i < importList[import_name].length; i++) {
					var import_data = importList[import_name][i];
					// if the modal doesn't exist, create one
					if (!$("#import_"+ import_data['pk']).length > 0) {
						make_import_modal_copy(import_name, import_data);
					}
				}
			}

			// swap to empty list displays if needed
			swap_input_list_content();

			// close modal and display message
			close_modal();
			display_message("Input Deleted");
		},
	});
}

// delete an input's option in the edit input modal
function delete_option(elem) {
	$(elem).parent().parent().remove();
}

// delete the entire textbox
function delete_textbox(textbox_pk) {
	$("#delete_textbox").val(textbox_pk);
	submit_form();
}

// View the template options for each import in the import list
function dropdown_imports(import_name) {
	var instance_list = $("#import_instances_" + import_name);
	if (instance_list.is(":visible")) {
		instance_list.css("display", "none");
	}
	else {
		instance_list.css("display", "flex");
	}
}

// get the list of options from the selected list
function get_options(el_id) {
	var children_list = $("#" + el_id).children();
	var options = [];
	for (let i = 0; i < children_list.length; i++) {
	  options.push($(children_list[i]).text().trim());
	}
	return JSON.stringify(options);
}

// import input into this textbox (only for template inputs right now)
function import_input(input_name, input_pk) {
	$.ajax({
		type:"POST",
		url: "/import-input/",
		data: {
			csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
			textbox_type: tbType, 
			textbox_pk: $("#textbox_pk").text(),
			textbox_name: $("#textbox_name").val(),
			textbox_content: $("#textbox_content").val(),
			input_pk: input_pk,
		},
		success: function(returned_data) {
			var server_data = JSON.parse(returned_data);

			// update input variables
			inputList = server_data["input_list"];
			importList = server_data["import_list"];

			// update lists and create modal
			update_input_lists();
			make_input_modal_copy(input_name, inputList[input_name]);

			// swap list displays if needed
			swap_input_list_content();

			close_modal();
			display_message("Input Imported");
		},
	});
}

// insert the input's marker into the narrative content at the current cursor position
function insert_input(marker) {
	// insert text at cursor's position
	var txtarea = document.getElementById("textbox_content");
	var start = txtarea.selectionStart;
	var finish = txtarea.selectionEnd;
	var allText = txtarea.value;
	var scroll = txtarea.scrollTop;
	var sel = allText.substring(start, finish);
	var newText = allText.substring(0, start) + marker + allText.substring(finish, allText.length);
	var caret = start + marker.length;

	txtarea.value = newText;
	txtarea.focus();
	txtarea.setSelectionRange(caret, caret);
	txtarea.scrollTop = scroll;

	// close and save
	close_modal();
	save_textbox();
}

// copy the generic new input modal and replace with specifics of an input
function make_input_modal_copy(name, input_data) {
	// get the copy modal html as a string and replace input-specific items
	var html_str = $("#input_INPUT_PK").prop("outerHTML");
	html_str = html_str.replaceAll("INPUT_PK", input_data["pk"]);
	html_str = html_str.replaceAll("INPUT_NAME", name);

	// convert back to html, add it to the DOM, and append any options from this input
	var new_modal = $(html_str);
	$("#input_INPUT_PK").after(new_modal);
	for (var i=0; i < input_data["options"].length; i++) {
		append_option(input_id=input_data["pk"], new_option=input_data["options"][i]);
	}
}

// copy the generic new input modal and replace with specifics of an input
function make_import_modal_copy(name, input_data) {
	// get the copy modal html as a string and replace input-specific items
	var html_str = $("#import_IMPORT_PK").prop("outerHTML");
	html_str = html_str.replaceAll("IMPORT_PK", input_data["pk"]);
	html_str = html_str.replaceAll("IMPORT_NAME", name);
	html_str = html_str.replaceAll("IMPORT_TEMPLATE", input_data['template']);

	// convert back to html, add it to the DOM, and append any options from this input
	var new_modal = $(html_str);
	$("#import_IMPORT_PK").after(new_modal);
	for (var i=0; i < input_data["options"].length; i++) {
		append_import_option(input_id=input_data["pk"], input_data['options'][i]);
	}
}

// move input's option down in its list of options
function move_option_down(elem) {
	var row = $(elem).parent().parent();
	var next = row.next();
	if (next.attr("class")) {
		row.insertAfter(next);
	}
}

// move input's option up in its list of options
function move_option_up(elem) {
	var row = $(elem).parent().parent();
	var prev = row.prev();
	if (prev.attr("class")) {
		row.insertBefore(prev);
	}
}

// open confirm delete modal for input
function open_confirm_delete_input(input_name) {
	var input_id = inputList[input_name]["pk"];
	$("#delete_input_text").text("Are you sure you want to delete this input?");
	$("#input_delete_yes_btn").attr("onclick", 'delete_input("' + input_id + '")');
	open_modal("confirm_delete_input");
}

// save cursor position and open input list modal
function open_input_list() {
	// save current cursor position
	var txtarea = document.getElementById("textbox_content");
	cursorPos = txtarea.selectionStart;

	// open input list modal and focus on selected field
	var modal = $("#insert_input_list");
	modal.css("display", "flex");
	modal.find(".focus").focus();
}

// save textbox to DB
function save_textbox(from_button=false) {
	$.ajax({
		type:"POST",
		url: "/save-textbox/",
		data: {
			csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
			textbox_type: tbType,
			textbox_name: $("#textbox_name").val(),
			textbox_content: $("#textbox_content").val(),
			textbox_pk: $("#textbox_pk").text(),
		},
		success: function(returned_data) {
			if (from_button) {
				display_message("Saved " + tbType);
			}
		},
	});

}

// swap input lists to empty list text if there are no items left
function swap_input_list_content() {
	// if there are insert input list items, make them visible
	if ( $('#insert_input_list_container').children().length > 0 ) {
		$("#insert_input_list_filled").css("display", "flex");
		$("#insert_input_list_empty").css("display", "none");    	
	}
	// otherwise, display empty list text
	else {
		$("#insert_input_list_filled").css("display", "none");
		$("#insert_input_list_empty").css("display", "block"); 
	}

	// if there is an import input list
	if (tbType === "Template") {
		// if there are import input list items, make them visible
		if ( $('#import_input_list_container').children().length > 0 ) {
			$("#import_input_list_filled").css("display", "flex");
			$("#import_input_list_empty").css("display", "none");    	
		}
		// otherwise, display empty list text
		else {
			$("#import_input_list_filled").css("display", "none");
			$("#import_input_list_empty").css("display", "block"); 
		}
	}
}

// update an existing input
function update_input(input_id, existing_name) {
	if (validate_input(input_id, existing_name)) {
		var new_name = $("#input_name_" + input_id).val();
		$.ajax({
			type:"POST",
			url: "/update-input/",
			data: {
				csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
				textbox_type: tbType, 
				textbox_pk: $("#textbox_pk").text(),
				textbox_name: $("#textbox_name").val(),
				textbox_content: $("#textbox_content").val(),
				input_pk: input_id,
				input_name: new_name,				
				input_options: get_options("option_list_" + input_id),
			},
			success: function(returned_data) {
				var server_data = JSON.parse(returned_data);

				// update input variables
				inputList = server_data["input_list"];
				importList = server_data["import_list"];

				// update lists, template content, update_input argument, and open_confirm_delete_input argument
				update_input_lists();
				$("#textbox_content").val(server_data["updated_content"]);
				$("#save_input_" + input_id).attr("onclick", "update_input('" + input_id + "','" + new_name + "')");
				$("#delete_input_" + input_id).attr("onclick", "open_confirm_delete_input('" + new_name + "')");

				open_modal("insert_input_list");
			},
		});
	}
}

// update input lists
function update_input_lists() {
	var insert_input_list = $("#insert_input_list_container");
	var import_input_list = $("#import_input_list_container");

	// empty the lists before refilling them with new items
	insert_input_list.empty();
	import_input_list.empty();

	// for each input in inputList variable, add it to the insert list
	for (var input in inputList) {
		var input_item = $("<div id='input_item_" + inputList[input]['pk'] + "' class='input-item hover-shadow'>");
		var input_text = $("<div class='input-item-text'>" + input + "</div>");
		input_text.attr("onclick", "insert_input('" + inputList[input]['marker'] + "')");
		var input_img = $("<img src='/static/media/edit.svg' class='view-icon hover-weight' title='Edit input'>");
		input_img.attr("onclick", "open_modal('input_" + inputList[input]['pk'] + "')");

		input_item.append(input_text);
		input_item.append(input_img);

		insert_input_list.append(input_item);
	}

	// for each input in importList variable, add it to the import list
	counter=1;
	for (var input_name in importList) {
		// if there are multiple instances of an import input
		if (importList[input_name].length > 1) {
			// create main list item with name of the input
			var input_item = $("<div class='list-item hover-shadow'>" + input_name + "<img src='/static/media/dropdown.svg'></div>")
			input_item.attr("onclick", "dropdown_imports(" + counter + ")");			

			// create the list container of each instance
			var instances_list = $("<div id='import_instances_" + counter + "' class='import-instances-list' style='display:none;'></div>");
			var list_header = $("<div class='text-s margin-xs'>Template Options</div>");
			instances_list.append(list_header);

			// create each instance and add it to the list container
			for (var i=0; i < importList[input_name].length; i++) {
				var instance_item = $("<div class='list-item hover-shadow'>" + importList[input_name][i]['template'] + "</div>");
				instance_item.attr("onclick", "open_modal('import_" + importList[input_name][i]['pk'] + "')");
				instances_list.append(instance_item);
			}

			// add the list container after the main list item
			input_item = input_item.add(instances_list); 
		}
		// otherwise there is only one instance of the input
		else {
			var input_item = $("<div class='list-item hover-shadow'>" + input_name + "</div>");
			input_item.attr("onclick", "open_modal('import_" + importList[input_name][0]['pk'] + "')");
		}

		// add input item to the overall import list
		import_input_list.append(input_item);
		counter += 1;
	}
}

// make sure the input has a name and the name isn't a duplicate
function validate_input(input_id, original_name=false) {
	// if new input name is blank
	if (!$("#input_name_" + input_id).val()) {
		$("#invalid_input_name_" + input_id).text("Input name cannot be left blank.");
		$("#invalid_input_name_" + input_id).css("display", "flex");
		setTimeout(function(){
			$("#invalid_input_name_" + input_id).text("");
			$("#invalid_input_name_" + input_id).css("display", "none");
		}, 4000);
		return false;
	}

	// if it's an existing input with no change in name, it's validated
	if ($("#input_name_" + input_id).val() === original_name) {
		return true;
	}
	// otherwise make sure it hasn't changed to an existing name
	else if (Object.keys(inputList).includes($("#input_name_" + input_id).val())) {
		$("#invalid_input_name_" + input_id).text("Input name already exists.");
		$("#invalid_input_name_" + input_id).css("display", "flex");
		setTimeout(function(){
			$("#invalid_input_name_" + input_id).text("");
			$("#invalid_input_name_" + input_id).css("display", "none");
		}, 4000);
		return false;
	}

	// otherwise it's a new input and it's validated
	return true;
}