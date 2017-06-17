import os

from django import forms
from django.db.models import Sum

from .models import Candidate, Votes, ProtocolFile


class PlaceEditForm(forms.Form):
    eligible_voters = forms.IntegerField(label='Uprawnieni',)
    issued_ballots = forms.IntegerField(label='Wydane karty',)
    spoilt_ballots = forms.IntegerField(label='Głosy nieważne')

    def __init__(self, *args, **kwargs):
        p = kwargs.pop('place')
        kwargs.setdefault('label_suffix', '')
        super(PlaceEditForm, self).__init__(*args, **kwargs)
        for c in Candidate.objects.all():
            self.fields['candidate_{}'.format(c.id)] = forms.CharField(
                label=str(c),
                widget=forms.NumberInput(attrs={'class': 'form-control'})
            )


class ProtocolUploadForm(forms.Form):
    file = forms.FileField(label='Zdjęcie protokołu (PDF lub JPG)')

    def clean(self):
        cleaned_data = super(ProtocolUploadForm, self).clean()
        filename = cleaned_data['file'].name
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.pdf']:
            raise forms.ValidationError('Niedozwolone rozszerzenie pliku.')
