import io, os, sys
import subprocess
from zipfile import ZipFile
from datetime import datetime
from pytz import timezone
from werkzeug.utils import secure_filename
import json
import hashlib
import requests
from django.http import HttpResponse

import pyotp
from django.conf import settings
from django.core.files.storage import FileSystemStorage


def login_otp(run_, otp_):
    now_ = datetime.now(timezone('Chile/Continental'))
    dt_ = now_.strftime('%Y-%m-%dT%H:%M:%S%Z:00')
    tmz_ = int(datetime.timestamp(now_))
    print(f"OTP: {otp_},RUN: {run_}, NOW: {now_}, TZ: {tmz_}, t_:{dt_}")

    url = settings.OTP_SERVICE
    print(url)
    headers = {'Content-Type': 'application/json', 'x-api-key': settings.X_API_KEY}
    payload = [{"RUT": run_, "OTP": otp_, "TIMESTAMP": dt_}]
    req = requests.post(url, headers=headers, json=payload)
    print(f"Request result: {req.status_code}, {req.json()}, {req.reason}")
    r_ = req.json()
    if (req.status_code != 200 or not r_[0].get('OTPVERIFY', False) or r_[0].get(
            'OTPVERIFY') == 'RUT_NO_EXISTE'): return False
    return True


class RouteCommand:
    def __init__(self):
        time = datetime.now(timezone('Chile/Continental'))
        self.t_stamp = str(int(datetime.timestamp(time)))
        print(f"time: {time}, timeStamp: {self.t_stamp}")
        self.pathRootDirectory = os.path.join(settings.BASE_DIR, f'{self.t_stamp}_tmpdirectory')
        print(self.pathRootDirectory)
        if not os.path.exists(self.pathRootDirectory):
            os.makedirs(self.pathRootDirectory)
            print("dir maked")
        os.system(f'cp "{settings.BASE_DIR}/static/jsonDataResult.json" "{self.pathRootDirectory}/jsonDataResult.json"')
        self.cmd = "NO_SE_PUDO_REALIZAR_DESENCRIPTACION"
        self.now_ = datetime.now(timezone('Chile/Continental'))
        self.dt_ = self.now_.strftime('%Y-%m-%dT%H:%M:%S%Z:00')

    def firmar_reporte(self):
        totp = pyotp.TOTP('JJCVGVKTKRCUCTKB')
        dt2_ = self.dt_[::-1].replace(':', '', 1)[::-1]
        dt = datetime.strptime(dt2_, "%Y-%m-%dT%H:%M:%S%z")
        self.token = totp.at(for_time=dt)
        response = totp.verify(otp=self.token, for_time=dt, valid_window=10)
        self.hash_ = hashlib.md5(f"{self.now_},{self.run_},{self.otp_},{self.token}".encode('utf-8')).hexdigest()
        print(self.token, response)
        print(self.hash_)

    def init_enviroment(self):
        #os.system(f'cp -a "{settings.APP_CODE}/." {self.pathRootDirectory}')
        self.path_exec_file = f"{self.pathRootDirectory}/git_tmp/parseCSVtoEDE.py"
        #self.path_exec_file = f"parseCSVtoEDE.py"
        print(f"Archivo parseCSVtoEDE.py copiado en: {self.path_exec_file}")

    def validarFormulario(self, file, otp, run, rbd):
        try:
            print("validando")
            self.file = file
            print(f"file done, {self.file.name}")
            if not self.allowed_file(self.file.name):
                print("extention not permited")
                raise "extention not permited"
            self.otp_ = otp
            print("otp done")
            rut_ = run
            if "-" not in rut_:
                rut_ = rut_.strip()[:-1] + "-" + rut_[-1]
            self.run_ = rut_
            print("rut done")
            self.rbd_ = rbd
            print(self.file, self.otp_, self.run_, self.rbd_)
            if (self.file and self.otp_ and self.run_ and self.rbd_): return True
            raise "Faltan parametros"
        except:
            return False

    def extractAll(self, file):
        filename = secure_filename(file.name)
        fullPath_file = os.path.join(self.pathRootDirectory, filename + 'source.zip')
        fs = FileSystemStorage(location=self.pathRootDirectory)
        fs.save(filename+'source.zip', file)
        #file.save(fullPath_file)

        with ZipFile(fullPath_file, 'r') as zip_ref:
            zip_ref.extractall(self.pathRootDirectory)
            _t = f'Archivo ZIP "{fullPath_file}" descomprimido con éxito';
            print(_t)
            print(zip_ref.namelist())

        return zip_ref.namelist()

    def getCheckCommand(self):
        print("Check command")
        dbFile = [f for f in sorted(os.listdir(self.pathRootDirectory)) if (str(f))[-15:] == "_encryptedD3.db"]
        dbPath = [os.path.join(self.pathRootDirectory, str(f)) for f in dbFile]
        encriptFile = [f for f in sorted(os.listdir(self.pathRootDirectory)) if (str(f))[-14:] == "_key.encrypted"]
        encriptPath = [os.path.join(self.pathRootDirectory, str(f)) for f in encriptFile]
        print(f"encriptPath: {encriptPath}")
        print(f"dbPath: {dbPath}")
        if encriptPath and dbPath:
            openssl_cmd = f'openssl rsautl -oaep -decrypt -inkey "{os.path.join(settings.BASE_DIR, "claveprivada.pem")}" -in "{encriptPath[0]}" -out "{os.path.join(self.pathRootDirectory, self.t_stamp)}_key.txt"'
            print(openssl_cmd)
            os.system(openssl_cmd)
            if os.path.exists(f"{os.path.join(self.pathRootDirectory, self.t_stamp)}_key.txt"):
                with open(f"{self.pathRootDirectory}/{self.t_stamp}_key.txt", "r") as myfile:
                    frase_secreta = myfile.readlines()
                print(f"frase_secreta: {frase_secreta}")
                if (frase_secreta):
                    self.cmd = f'python3 "{self.path_exec_file}" check -t 0 --json {frase_secreta[0]} {dbPath[0]}'
                else:
                    self.cmd = "NO_SE_PUDO_REALIZAR_DESENCRIPTACION"
        else:
            self.cmd = f'python3 "{self.path_exec_file}" check --help'
        return self.cmd

    def execute(self, cmd, cwd):
        try:
            print("execute intro")
            completedProcess = subprocess.run(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT, timeout=9999, universal_newlines=True)
            print(f"completed: {completedProcess}")
            response = HttpResponse(completedProcess.stdout, 200)
            response.mimetype = "text/plain"
            return response
        except subprocess.TimeoutExpired:
            response = HttpResponse("Timedout", 400)
            response.mimetype = "text/plain"
            return response

        # def saveReportResult(self, jsonDumps):
        #self.post_id = dbMongoCollection.insert_one({
        #    '_id': self.hash_,
        #    'rbd': self.rbd_,
        #    'dt': self.now_,
        #    't_stamp': self.t_stamp,
        #    'run': self.run_,
        #    'otpEDE': self.token,
        #    'otpUser': self.otp_,
        #    'json': jsonDumps
        #}).inserted_id

    def allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS
