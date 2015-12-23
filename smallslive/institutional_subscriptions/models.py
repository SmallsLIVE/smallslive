from django.db import models
from django.utils import timezone


class Institution(models.Model):
    name = models.CharField(max_length=200)
    user_quota = models.IntegerField(default=0)
    subscription_end = models.DateTimeField()
    contact_name = models.CharField(max_length=150, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(max_length=150, blank=True)
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return u"Institution: {0}".format(self.name)

    def is_subscription_active(self):
        if not self.subscription_start or not self.subscription_end:
            return False
        else:
            return self.subscription_start <= timezone.now() <= self.subscription_end
