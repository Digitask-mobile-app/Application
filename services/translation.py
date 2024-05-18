from .models import Task, PlumberTask
from modeltranslation.translator import TranslationOptions,register

@register(Task)
class TaskTranslationOptions(TranslationOptions):
    fields = ('description', 'location', 'note',)

@register(PlumberTask)
class PlumberTaskTranslationOptions(TranslationOptions):
    fields = ('equipment',)