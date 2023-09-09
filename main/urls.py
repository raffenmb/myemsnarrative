# main/urls.py

from django.urls import path
from main import views

app_name = "main"

mainpatterns = [
	path('', views.welcome_view, name='welcome'),
	path('acknowledgment/', views.acknowledgment_view, name='acknowledgment'),
	path('home/', views.home_view, name='home'),
	path('design/', views.design_menu_view, name="design_menu"),
	path('template/<int:pk>/', views.template_view, name='template'),
	path('phrase/<int:pk>/', views.phrase_view, name='phrase'),
	path('generate/<int:temp_pk>/', views.generate_narrative_view, name='generate_narrative'),
	path('narrative/<int:pk>/', views.narrative_view, name='narrative'),
	path('narrative-library/', views.narrative_library_view, name='narrative_library'),
	path('feedback/', views.feedback_view, name="feedback"),
]

ajaxpatterns = [
	path('save-textbox/', views.save_textbox_view, name="save_textbox"),
	path('create-input/', views.create_input_view, name="create_input"),
	path('update-input/', views.update_input_view, name="update_input"),
	path('delete-input/', views.delete_input_view, name="delete_input"),
	path('import-input/', views.import_input_view, name="import_input"),
	path('save-narrative/', views.save_narrative_view, name='save_narrative'),
	path('save-option/', views.save_option_view, name='save_option'),
	path('clean-narrative/', views.clean_narrative_view, name='clean_narrative'),
]

urlpatterns = mainpatterns + ajaxpatterns