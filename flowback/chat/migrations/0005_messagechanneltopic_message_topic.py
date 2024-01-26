# Generated by Django 4.2.7 on 2024-01-26 12:33

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_message_messagechannel_messagechannelparticipant_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageChannelTopic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.messagechannel')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='message',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='chat.messagechanneltopic'),
        ),
    ]
