// static/javascript/global.js

// displays any messages when page loads
$(document).ready(function() {
  var msg_container = $("#message_container");
  // display the message only for 2 seconds
  if (msg_container) {
	msg_container.css("display", "flex");
	setTimeout(function(){
	  msg_container.css("display", "none");
	}, 4000);
  }
})

// clear the search bar of text and focus on it
function clear_search(el) {
  var search_bar = $(el).prev();
  // clear the input and focus on it
  search_bar.val("");
  search_bar.focus();
  // trigger the onkeyup function so the list can be reset
  search_bar.keyup();
}

// close a specific modal or all modals if not specified
function close_modal(el_id=null) {
  // close specific modal only
  if (el_id) {
	$("#" + el_id).css("display", "none");
  }
  // close all modals visible
  else {
	$(".modal").css("display", "none");
  }
}

// display a message at the top of the screen
function display_message(msg, tag="success") {
  var message_container = $("#message_container");
  var message = $(document.createElement('div'))
	.addClass('message')
	.text(msg);

  message_container.append(message);

  // only display the message for 2 seconds and then clear it
  message_container.css("display", "flex");
  setTimeout(function(){
	message_container.css("display", "none");
	message_container.empty();
  }, 2000);
}

// limit list below the search field to items matching the text in the search field
function filter_search(input_id, list_name) {
  // get the user's input in lowercase and the list of items to filter
  var user_input = $(input_id).val().toLowerCase();
  var list_of_items = $('div[name=' + list_name +']').children();

  // hide display of items that the user's input can't be found in
  for (i=0; i < list_of_items.length; i++) {
	var item = $(list_of_items[i]);
	var item_name = item.text().toLowerCase();
	if (item_name.indexOf(user_input) > -1) {
	  item.css('display', 'flex');
	} else {
	  item.css('display', 'none');
	}
  }
}

// open a specific modal and close all others
function open_modal(el_id) {
  // close other modals
  $(".modal").hide();

  // open the modal
  var modal = $("#" + el_id);
  modal.css("display", "flex");

  // focus on the field designated by the class focus
  modal.find(".focus").focus();
}

// grow or shrink the textarea based on the amount of text inside
function resize_textarea(el, narrative=false) {
	if (narrative === true && el.scrollHeight > 115) {
		el.style.height = "116px";
	}
	else {
		el.style.height = 0;
		el.style.height = (el.scrollHeight) + "px";
	}
};

// submit a form, default id is main_form
function submit_form(form_id="main_form") {
  $("#" + form_id).submit();
}