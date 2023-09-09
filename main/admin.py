from django.contrib import admin

from main.models import (
	Template, Narrative,
	Phrase, InputT, InputP)

class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'pk')

class ToolsAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'pk')

class InputTAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'pk')

class NarrativeAdmin(admin.ModelAdmin):
    list_display = ('template', 'user', 'created')

class InputPAdmin(admin.ModelAdmin):
    list_display = ('name', 'phrase', 'user', 'pk')

admin.site.register(Template, TemplateAdmin)
admin.site.register(Narrative, NarrativeAdmin)
admin.site.register(Phrase, ToolsAdmin)
admin.site.register(InputT, InputTAdmin)
admin.site.register(InputP, InputPAdmin)