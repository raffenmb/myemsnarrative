# main/functions.py

from django.core.mail import send_mail
from main.models import Template, Phrase, Narrative
import json, re

# variables for cleaning the narrative
a_to_an = {" a 8": " an 8", " a 18": " an 18", " a a": " an a", " a e": " an e", " a i": " an i", " a o": " an o", " a u": " an u", " A a": " An a", " A e": " An e", " A i": " An i", " A o": " An o", " A u": " An u", " a A": " an A", " a E": " an E", " a I": " an I", " a O": " an O", " a U": " an U", " A A": " An A", " A E": " An E", " A I": " An I", " A O": " An O", " A U": " An U",}
pronouns = [(" his ", " her ", " their "), (" His ", " Her ", " Their "), (" he ", " she ", " they "), (" He ", " She ", " They "), (" him ", " her ", "them "), (" him.", " her.", " them."), (" him,", " her,", " them,")]

# for cleaning narrative, replace "a" and "an" when gramatically appropriate
def convert_a_to_an(content):
	for improper, proper in a_to_an.items():
		content = content.replace(improper, proper)
	return content

# remove unanswered markers in the content
def remove_markers(content):
	markers_found = re.findall('{.*?}', content)
	for marker in markers_found:
		content = content.replace(marker, "")

	return content

# save narrative
def save_narrative(post):
	# get the correct narrative
	narrative = Narrative.objects.get(pk=int(post['narrative_pk']))

	# save the narrative's name, content and input list from browser side to DB
	input_list = json.loads(post["input_list"])
	narrative.input_list = json.dumps(input_list)
	narrative.template = post["narrative_name"]
	narrative.content = post["narrative_content"]
	narrative.save()

	return narrative

# save textbox
def save_textbox(post):
	# get the correct textbox from the database
	if post["textbox_type"] == "Template":
		textbox = Template.objects.get(pk=int(post['textbox_pk']))
	elif post["textbox_type"] == "Phrase":
		textbox = Phrase.objects.get(pk=int(post['textbox_pk']))

	# if there's a name submitted, save it
	if post['textbox_name']:
		textbox.name = post['textbox_name']
	# otherwise name it "Untitled"
	else:
		textbox.name = "Untitled"

	# save the content and the textbox
	textbox.content = post['textbox_content']
	textbox.save()

	return textbox

# send an email to admin with feedback from user
def send_feedback(post, user):
	send_mail(
		subject=post['feedback_subject'], 
		message= "From: " + user.email + "\n\n" + post['feedback_message'], 
		from_email=user.email,
		recipient_list=['myemsnarrative@gmail.com'], 
		fail_silently=False
		)

	return True

# for cleaning narrative, replace all pronouns with specific gender pronouns
def switch_pronouns(content, gender):
	for options in pronouns:
		if gender == "male":
			content = content.replace(options[1], options[0])
			content = content.replace(options[2], options[0])
		elif gender == "female":
			content = content.replace(options[0], options[1])
			content = content.replace(options[2], options[1])
		elif gender == "non-binary":
			content = content.replace(options[0], options[2])
			content = content.replace(options[1], options[2])

	return content