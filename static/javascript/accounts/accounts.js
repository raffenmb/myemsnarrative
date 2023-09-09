// static/javascript/accounts/user_account.js

// on user account page, switch between sidebar/menu views
function switch_view(view_id) {
	$(".account-content").css("display", "none");
	$("#" + view_id).css("display", "flex");
}

// on register page, toggle the submit button off disabled if user checks checkbox and vice versa
function switch_disable() {
	console.log('switched');
	var agreeCheckbox = document.getElementById("agree");
	var submitButton = document.getElementById("submit_btn");

	if (!agreeCheckbox.checked) {
		submitButton.disabled = true;
	} 
	else {
		submitButton.disabled = false;
	}
}