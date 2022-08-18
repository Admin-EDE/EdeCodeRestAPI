import os
from zipfile import ZipFile
from datetime import datetime
from pytz import timezone

import json
from git import Repo
import shutil
from . import otp_model


def clone_repo(repodir):

    Repo.clone_from("https://github.com/Admin-EDE/DockerEdeCode", repodir, branch='updated_reqs')
    print("cloned")


def copy_and_delete_data(git_tmp_dir, pathdir):
    # copy _Data.zip and deletes git tmp folder
    files_list = os.listdir(git_tmp_dir)
    for file in files_list:
        if (str(file))[-9:] == "_Data.zip":
            shutil.copy(os.path.join(git_tmp_dir, file), os.path.join(pathdir, file))
    shutil.rmtree(git_tmp_dir, ignore_errors=True)


def upload_file_view(rCmd: otp_model.RouteCommand):
    try:
        cmd = rCmd.cmd
        print("to execute")
        repodir = os.path.join(rCmd.pathRootDirectory, "git_tmp")
        clone_repo(repodir)
        response = rCmd.execute(cmd, cwd=repodir)
        print("executed")
        # print(response)
        print(sorted(os.listdir(rCmd.pathRootDirectory)))
        copy_and_delete_data(repodir, rCmd.pathRootDirectory)
        dataFile = [f for f in sorted(os.listdir(rCmd.pathRootDirectory)) if (str(f))[-9:] == "_Data.zip"]
        print(dataFile)
        if dataFile:
            with ZipFile(f"{os.path.join(rCmd.pathRootDirectory, dataFile[0])}") as zipfile:
                for zipinfo in zipfile.filelist:
                    if (str(zipinfo.filename))[-4:] == ".txt":
                        logFileName = zipinfo.filename
                        zipfile.extract(logFileName, path=f'{rCmd.pathRootDirectory}')
                        print("extracted log file")
                        with open(os.path.join(rCmd.pathRootDirectory, "jsonDataResult.json")) as json_file:
                            dataJson = json.load(json_file)

                        # print(dataJson.get('functions',{}).keys())
                        functions_list = dataJson.get('functions', {}).keys()
                        # print("functions_list:",type(functions_list),functions_list)
                        jsonDumps = json.dumps(dataJson, indent=None)
                        functions_and_result = []
                        functions_implemented = []
                        with open(f"{rCmd.pathRootDirectory}/{logFileName}") as f:
                            logs = f.read().splitlines()
                            for lineNumber ,l in enumerate(logs):
                                d = {}
                                try:
                                    d = eval(l)
                                    if type(d) != dir:
                                        raise Exception(f"{d} no es dir")
                                except:
                                    #print(f"No se pudo evaluar la linea #{lineNumber} del archivo. Contenido: {l} ")
                                    pass
                                try:
                                    for key ,value in d.items():
                                        # print(f"Outside if: {key}:{value}")
                                        if key == 'funcName' and value in functions_list\
                                                and d.get('message') in \
                                                ["Rechazado", "S/Datos", "Aprobado", "No/Verificado"]:
                                            print(f"Inside if functions_list: {key}:{value}")
                                            print(d.get('message'))
                                            functions_implemented.append(value)
                                            functions_and_result.append((value, d.get('message')))
                                            txt1 = '#/functions/' + value
                                            txt2 = f'"{value}": "No/Verificado"'
                                            result = d.get('message')
                                            jsonDumps = jsonDumps.replace(txt1, f'{result}')
                                            jsonDumps = jsonDumps.replace(txt2, f'"{value}": "{result}"')
                                except Exception as e:
                                    print(f"{d}:, {e}")
                            print("end of file")

                        print(f"functions_implemented: {functions_implemented}")
                        for fn in functions_list:
                            if fn not in functions_implemented:
                                # print(f"Inside if functions_implemented: {fn}")
                                jsonDumps = jsonDumps.replace('#/functions/' + fn, "No/Verificado")

            # rCmd.saveReportResult(jsonDumps)

            # The data that you want to store
            data = f"/checkresult/{rCmd.t_stamp}-{dataFile[0]}-{rCmd.hash_}"
            # print(data)
            #print(dir(jsonDumps.))
            return jsonDumps, functions_and_result
        else:
            return None, response
    except Exception as e:
        print(f"Error general en process file: {e}")
        #abort(500, e)