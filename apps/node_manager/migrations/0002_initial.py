# Generated by Django 4.2.13 on 2024-06-03 09:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('node_manager', '0001_initial'),
        ('user_manager', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='node_messagerecipientrule',
            name='recipients',
            field=models.ManyToManyField(related_name='node_message_recipients_mapping', to='user_manager.user'),
        ),
        migrations.AddField(
            model_name='node_group',
            name='leader',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='user_manager.user'),
        ),
        migrations.AddField(
            model_name='node_group',
            name='time_slot_recipient',
            field=models.ManyToManyField(related_name='time_slot_recipient_mappings', to='node_manager.node_messagerecipientrule'),
        ),
        migrations.AddField(
            model_name='node_diskpartition',
            name='node',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='node_manager.node'),
        ),
        migrations.AddField(
            model_name='node_baseinfo',
            name='disk_list',
            field=models.ManyToManyField(related_name='disk_list', to='node_manager.node_diskpartition'),
        ),
        migrations.AddField(
            model_name='node_baseinfo',
            name='node',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='node_manager.node'),
        ),
        migrations.AddField(
            model_name='node',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='node_manager.node_group'),
        ),
        migrations.AddField(
            model_name='node',
            name='tags',
            field=models.ManyToManyField(related_name='tags', to='node_manager.node_tag'),
        ),
    ]