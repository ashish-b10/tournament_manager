# Generated by Django 2.2.4 on 2019-08-04 12:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tmdb', '0017_update_headtable_permissions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sparringteammatch',
            name='division',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tmdb.TournamentSparringDivision'),
        ),
        migrations.AlterField(
            model_name='sparringteammatch',
            name='winning_team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='winning_team', to='tmdb.SparringTeamRegistration'),
        ),
        migrations.AlterField(
            model_name='sparringteamregistration',
            name='tournament_division',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tmdb.TournamentSparringDivision'),
        ),
        migrations.AlterField(
            model_name='tournamentsparringdivision',
            name='tournament',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tmdb.Tournament'),
        ),
    ]
