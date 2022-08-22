import os
from zipfile import ZipFile
from datetime import datetime
from pytz import timezone

import json
from git import Repo
import shutil
from .lib_route_command import RouteCommand


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


def upload_file_view(r_cmd: RouteCommand):
    try:
        cmd = r_cmd.cmd
        print("to execute")
        repodir = os.path.join(r_cmd.pathRootDirectory, "git_tmp")
        clone_repo(repodir)
        response = r_cmd.execute(cmd, cwd=repodir)
        print("executed")
        # print(response)
        print(sorted(os.listdir(r_cmd.pathRootDirectory)))
        copy_and_delete_data(repodir, r_cmd.pathRootDirectory)
        data_file = [f for f in sorted(os.listdir(r_cmd.pathRootDirectory)) if (str(f))[-9:] == "_Data.zip"]
        print(data_file)
        if data_file:
            with ZipFile(f"{os.path.join(r_cmd.pathRootDirectory, data_file[0])}") as zipfile:
                for zipinfo in zipfile.filelist:
                    if (str(zipinfo.filename))[-4:] == ".txt":
                        log_fileName = zipinfo.filename
                        zipfile.extract(log_fileName, path=f'{r_cmd.pathRootDirectory}')
                        print("extracted log file")
                        with open(os.path.join(r_cmd.pathRootDirectory, "jsonDataResult.json")) as json_file:
                            dataJson = json.load(json_file)

                        # print(dataJson.get('functions',{}).keys())
                        functions_list = dataJson.get('functions', {}).keys()
                        # print("functions_list:",type(functions_list),functions_list)
                        json_dumps = json.dumps(dataJson, indent=None)
                        functions_and_result = []
                        functions_implemented = []
                        with open(f"{r_cmd.pathRootDirectory}/{log_fileName}") as f:
                            logs = f.read().splitlines()
                            for lineNumber, l in enumerate(logs):
                                d = {}
                                try:
                                    d = eval(l)
                                    if type(d) != dir:
                                        raise Exception(f"{d} no es dir")
                                except:
                                    #print(f"No se pudo evaluar la linea #{lineNumber} del archivo. Contenido: {l} ")
                                    pass
                                try:
                                    for key, value in d.items():
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
                                            json_dumps = json_dumps.replace(txt1, f'{result}')
                                            json_dumps = json_dumps.replace(txt2, f'"{value}": "{result}"')
                                except Exception as e:
                                    print(f"{d}:, {e}")
                            print("end of file")

                        print(f"functions_implemented: {functions_implemented}")
                        for fn in functions_list:
                            if fn not in functions_implemented:
                                # print(f"Inside if functions_implemented: {fn}")
                                json_dumps = json_dumps.replace('#/functions/' + fn, "No/Verificado")

            return json_dumps, functions_and_result
        else:
            return None, response
    except Exception as e:
        print(f"Error general en process file: {e}")
        # abort(500, e)
