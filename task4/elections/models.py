import os

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum


class Candidate(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        creating = False
        if not self.pk:
            creating = True
        super(Candidate, self).save(*args, **kwargs)
        if creating:
            for v in Voivodeship.objects.all():
                Votes.objects.create(candidate=self, parent=Results.objects.get(voivodeship=v), amount=0)
            for d in District.objects.all():
                Votes.objects.create(candidate=self, parent=Results.objects.get(district=d), amount=0)
            for m in Municipality.objects.all():
                Votes.objects.create(candidate=self, parent=Results.objects.get(municipality=m), amount=0)
            for p in Place.objects.all():
                Votes.objects.create(candidate=self, parent=Results.objects.get(place=p), amount=0)

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)


class Voivodeship(models.Model):  # województwo
    name = models.CharField(max_length=50, unique=True)

    def save(self, *args, **kwargs):
        creating = False
        if not self.pk:
            creating = True
        super(Voivodeship, self).save(*args, **kwargs)
        if creating:
            r = Results.objects.create(voivodeship=self, eligible_voters=0, issued_ballots=0, spoilt_ballots=0)
            for c in Candidate.objects.all():
                Votes.objects.create(parent=r, candidate=c, amount=0)

    def __str__(self):
        return 'Województwo {}'.format(self.name)


class District(models.Model):  # okręg
    id = models.IntegerField(primary_key=True)

    def save(self, *args, **kwargs):
        super(District, self).save(*args, **kwargs)
        if Results.objects.filter(district=self).count() == 0:
            r = Results.objects.create(district=self, eligible_voters=0, issued_ballots=0, spoilt_ballots=0)
            for c in Candidate.objects.all():
                Votes.objects.create(parent=r, candidate=c, amount=0)

    def __str__(self):
        return 'Okręg nr {}'.format(self.id)


class Municipality(models.Model):  # gmina
    id = models.CharField(max_length=6, primary_key=True)
    name = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        super(Municipality, self).save(*args, **kwargs)
        if Results.objects.filter(municipality=self).count() == 0:
            r = Results.objects.create(municipality=self, eligible_voters=0, issued_ballots=0, spoilt_ballots=0)
            for c in Candidate.objects.all():
                Votes.objects.create(parent=r, candidate=c, amount=0)

    def __str__(self):
        return 'Gmina {} ({})'.format(self.name, self.id)

    class Meta:
        verbose_name_plural = "municipalities"


class Place(models.Model):  # obwód
    number = models.IntegerField()
    address = models.CharField(max_length=500)
    voivodeship = models.ForeignKey('Voivodeship', on_delete=models.CASCADE)
    district = models.ForeignKey('District', on_delete=models.CASCADE)
    municipality = models.ForeignKey('Municipality', on_delete=models.CASCADE)
    next_protocol_number = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        creating = False
        if not self.pk:
            creating = True
        super(Place, self).save(*args, **kwargs)
        if creating:
            r = Results.objects.create(place=self, eligible_voters=0, issued_ballots=0, spoilt_ballots=0)
            for c in Candidate.objects.all():
                Votes.objects.create(parent=r, candidate=c, amount=0)

    def __str__(self):
        return 'Obwód nr {} - {}'.format(self.number, self.municipality)

    class Meta:
        unique_together = ('number', 'municipality', 'district')


class Results(models.Model):  # wyniki w danym miejscu
    voivodeship = models.OneToOneField('Voivodeship', null=True, blank=True, on_delete=models.CASCADE)
    district = models.OneToOneField('District', null=True, blank=True, on_delete=models.CASCADE)
    municipality = models.OneToOneField('Municipality', null=True, blank=True, on_delete=models.CASCADE)
    place = models.OneToOneField('Place', null=True, blank=True, on_delete=models.CASCADE)
    # exactly one of the above should be not null
    eligible_voters = models.IntegerField()  # uprawnieni
    issued_ballots = models.IntegerField()  # wydane karty
    spoilt_ballots = models.IntegerField()  # głosy nieważne

    def save(self, *args, **kwargs):
        c = (self.voivodeship is not None) + (self.district is not None)\
            + (self.municipality is not None) + (self.place is not None)
        if c != 1:
            raise ValidationError('Exactly one of: voivodeship, district, municipality, place has to be not None.')
        super(Results, self).save(*args, **kwargs)
        if self.place:
            self.place.municipality.results.update_results()
            self.place.district.results.update_results()
            self.place.voivodeship.results.update_results()

    def update_results(self):
        place_qs = None
        if self.voivodeship:
            place_qs = Place.objects.filter(voivodeship=self.voivodeship)
        elif self.district:
            place_qs = Place.objects.filter(district=self.district)
        elif self.municipality:
            place_qs = Place.objects.filter(municipality=self.municipality)
        if place_qs:
            results_qs = Results.objects.filter(place__in=place_qs)
            agg = results_qs.aggregate(eli=Sum('eligible_voters'), iss=Sum('issued_ballots'), spo=Sum('spoilt_ballots'))
            self.eligible_voters = agg['eli'] or 0
            self.issued_ballots = agg['iss'] or 0
            self.spoilt_ballots = agg['spo'] or 0
            self.save()

    def parent_str(self):
        if self.voivodeship:
            return str(self.voivodeship)
        elif self.district:
            return str(self.district)
        elif self.municipality:
            return str(self.municipality)
        elif self.place:
            return str(self.place)

    def __str__(self):
        return '{} - {}, {}, {}'.format(self.parent_str(), self.eligible_voters,
                                        self.issued_ballots, self.spoilt_ballots)

    class Meta:
        verbose_name_plural = "results"


class Votes(models.Model):
    amount = models.IntegerField()
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE)
    parent = models.ForeignKey('Results', on_delete=models.CASCADE)

    def __str__(self):
        return '{} - {} - {} głosów'.format(self.parent.parent_str(), self.candidate, self.amount)

    class Meta:
        unique_together = ('candidate', 'parent')
        verbose_name_plural = "votes"

    def save(self, *args, **kwargs):
        super(Votes, self).save(*args, **kwargs)
        if self.parent.place is not None:
            c = self.candidate
            p = self.parent.place
            Votes.objects.get(parent__municipality=p.municipality, candidate=c).update_votes()
            Votes.objects.get(parent__district=p.district, candidate=c).update_votes()
            Votes.objects.get(parent__voivodeship=p.voivodeship, candidate=c).update_votes()

    def update_votes(self):
        c = self.candidate
        p = self.parent
        v = None

        if p.municipality:
            v = Votes.objects.filter(parent__place__municipality=p.municipality, candidate=c)
        elif p.district:
            v = Votes.objects.filter(parent__place__district=p.district, candidate=c)
        elif p.voivodeship:
            v = Votes.objects.filter(parent__place__voivodeship=p.voivodeship, candidate=c)

        if v:
            self.amount = v.aggregate(Sum('amount'))['amount__sum'] or 0
            self.save()


def protocol_file_path(instance, filename):
    return 'elections/protocols/protokol{}_{}{}'.format(
        instance.place.next_protocol_number,
        instance.place.id,
        os.path.splitext(filename)[1]
    )


class ProtocolFile(models.Model):
    place = models.ForeignKey('Place')
    file = models.FileField(upload_to=protocol_file_path)

    def __str__(self):
        return os.path.basename(self.file.name)
