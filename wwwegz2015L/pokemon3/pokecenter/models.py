from django.db import models
from django.core.validators import RegexValidator

class Trainer(models.Model):
    license_number = models.CharField(
        max_length=10,
        primary_key=True,
        validators=[
            RegexValidator(
                regex='^[A-Z]{3}[0-9]{7}$',
                message="License number must consist of three capital letters followed by seven digits",
                code="invalid_license_number"
            )
        ]
    )

    name = models.CharField(max_length=128)
    
    def __str__(self):
        return "%s (%s)" % (self.name, self.license_number)
    
class Pokemon(models.Model):
    HEALTHY = "H"
    REGENERATING = "R"

    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)

    name = models.CharField(max_length=64)

    status = models.CharField(
        max_length=1,
        choices=(
            (HEALTHY, "Healthy"),
            (REGENERATING, "Regenerating"),
        )
    )
    
    def __str__(self):
        return "%s (%s, %s)" % (self.name, self.trainer.name, self.status)