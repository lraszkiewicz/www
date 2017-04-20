from django.db import models


class Candidate(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)


class Voivodeship(models.Model):  # województwo
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return 'Województwo {}'.format(self.name)


class District(models.Model):  # okręg
    id = models.IntegerField(primary_key=True)

    def __str__(self):
        return 'Okręg nr {}'.format(self.id)


class Municipality(models.Model):  # gmina
    id = models.CharField(max_length=6, primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return 'Gmina {} ({})'.format(self.name, self.id)

    class Meta:
        verbose_name_plural = "municipalities"


class Place(models.Model):  # obwód
    number = models.IntegerField()
    address = models.CharField(max_length=500)
    voivodeship = models.ForeignKey('Voivodeship')
    district = models.ForeignKey('District')
    municipality = models.ForeignKey('Municipality')
    eligible_voters = models.IntegerField()  # uprawnieni
    issued_ballots = models.IntegerField()  # wydane karty
    spoilt_ballots = models.IntegerField()  # głosy nieważne

    def __str__(self):
        return 'Obwód nr {} - {}'.format(self.number, self.municipality)

    class Meta:
        unique_together = ('number', 'municipality', 'district')


class Votes(models.Model):
    amount = models.IntegerField()
    candidate = models.ForeignKey('Candidate')
    place = models.ForeignKey('Place')

    def __str__(self):
        return '{} - {} głosów - {}'.format(self.candidate, self.amount, self.place)

    class Meta:
        unique_together = ('candidate', 'place')
        verbose_name_plural = "votes"
