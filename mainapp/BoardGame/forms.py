from django.forms import ModelForm
from .models import Game, Player, Session
from django import forms


class GameForm(ModelForm):
    class Meta:
        model = Game
        fields = '__all__'


class PlayerForm(ModelForm):
    class Meta:
        model = Player
        exclude = ['player_wins']
        labels = {
            'player_fname': "First Name",
            'player_lname': "Last Name",
        }


class SessionForm(ModelForm):
    class Meta:
        model = Session
        fields ='__all__'


GAME_TYPES = [
    ('boardgame', "Board Games"),
    ('rpg', 'RPGs'),
]

class SearchForm(forms.Form):
    game_type = forms.CharField(widget=forms.Select(choices=GAME_TYPES))