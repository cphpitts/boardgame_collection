from django.db import models

# Create your models here.
class Game(models.Model):
    game_name = models.CharField(max_length=100, default="", blank=True, null=False)
    game_designer = models.CharField(max_length=100, default="", blank=True, null=False)
    game_publisher = models.CharField(max_length=100, default="", blank=True, null=False)
    game_min_player = models.IntegerField(default=1, blank=True, null=False)
    game_max_player = models.IntegerField(default=1, blank=True, null=False)
    game_image_path = models.CharField(max_length=1000, default="", blank=True, null=False)
    game_playtime = models.CharField(max_length=100, default="", blank=True, null=False)
    game_expansion = models.BooleanField()

    objects = models.Manager()

    def __str__(self):
        return self.game_name

class Player(models.Model):
    player_fname = models.CharField(max_length=100, default="", null=False)
    player_lname = models.CharField(max_length=100, default="", null=False)
    player_wins = models.IntegerField(default=0)

    objects = models.Manager()

    def __str__(self):
        return "{} {}".format(self.player_fname, self.player_lname)

class Session(models.Model):
    session_name = models.CharField(max_length=100, default="", null=False)
    session_game = models.ForeignKey(Game, related_name="game_session", on_delete=models.CASCADE)
    session_player = models.ManyToManyField(Player, related_name="player_session")
    session_winner = models.ForeignKey(Player, related_name="game_winner", on_delete=models.CASCADE)

    objects = models.Manager()

    def __str__(self):
        return self.session_name