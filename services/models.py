from django.db import models
from accounts.models import User,Group
# from django.contrib.gis.db import models

TASK_TYPES = (
    ('connection', 'connection'),
    ('problem', 'problem'),
)

status_task = (
    ("waiting", 'waiting'),
    ("inprogress", "inprogress"),
    ("started", "started"),
    ("completed", "completed"),
)

class Status(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)

    class Meta:
        abstract = True


class Task(Status):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    task_type = models.CharField(max_length=100, choices=TASK_TYPES)
    description = models.TextField(null=True,blank=True)
    registration_number = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=100,null=True,blank=True)
    location = models.CharField(max_length=100)  
    note = models.TextField(null=True,blank=True)
    date = models.DateField()
    group = models.ManyToManyField(Group, related_name='group_tasks',blank=True)
    status = models.CharField(max_length=100, choices=status_task, default='waiting')

    is_voice = models.BooleanField(default=False)
    is_internet = models.BooleanField(default=False)
    is_tv = models.BooleanField(default=False)

    def __str__(self):
        return self.description
 

    def is_service(self):
        return hasattr(self, 'internet') or hasattr(self, 'tv') or hasattr(self, 'voice')

    def get_service(self):
        if hasattr(self, 'internet') and self.internet:
            return 'Internet'
        if hasattr(self, 'tv') and self.tv:
            return 'TV'
        if hasattr(self, 'voice') and self.voice:
            return 'Voice'
        return None
    
    

class Internet(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='internet')
    photo_modem = models.ImageField(upload_to='internet/')
    modem_SN = models.CharField(max_length=100)
    optical_cable = models.CharField(max_length=100)
    fastconnector = models.CharField(max_length=100)
    siqnal = models.CharField(max_length=100)


class TV(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='tv')
    photo_modem = models.ImageField(upload_to='tv/')
    modem_SN = models.CharField(max_length=100)
    rg6_cable = models.CharField(max_length=100)
    f_connector = models.CharField(max_length=100)
    splitter = models.CharField(max_length=100)


class Voice(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='voice')
    photo_modem = models.ImageField(upload_to='voice/')
    modem_SN = models.CharField(max_length=100)
    home_number = models.CharField(max_length=100)
    password = models.CharField(max_length=100)


class PlumberTask(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    equipment = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    count =  models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return self.equipment
    
