import os
from zipfile import ZipFile
from datetime import datetime
from pytz import timezone
import qrcode
import json
from git import Repo
import shutil
from . import otp_model


def clone_repo(repodir):

    Repo.clone_from("https://github.com/Admin-EDE/DockerEdeCode", repodir, branch='master')
    #print("to copy")
    #files_list = os.listdir(repodir)
    #for files in files_list:
    #    if not files in [".git", ".gitignore"] :
    #        shutil.copytree(files, path_)
    print("cloned")


def upload_file_view(rCmd: otp_model.RouteCommand):
    try:
        cmd = rCmd.cmd
        print("to execute")
        repodir = os.path.join(rCmd.pathRootDirectory, "git_tmp")
        clone_repo(repodir)
        response = rCmd.execute(cmd, cwd=repodir)
        print("executed")
        print(response)
        print(sorted(os.listdir(rCmd.pathRootDirectory)))
        dataFile = [f for f in sorted(os.listdir(rCmd.pathRootDirectory)) if (str(f))[-9:] == "_Data.zip"]
        print(dataFile)
        if dataFile:
            with ZipFile(f"{os.path.join(rCmd.pathRootDirectory, dataFile[0])}") as zipfile:
                for zipinfo in zipfile.filelist:
                    if (str(zipinfo.filename))[-4:] == ".txt":
                        logFileName = zipinfo.filename
                        zipfile.extract(logFileName, path=f'{rCmd.pathRootDirectory}')
                        print("extracted log file")
                        with open(f"{rCmd.pathRootDirectory}/jsonDataResult.json") as json_file:
                            dataJson = json.load(json_file)

                        # print(dataJson.get('functions',{}).keys())
                        functionsList = dataJson.get('functions', {}).keys()
                        # print("functionsList:",type(functionsList),functionsList)
                        jsonDumps = json.dumps(dataJson, indent=None)
                        functionsImplemented = []
                        with open(f"{rCmd.pathRootDirectory}/{logFileName}") as f:
                            logs = f.read().splitlines()
                            for lineNumber ,l in enumerate(logs):
                                d = {}
                                try:
                                    d = eval(l)
                                except:
                                    print(f"No se pudo evaluar la linea #{lineNumber} del archivo. Contenido: {l} ")
                                    pass

                                for key ,value in d.items():
                                    # print(f"Outside if: {key}:{value}")
                                    if key == 'funcName' and value in functionsList and d.get('message') in \
                                        ["Rechazado", "S/Datos", "Aprobado", "No/Verificado"]:
                                        print(f"Inside if functionsList: {key}:{value}")
                                        print(d.get('message'))
                                        functionsImplemented.append(value)
                                        txt1 = '#/functions/' + value
                                        txt2 = f'"{value}": "No/Verificado"'
                                        result = d.get('message')
                                        jsonDumps = jsonDumps.replace(txt1, f'{result}')
                                        jsonDumps = jsonDumps.replace(txt2, f'"{value}": "{result}"')

                        print(f"functionsImplemented: {functionsImplemented}")
                        for fn in functionsList:
                            if fn not in functionsImplemented:
                                # print(f"Inside if functionsImplemented: {fn}")
                                jsonDumps = jsonDumps.replace('#/functions/' + fn, "No/Verificado")

            rCmd.saveReportResult(jsonDumps)

            # The data that you want to store
            data = f"/checkresult/{rCmd.t_stamp}-{dataFile[0]}-{rCmd.hash_}"
            #data = url_for('check_result_route', foldername=f'{rCmd.pathRootDirectory}-{dataFile[0]}-{rCmd.hash_}',
            #               _external=True, _scheme='https')
            #data = data.replace("//app", "/app")

            # Create qr code instance
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            # Add data
            qr.add_data(data)
            qr.make(fit=True)
            # qr.make()

            # Create an image from the QR Code instance
            img = qr.make_image()
            img.save(f"{rCmd.pathRootDirectory}/qrimage.jpg")

            fchk = open(f"/app/templates/check.html", "r")
            fstyle = open(f"/app/static/css/style.css", "r")
            txt = fchk.read()
            styleText = fstyle.read()
            fchk.close()
            fstyle.close()
            txt = txt.replace("/app/static/js/d3.v4.js", 'https://d3js.org/d3.v4.js')
            txt = txt.replace('<link rel="stylesheet" href="/app/static/css/style.css">',
                              '<style>' + styleText + '</style>')
            txt = txt.replace("{{jsonData|tojson|safe}}", "'" + jsonDumps + "'")
            # txt = txt.replace("{{json|tojson|safe}}", '"' + request.url_root + 'report/' + rCmd.hash_ + '"')
            # url_for('check_result_route', foldername=rCmd.pathRootDirectory+"-"+dataFile[0]+"-"+rCmd.hash_)
            # txt = txt.replace("{{json|tojson|safe}}", '"' + url_for('report_route', id=rCmd.hash_,_external=True,_scheme='https')+ '"')
            txt = txt.replace("{{json|tojson|safe}}", '"' + data + '"')
            txt = txt.replace('/{{folder}}/{{file}}', data)
            txt = txt.replace('/{{folder}}/qrimage.jpg', "./qrimage.jpg")
            txt = txt.replace('Descargar informe técnico', "Accede a tu informe desde Internet")

            f = open(f"{rCmd.pathRootDirectory}/linkReport.html", "w+")
            f.write(txt)
            f.close()

            with ZipFile(f"{rCmd.pathRootDirectory}/{dataFile[0]}", 'a') as zipf:
                zipf.write(f"{rCmd.pathRootDirectory}/qrimage.jpg", 'qrimage.jpg')
                zipf.write(f"{rCmd.pathRootDirectory}/linkReport.html", 'linkReport.html')

            #return redirect(
            #    url_for('check_result_route', foldername=rCmd.pathRootDirectory + "-" + dataFile[0] + "-" + rCmd.hash_))
        #elif (dataFile):
        #    print(f"beforeRedirect: {os.path.join(rCmd.t_stamp, dataFile)}")
            #return redirect(url_for('app_file_route', foldername=rCmd.t_stamp, filename=dataFile[0]))
        else:
            return response
    except Exception as e:
        print(f"Error general en process file: {e}")
        #abort(500, e)