# main/views.py

from django.db.models.functions import Lower
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
import json, pprint

from main.models import (
	Phrase, Template, 
	InputP, InputT, Narrative)

from accounts.models import CustomUser

from main import functions as fx
from myemsnarrative import settings


#----------------------------------------------------------------------------------------------------------------------------------------------
#
# WELCOME VIEWS
#
#----------------------------------------------------------------------------------------------------------------------------------------------


def welcome_view(request):
	context = {'owner': request.user}

	return render(request, 'main/welcome.html', context)


@login_required
def acknowledgment_view(request):
	context = {
		'owner': request.user,
		}

	if request.POST:
		return redirect('main:home')

	return render(request, 'misc/acknowledgment.html', context)


@login_required
def home_view(request):
	context = {
		'owner': request.user,
		'template_list': Template.objects.filter(user=request.user).order_by(Lower("name")),
		}

	return render(request, 'main/home.html', context)


@login_required
def design_menu_view(request):
	if request.POST:
		post = request.POST
		if post['textbox_type'] == 'phrase':
			# create a new blank phrase
			new_phrase = Phrase(user=request.user, name="Untitled", content="")
			new_phrase.save()
			# copy the content of another phrase if there's a pk to copy
			if post['textbox_pk']:
				new_phrase.copy(to_copy=Phrase.objects.get(pk=int(post["textbox_pk"])))
			# redirect to the new phrase's page
			return redirect('main:phrase', pk=new_phrase.pk)
		elif post['textbox_type'] == 'template':
			# create a new blank template
			new_template = Template(user=request.user, name="Untitled", content="")
			new_template.save()
			# copy the content of another template if there's a pk to copy
			if post['textbox_pk']:
				new_template.copy(to_copy=Template.objects.get(pk=int(post["textbox_pk"])))
			# redirect to the new template's page
			return redirect('main:template', pk=new_template.pk)

	context = {
		'owner': request.user,
		'templates': Template.objects.filter(user=request.user).order_by(Lower("name")),
		'phrases': Phrase.objects.filter(user=request.user).order_by(Lower("name")),
		'our_templates': Template.objects.filter(for_all=True).order_by(Lower("name")),
		'our_phrases': Phrase.objects.filter(for_all=True).order_by(Lower("name")),
	}

	return render(request, 'main/design_menu.html', context)


#----------------------------------------------------------------------------------------------------------------------------------------------
#
# TEXTBOX VIEWS
#
#----------------------------------------------------------------------------------------------------------------------------------------------


@login_required
def template_view(request, pk):
	template = Template.objects.get(pk=pk)

	if request.POST:
		post = request.POST
		if post['delete_textbox']:
			temp_to_delete = Template.objects.get(pk=int(post['delete_textbox']))
			temp_to_delete.delete()
			return redirect('main:design_menu')

	context = {
		'owner': template.user,
		'template': template,
		'input_list': template.textbox_input_list(),
		'import_list': template.textbox_import_list(),
		}

	return render(request, 'main/template.html', context)


@login_required
def phrase_view(request, pk):
	phrase = Phrase.objects.get(pk=pk)

	if request.POST:
		post = request.POST
		if post['delete_textbox']:
			phrase_to_delete = Phrase.objects.get(pk=int(post['delete_textbox']))
			phrase_to_delete.delete()
			return redirect('main:design_menu')

	context = {
		'owner': phrase.user,
		'phrase': phrase,
		'input_list': phrase.textbox_input_list(),
		'import_list': phrase.textbox_import_list(),
		}

	return render(request, 'main/phrase.html', context)


#----------------------------------------------------------------------------------------------------------------------------------------------
#
# TEXTBOX AJAX VIEWS
#
#----------------------------------------------------------------------------------------------------------------------------------------------


# saves template, but only called when user hits Save button on textbox page
@login_required
def save_textbox_view(request):
	if request.POST:
		post = request.POST

		fx.save_textbox(post)

		return HttpResponse("Successfully saved textbox.")
	else:
		return HttpResponse("Didn't receive a POST request.")


# create an input for a textbox and save the input and textbox
@login_required
def create_input_view(request):
	if request.POST:
		post = request.POST

		# save and get textbox for this input
		textbox = fx.save_textbox(post)

		# create input and save it
		if post["textbox_type"] == "Template":
			new_input = InputT(
				user=request.user, 
				template=textbox,
				name=post["input_name"],
				options=post["input_options"],
			)
		elif post["textbox_type"] == "Phrase":
			new_input = InputP(
				user=request.user, 
				phrase=textbox,
				name=post["input_name"],
				options=post["input_options"],
			)
		new_input.save()

		# return the updated input lists
		return_data = {
			"input_list": textbox.textbox_input_list(),
			"import_list": textbox.textbox_import_list(),
		}

		return HttpResponse(json.dumps(return_data))
	else:
		return HttpResponse("Didn't receive a POST request.")


# update an existing input and update markers in content (if changed)
@login_required
def update_input_view(request):
	if request.POST:
		post = request.POST

		# get input and update it
		if post["textbox_type"] == "Template": 
			inpt = InputT.objects.get(pk=int(post["input_pk"]))
			old_marker = inpt.marker()
			textbox = inpt.template
		elif post["textbox_type"] == "Phrase":
			inpt = InputP.objects.get(pk=int(post["input_pk"]))
			old_marker = inpt.marker()
			textbox = inpt.phrase
		inpt.name = post["input_name"]
		inpt.options = post["input_options"]
		inpt.save()

		# save textbox and update content with new markers (if they changed)
		# if there's no text for name, don't save it
		if post['textbox_name']:
			textbox.name = post['textbox_name']
		textbox.content = post["textbox_content"].replace(old_marker, inpt.marker())
		textbox.save()

		# return the updated input lists and content
		return_data = {
			"input_list": textbox.textbox_input_list(),
			"import_list": textbox.textbox_import_list(),
			"updated_content": textbox.content,
		}

		return HttpResponse(json.dumps(return_data))
	else:
		return HttpResponse("Didn't receive a POST request.")


# delete an existing input and update markers in content (if changed)
@login_required
def delete_input_view(request):
	if request.POST:
		post = request.POST

		# get input and delete it
		if post["textbox_type"] == "Template": 
			inpt = InputT.objects.get(pk=int(post["input_pk"]))
			marker = inpt.marker()
			textbox = inpt.template
		elif post["textbox_type"] == "Phrase":
			inpt = InputP.objects.get(pk=int(post["input_pk"]))
			marker = inpt.marker()
			textbox = inpt.phrase
		inpt.delete()

		# save textbox and remove markers from content if there is one
		# if there's no text for name, don't save it
		if post['textbox_name']:
			textbox.name = post['textbox_name']
		textbox.content = post["textbox_content"].replace(marker, "")
		textbox.save()

		# return the updated input lists and content
		return_data = {
			"input_list": textbox.textbox_input_list(),
			"import_list": textbox.textbox_import_list(),
			"updated_content": textbox.content,
		}

		return HttpResponse(json.dumps(return_data))
	else:
		return HttpResponse("Didn't receive a POST request.")


@login_required
def import_input_view(request):
	if request.POST:
		post = request.POST

		if post["textbox_type"] == "Template":
			textbox = fx.save_textbox(post)

			# create a new input based on the one selected
			input_to_import = InputT.objects.get(pk=int(post['input_pk']))
			new_input = InputT(
				user=request.user, 
				template=textbox,
				name=input_to_import.name,
				options=input_to_import.options,
			)
			new_input.save()

		# return the updated input lists
		return_data = {
			"input_list": textbox.textbox_input_list(),
			"import_list": textbox.textbox_import_list(),
		}

		return HttpResponse(json.dumps(return_data))
	else:
		return HttpResponse("Didn't receive a POST request.")


#----------------------------------------------------------------------------------------------------------------------------------------------
#
# NARRATIVE VIEWS
#
#----------------------------------------------------------------------------------------------------------------------------------------------

def generate_narrative_view(request, temp_pk):
	# create new narrative from template
	template = Template.objects.get(pk=temp_pk)

	narrative = Narrative(
		user=request.user, 
		template=template, 
		name=template.name, 
		input_list=template.narrative_input_list(), 
		content=template.content)
	narrative.save()
	return redirect('main:narrative', pk=narrative.pk)

@login_required
def narrative_view(request, pk):
	narrative = Narrative.objects.get(pk=pk)

	if request.POST:
		post = request.POST 
		if post['delete_narrative']:
			narr_to_delete = Narrative.objects.get(pk=int(post['delete_narrative']))
			narr_to_delete.delete()
			return redirect('main:narrative_library')

	context = {
		'owner': request.user,
		'narrative': narrative, 
		'input_list': json.loads(narrative.input_list),
		'our_phrase_list': Phrase.objects.filter(for_all=True).order_by(Lower("name")),
		'your_phrase_list': Phrase.objects.filter(user=request.user).order_by(Lower("name")),
		'a_to_an': fx.a_to_an,
		'pronouns': fx.pronouns,
		}

	return render(request, 'main/narrative.html', context)


@login_required
def narrative_library_view(request):
	count = Narrative.objects.filter(user=request.user).count()
	narratives = Narrative.objects.filter(user=request.user).order_by('-created')

	context = {
		'owner': request.user,
		'narratives': narratives,
		'total_written': len(narratives),
		}

	return render(request, 'main/narrative_library.html', context)


#----------------------------------------------------------------------------------------------------------------------------------------------
#
# NARRATIVE AJAX VIEWS
#
#----------------------------------------------------------------------------------------------------------------------------------------------


# update the DB with the narrative's current content and input list on the browser side
@login_required
def save_narrative_view(request):
	if request.POST:
		post = request.POST

		fx.save_narrative(post)

		return HttpResponse("Successfully saved narrative.")
	else:
		return HttpResponse("Didn't receive a POST request.")


# save a new input option from the narrative page to the database
# ready to work for phrases too, but this isn't set up on browser side yet
@login_required
def save_option_view(request):
	if request.POST:
		post = request.POST

		# update name and content of narrative
		fx.save_narrative(post)

		# get the correct input to save to
		if post['input_id'][0] == "t":
			inpt = InputT.objects.get(pk=int(post['input_id'][2:]))
		elif post['input_id'][0] == "p":
			inpt = InputP.objects.get(pk=int(post['input_id'][2:]))
		else:
			print("Trouble finding correct input type.")

		# add new option to options list and save input
		options_list = inpt.get_options()
		options_list.append(post['new_option'])
		inpt.save_options(options_list)


		return HttpResponse("Successfully saved new input option.")
	else:
		return HttpResponse("Something went wrong saving option to DB.")


# clean the narrative with options selected by user, and return to browser side
@login_required
def clean_narrative_view(request):
	if request.POST:
		post = request.POST

		# get the narrative, current content, and functions to execute
		narrative = fx.save_narrative(post)
		content = narrative.content
		to_execute = json.loads(post["to_execute"])

		# execute the functions checked by the user on the browser side
		if to_execute["remove_markers"]:
			content = fx.remove_markers(content)
		# alternate between a and an appropriately
		if to_execute["a_to_an"]:
			content = fx.convert_a_to_an(content)
		# change all pronouns to the gender selected by the user
		if to_execute["pronouns"]:
			content = fx.switch_pronouns(content, to_execute["pronouns"])

		# update and save narrative with new content
		narrative.content = content 
		narrative.save()
		
		return_data = {
			"content": content,
		}

		return HttpResponse(json.dumps(return_data))
	else:
		return HttpResponse("Something went wrong saving narrative to DB.")

#----------------------------------------------------------------------------------------------------------------------------------------------
#
# OTHER VIEWS
#
#----------------------------------------------------------------------------------------------------------------------------------------------


@login_required
def feedback_view(request):
	context = {
		'owner': request.user,
		}

	if request.POST:
		post = request.POST
		
		fx.send_feedback(post, request.user)
		messages.success(request, "Feedback Sent. Thank You.")
		return redirect("main:home")

	return render(request, 'main/feedback.html', context)
