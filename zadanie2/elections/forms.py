from django import forms

from .models import Candidate, Votes


class PlaceEditForm(forms.Form):
    eligible_voters = forms.IntegerField(label='Uprawnieni')
    issued_ballots = forms.IntegerField(label='Wydane karty')
    spoilt_ballots = forms.IntegerField(label='Głosy nieważne')

    def __init__(self, *args, **kwargs):
        p = kwargs.pop('place')
        super(PlaceEditForm, self).__init__(*args, **kwargs)

        self.fields['eligible_voters'].initial = p.eligible_voters
        self.fields['issued_ballots'].initial = p.issued_ballots
        self.fields['spoilt_ballots'].initial = p.spoilt_ballots
        for c in Candidate.objects.all():
            self.fields['candidate_{}'.format(c.id)] = forms.CharField(
                label=str(c),
                initial=Votes.objects.get(place=p, candidate=c).amount
            )
