from django.db import models


class Candidate(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class District(models.Model):  # okręg
    id = models.IntegerField(primary_key=True)


class Municipality(models.Model):  # gmina
    id = models.CharField(max_length=6, primary_key=True)
    name = models.CharField(max_length=50)


class Area(models.Model):  # obwód
    number = models.IntegerField()
    address = models.CharField(max_length=500)
    municipality = models.ForeignKey('Municipality')
    district = models.ForeignKey('District')

    class Meta:
        unique_together = ('id', 'municipality')


class Votes(models.Model):
    amount = models.IntegerField()
    candidate = models.ForeignKey('Candidate')
    area = models.ForeignKey('Area')

    class Meta:
        unique_together = ('candidate', 'area')
