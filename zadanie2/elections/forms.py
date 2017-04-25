from django import forms
from django.db.models import Sum

from .models import Candidate, Votes, ProtocolFile


class PlaceEditForm(forms.Form):
    eligible_voters = forms.IntegerField(label='Uprawnieni',)
    issued_ballots = forms.IntegerField(label='Wydane karty',)
    casted_ballots = forms.IntegerField(label='Głosy oddane (głosy ważne + głosy nieważne)', disabled=True)
    valid_ballots = forms.IntegerField(label='Głosy ważne (suma głosów kandydatów)', disabled=True)
    spoilt_ballots = forms.IntegerField(label='Głosy nieważne')

    def __init__(self, *args, **kwargs):
        p = kwargs.pop('place')
        kwargs.setdefault('label_suffix', '')
        super(PlaceEditForm, self).__init__(*args, **kwargs)

        self.fields['eligible_voters'].initial = p.eligible_voters
        self.fields['issued_ballots'].initial = p.issued_ballots
        self.fields['spoilt_ballots'].initial = p.spoilt_ballots
        self.fields['valid_ballots'].initial = Votes.objects.filter(place=p).aggregate(Sum('amount'))['amount__sum']
        self.fields['casted_ballots'].initial = self.fields['valid_ballots'].initial + p.spoilt_ballots
        for c in Candidate.objects.all():
            self.fields['candidate_{}'.format(c.id)] = forms.CharField(
                label=str(c),
                initial=Votes.objects.get(place=p, candidate=c).amount,
                widget=forms.NumberInput(attrs={'class': 'form-control'})
            )

    def clean(self):
        cleaned_data = super(PlaceEditForm, self).clean()
        valid_ballots = 0
        for x in cleaned_data:
            if 'candidate' in x:
                valid_ballots += int(cleaned_data[x])
        if valid_ballots + int(cleaned_data['spoilt_ballots']) > int(cleaned_data['issued_ballots']):
            raise forms.ValidationError('Oddano więcej głosów niż wydano kart.')
        if int(cleaned_data['issued_ballots']) > cleaned_data['eligible_voters']:
            raise forms.ValidationError('Wydano więcej kart niż było osób uprawnionych do głosowania')


class ProtocolUploadForm(forms.Form):
    file = forms.FileField(label='Zdjęcie protokołu (PDF lub JPG)')
