import os
import subprocess
from zipfile import ZipFile
from datetime import datetime
from pytz import timezone
from werkzeug.utils import secure_filename
import hashlib

from django.http import HttpResponse

import pyotp
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import shutil


class RouteCommand:
    def __init__(self):
        time = datetime.now(timezone('Chile/Continental'))
        self.t_stamp = str(int(datetime.timestamp(time)))
        print(f"time: {time}, timeStamp: {self.t_stamp}")
        self.pathRootDirectory = os.path.join(settings.BASE_DIR, "tmp", f'{self.t_stamp}_tmpdirectory')
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
        # os.system(f'cp -a "{settings.APP_CODE}/." {self.pathRootDirectory}')
        self.path_exec_file = f"{self.pathRootDirectory}/git_tmp/parseCSVtoEDE.py"
        # self.path_exec_file = f"parseCSVtoEDE.py"
        print(f"Archivo parseCSVtoEDE.py copiado en: {self.path_exec_file}")

    def delete_folder(self):
        shutil.rmtree(self.pathRootDirectory, ignore_errors=True)

    def validar_formulario(self, file, otp, run, rbd):
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
            if self.file and self.otp_ and self.run_ and self.rbd_: return True
            raise "Faltan parametros"
        except:
            return False

    def extract_all(self, file):
        filename = secure_filename(file.name)
        full_path_file = os.path.join(self.pathRootDirectory, filename + 'source.zip')
        fs = FileSystemStorage(location=self.pathRootDirectory)
        fs.save(filename+'source.zip', file)
        #file.save(fullPath_file)

        with ZipFile(full_path_file, 'r') as zip_ref:
            zip_ref.extractall(self.pathRootDirectory)
            _t = f'Archivo ZIP "{full_path_file}" descomprimido con éxito';
            print(_t)
            print(zip_ref.namelist())

        return zip_ref.namelist()

    def get_check_command(self):
        print("Check command")
        db_file = [f for f in sorted(os.listdir(self.pathRootDirectory)) if (str(f))[-15:] == "_encryptedD3.db"]
        db_path = [os.path.join(self.pathRootDirectory, str(f)) for f in db_file]
        encrypt_file = [f for f in sorted(os.listdir(self.pathRootDirectory)) if (str(f))[-14:] == "_key.encrypted"]
        encrypt_path = [os.path.join(self.pathRootDirectory, str(f)) for f in encrypt_file]
        print(f"encriptPath: {encrypt_path}")
        print(f"dbPath: {db_path}")
        if encrypt_path and db_path:
            openssl_cmd = f'openssl rsautl -oaep -decrypt -inkey "{os.path.join(settings.BASE_DIR, "claveprivada.pem")}" -in "{encrypt_path[0]}" -out "{os.path.join(self.pathRootDirectory, self.t_stamp)}_key.txt"'
            print(openssl_cmd)
            os.system(openssl_cmd)
            if os.path.exists(f"{os.path.join(self.pathRootDirectory, self.t_stamp)}_key.txt"):
                with open(f"{self.pathRootDirectory}/{self.t_stamp}_key.txt", "r") as myfile:
                    frase_secreta = myfile.readlines()
                print(f"frase_secreta: {frase_secreta}")
                if frase_secreta:
                    self.cmd = f'python3 "{self.path_exec_file}" check -s -t 0 --json {frase_secreta[0]} {db_path[0]}'
                else:
                    self.cmd = "NO_SE_PUDO_REALIZAR_DESENCRIPTACION"
        else:
            self.cmd = f'python3 "{self.path_exec_file}" check --help'
        return self.cmd

    def execute(self, cmd, cwd):
        try:
            print("execute intro")
            completed_process = subprocess.run(cmd, cwd=cwd, shell=True,
                                               stderr=subprocess.STDOUT, timeout=9999, universal_newlines=True)
            print(f"completed: {completed_process}")
            response = completed_process.returncode
            return response
        except subprocess.TimeoutExpired:
            response = "Timedout"
            return response

    def allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS
