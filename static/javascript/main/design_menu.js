// static/javascript/main/design_menu.js

// toggle between ours and yours phrase list in copy modal
$('input[type=radio][name=phrase_owner]').change(function() {
	$("div[name=phrase_owner_list]").css("display", "none");
	$("#phrase_list_" + this.value).css("display", "flex");
	$("#phrase_list_search").focus();
});

// toggle between ours and yours template list in copy modal
$('input[type=radio][name=template_owner]').change(function() {
	$("div[name=template_owner_list]").css("display", "none");
	$("#template_list_" + this.value).css("display", "flex");
	$("#template_list_search").focus();
});

// submit form to copy a template or phrase on backend
function copy_textbox(textbox_type, textbox_pk) {
	$("#textbox_type").val(textbox_type);
	$("#textbox_pk").val(textbox_pk);
	$("#main_form").submit();
}

// submit form to create a blank template or phrase on backend
function create_textbox(textbox_type) {
	$("#textbox_type").val(textbox_type);
	$("#main_form").submit();
}