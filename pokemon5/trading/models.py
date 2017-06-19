from django.db import models


class Trainer(models.Model):
    name = models.CharField(max_length=127)
    
    def __str__(self):
        return self.name


class PokemonType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=127, unique=True)
    tradeEvolution = models.ForeignKey('PokemonType', blank=True, null=True)
    
    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class Pokemon(models.Model):
    type = models.ForeignKey(PokemonType)
    trainer = models.ForeignKey(Trainer)
    
    def __str__(self):
        return "%s (%s)" % (self.type.name, self.trainer.name)
