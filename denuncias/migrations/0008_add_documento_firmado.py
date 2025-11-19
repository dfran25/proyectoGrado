# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('denuncias', '0007_historialmodificacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='consultoriojuridico',
            name='documento_firmado',
            field=models.FileField(blank=True, null=True, upload_to='documentos_firmados/%Y/%m/', verbose_name='Documento firmado'),
        ),
        migrations.AddField(
            model_name='consultoriojuridico',
            name='firma_usuario',
            field=models.CharField(blank=True, max_length=200, verbose_name='Firma digital del usuario'),
        ),
        migrations.AddField(
            model_name='consultoriojuridico',
            name='fecha_firma',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de firma'),
        ),
    ]
