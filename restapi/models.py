from django.db import models


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=11)
    t_stamp = models.DateTimeField(auto_now=True)


class QuerysRbds(models.Model):
    id = models.IntegerField(primary_key=True)
    filename = models.CharField(max_length=40)
    run = models.CharField(max_length=11)
    otp = models.IntegerField()
    otp_is_valid = models.BooleanField(null=True)
    rbd = models.IntegerField()
    email = models.CharField(max_length=40, null=True)


class Report(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    rbd = models.IntegerField()
    link = models.CharField(max_length=200)
    run = models.CharField(max_length=11)
    reportestr = models.CharField(max_length=20000)
    t_stamp = models.DateTimeField(auto_now=True)
    queryid = models.IntegerField(null=True)


class ResultReport(models.Model):
    id = models.IntegerField(primary_key=True)
    report_id = models.CharField(max_length=32)
    func_name = models.CharField(max_length=5)
    result = models.CharField(max_length=9)  # S/Datos, Aprobado, Rechazado
# Create your models here.
