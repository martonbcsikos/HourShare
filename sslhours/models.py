from decimal import Decimal
from django.db import models


class SSLHour(models.Model):
    SSL_ID = models.UUIDField()
    date_earned = models.DateField()
    project_name = models.CharField(max_length=255)
    hours = models.DecimalField(max_digits=4, decimal_places=1)
    username = models.CharField(max_length=255)
    student_id = models.CharField(max_length=10)
    school_name = models.CharField(max_length=255)
    club = models.CharField(max_length=255)
    dt_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username}: {self.hours} ({self.school_name})"


# Some code to create dummy data
# uuid
# from datetime import datetime
# from sslhours.models import SSLHour

# SSLHour.objects.create(
#     SSL_ID=uuid.uuid4(),
#     date_earned=datetime.now().date(),
#     project_name='volunteering',
#     hours=4.0,
#     username='William',
#     student_id=789,
#     school_name='Einstein',
#     club='Orchestra',
# )
