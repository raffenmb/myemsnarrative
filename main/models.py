# main/models.py

from django.db import models
from accounts.models import CustomUser
from django.db.models.functions import Lower
import json, re

class Template(models.Model):
	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='templates', null=False)
	name = models.CharField(max_length=255)
	content = models.TextField(blank=True, null=True)
	for_all = models.BooleanField(default=False)
	for_members = models.BooleanField(default=False)


	def __str__(self):
		return self.name

	# make this template an exact copy of an existing template
	def copy(self, to_copy):
		# copy name and content to this new template
		self.name = to_copy.name
		self.content = to_copy.content

		# create copies of all inputs in the existing template and save to this one
		for inpt in to_copy.inputTs.order_by(Lower('name')):
			new_input = InputT(
				template=self,
				user=self.user,
				name=inpt.name,
				options=inpt.options,
				)
			new_input.save()
		self.save()

	# create a dictionary of only the inputs found inside this template's content
	def narrative_input_list(self):
		# get all markers in template
		all_inputs = self.inputTs.all()
		all_markers = re.findall('{.*?}', self.content)

		# remove duplicate markers without changing the order
		single_markers = []
		[single_markers.append(marker) for marker in all_markers if marker not in single_markers]
		inputs_found = [inpt for found in single_markers for inpt in all_inputs if inpt.marker() == found]

		# create list of inputs for the narrative page
		input_list = {f"t_{inpt.pk}": {"name": inpt.name, "pk": inpt.pk, "options": inpt.get_options(), "marker": inpt.marker()} for inpt in inputs_found}

		return json.dumps(input_list)

	# create a dictionary of all inputs attached to this template and its info
	def textbox_input_list(self):
		all_inputs = self.inputTs.all().order_by(Lower('name'))

		input_list = {inpt.name: {"pk": inpt.pk, "options": inpt.get_options(), "marker": inpt.marker()} for inpt in all_inputs}
		return input_list

	# create a dictionary of all inputs that are not in this template, but are attached to the other templates owned by this user
	def textbox_import_list(self):
		# get just the names of the inputs in this template
		this_temp_inputs = list(self.inputTs.values_list('name', flat=True))
		# get the objects of all inputs not in this template but still owned by this user
		other_inputs = InputT.objects.filter(user=self.user).exclude(template=self).order_by(Lower('name'))

		# create a dictionary of inputs that do not have the same name as an input already in this template
		import_list = {}
		for inpt in other_inputs:
			# if the input does not share a name with an input in this template
			if inpt.name not in this_temp_inputs:
				# if the input name is already in the dictionary, add this one to it
				if inpt.name in import_list.keys():
					import_list[inpt.name].append({"pk": inpt.pk, "options": inpt.get_options(), "template": inpt.template.name})
				# otherwise start a new item for that input
				else:
					import_list[inpt.name] = [{"pk": inpt.pk, "options": inpt.get_options(), "template": inpt.template.name}]
			# otherwise, ignore it since it's a duplicate
			else: 
				continue

		# organize the templates for each input alphabetically
		for inpt in import_list:
			import_list[inpt] = sorted(import_list[inpt], key=lambda x: x['template'].lower())

		return import_list

	# create a dictionary of the input names and pks of all inputs attached to this template
	def get_input_names(self):
		return {inpt.name:inpt.pk for inpt in self.inputTs.order_by(Lower('name'))}

# inputs for templates
class InputT(models.Model):
	user = models.ForeignKey(CustomUser, related_name='inputTs', on_delete=models.CASCADE, null=False)
	template = models.ForeignKey(Template, related_name='inputTs', on_delete=models.CASCADE, null=False)
	name = models.CharField(max_length=255, blank=False, null=False)
	options = models.TextField(blank=True, null=True, default="[]")


	def __str__(self):
		return self.name

	def marker(self):
		return "{" + self.name + "}"

	def get_options(self):
		return json.loads(self.options)

	def save_options(self, option_list):
		self.options = json.dumps(option_list)
		self.save()


class Phrase(models.Model):
	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='phrases', null=False)
	name = models.CharField(max_length=255)
	content = models.TextField()
	for_all = models.BooleanField(default=False)
	for_members = models.BooleanField(default=True)

	def __str__(self):
		return self.name 

	# make this phrase an exact copy of an existing phrase
	def copy(self, to_copy):
		# copy name and content to this new phrase
		self.name = to_copy.name
		self.content = to_copy.content

		# create copies of all inputs in the existing phrase and save to this one
		for inpt in to_copy.inputPs.order_by(Lower('name')):
			new_input = InputP(
				phrase=self,
				user=self.user,
				name=inpt.name,
				options=inpt.options,
				)
			new_input.save()
		self.save()

	# create a dictionary of only the inputs found inside this phrase's content
	def narrative_input_list(self):
		# get markers in phrase in order without duplicates
		all_inputs = self.inputPs.all()
		all_markers = re.findall('{.*?}', self.content)

		# remove duplicate markers 
		single_markers = []
		[single_markers.append(marker) for marker in all_markers if marker not in single_markers]
		inputs_found = [inpt for found in single_markers for inpt in all_inputs if inpt.marker() == found]

		# create list of inputs for the narrative page phrase boxes
		input_list = [{"name": inpt.name, "pk": inpt.pk, "options": inpt.get_options(), "marker": inpt.marker()} for inpt in inputs_found]

		return input_list

	# create a dictionary of all inputs attached to this phrase and its info
	def textbox_input_list(self):
		all_inputs = self.inputPs.all()

		input_list = {inpt.name: {"pk": inpt.pk, "options": inpt.get_options(), "marker": inpt.marker()} for inpt in all_inputs}
		return input_list

	# empty for now, but leaving in case I want to use this later
	def textbox_import_list(self):
		return {}

	# create a dictionary of the input names and pks of all inputs attached to this phrase
	def get_input_names(self):
		return {inpt.name:inpt.pk for inpt in self.inputPs.order_by(Lower('name'))}

# inputs for phrases
class InputP(models.Model):
	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='inputPs', null=False)
	phrase = models.ForeignKey(Phrase, on_delete=models.CASCADE, related_name='inputPs', null=False)
	name = models.CharField(max_length=255, blank=False, null=False)
	options = models.TextField(blank=True, null=True, default="[]")

	def __str__(self):
		return self.name

	def marker(self):
		return "{" + self.name + "}"

	def get_options(self):
		return json.loads(self.options)

	def save_options(self, option_list):
		self.options = json.dumps(option_list)
		self.save()


class Narrative(models.Model):
	user = models.ForeignKey(CustomUser, related_name="narratives", on_delete=models.CASCADE, null=False)
	template = models.CharField(max_length=255, blank=True, null=True)
	name = models.CharField(max_length=255, default="Untitled Narrative")
	input_list = models.TextField(default="[]")
	content = models.TextField(blank=True, null=True)
	created = models.DateTimeField(auto_now_add=True)

