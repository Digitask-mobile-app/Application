from django.contrib import admin
from .models import Task, Internet, Voice, TV, PlumberTask, Warehouse, History, WarehouseManager
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

# @admin.register(Task)
# class TaskAdmin(TranslationAdmin):
#     # form = TaskAdminForm
#     list_display = ("description",)
#     class Media:

#         group_fieldsets = True 

#         js = (
#             'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
#             'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
#             'modeltranslation/js/tabbed_translation_fields.js',
#         )
#         css = {
#             'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
#         }

# @admin.register(PlumberTask)
# class PlumberTaskAdmin(TranslationAdmin):
#     list_display = ("equipment",)
#     class Media:

#         group_fieldsets = True 

#         js = (
#             'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
#             'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
#             'modeltranslation/js/tabbed_translation_fields.js',
#         )
#         css = {
#             'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
#         }



admin.site.register(PlumberTask)

class TvInline(admin.StackedInline):  
    model = TV
    extra = 0

class InternetInline(admin.StackedInline):  
    model = Internet
    extra = 0

class VoiceInline(admin.StackedInline):  
    model = Voice
    extra = 0

class TaskAdmin(admin.ModelAdmin):
    inlines = [TvInline,InternetInline,VoiceInline]
    
admin.site.register(Task,TaskAdmin)

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('equipment_name', 'brand', 'model', 'serial_number', 'number', 'region', 'size_length')
    search_fields = ('equipment_name', 'brand', 'model', 'serial_number', 'region')

from django.contrib import admin

@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = (
        'get_equipment_name', 
        'get_brand', 
        'get_model', 
        'get_serial_number', 
        'get_region', 
        'action', 
        'timestamp'
    )
    search_fields = (
        'warehouse_item__equipment_name', 
        'warehouse_item__brand', 
        'warehouse_item__model', 
        'warehouse_item__serial_number', 
        'warehouse_item__region', 
        'action'
    )
    readonly_fields = (
        'warehouse_item', 
        'get_equipment_name', 
        'get_brand', 
        'get_model', 
        'get_serial_number', 
        'get_region', 
        'get_number', 
        'get_size_length'
    )

    def get_equipment_name(self, obj):
        return obj.get_equipment_name()
    get_equipment_name.short_description = 'Equipment Name'

    def get_brand(self, obj):
        return obj.get_brand()
    get_brand.short_description = 'Brand'

    def get_model(self, obj):
        return obj.get_model()
    get_model.short_description = 'Model'

    def get_serial_number(self, obj):
        return obj.get_serial_number()
    get_serial_number.short_description = 'Serial Number'

    def get_region(self, obj):
        return obj.get_region()
    get_region.short_description = 'Region'

    def get_number(self, obj):
        return obj.get_number()
    get_number.short_description = 'Number'

    def get_size_length(self, obj):
        return obj.get_size_length()
    get_size_length.short_description = 'Size Length'

