from django.contrib import admin
from .models import Task, Internet, Voice, TV, PlumberTask
from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language
from modeltranslation.admin import TranslationAdmin


# class TaskAdminForm(forms.ModelForm):
#     task_type = forms.ChoiceField(choices=(), required=False)

#     class Meta:
#         model = Task
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super(TaskAdminForm, self).__init__(*args, **kwargs)

#         language = get_language()
#         if language == 'az':
#             choices = (
#                 ('connection', _('Qoşulma')),
#                 ('problem', _('Problem')),
#             )
#         elif language == 'en-US':
#             choices = (
#                 ('connection', _('Connection')),
#                 ('problem', _('Problem')),
#             )

#         self.fields['task_type'].choices = choices

@admin.register(Task)
class TaskAdmin(TranslationAdmin):
    # form = TaskAdminForm
    list_display = ("description",)
    class Media:

        group_fieldsets = True 

        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }

@admin.register(PlumberTask)
class PlumberTaskAdmin(TranslationAdmin):
    list_display = ("equipment",)
    class Media:

        group_fieldsets = True 

        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }

admin.site.register(Internet)
admin.site.register(Voice)
admin.site.register(TV)
