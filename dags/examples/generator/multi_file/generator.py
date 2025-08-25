import os, fileinput, shutil, json

DAGS_FOLDER = "/usr/local/airflow/dags"
module_path = f"{DAGS_FOLDER}/examples/generator/multi_file"
config_filepath = f"{module_path}/configs/"
generated_dags_path = f"{DAGS_FOLDER}/examples/generated_dags"

generated_dags = []

for filename in os.listdir(config_filepath):
    f = open(config_filepath + filename)
    config = json.load(f)

    new_filename =  f"{generated_dags_path}/{config["dag_id"]}.py"
    shutil.copyfile(f"{module_path}/template.py", new_filename)

    for line in fileinput.input(new_filename, inplace=True):
        line = line.replace("dag_id_to_replace", "'" + config["dag_id"] + "'")
        line = line.replace("schedule_to_replace", config["schedule"])
        line = line.replace("bash_command_to_replace", config["bash_command"])
        line = line.replace("env_var_to_replace", config["env_var"])
        print(line, end="")

    generated_dags.append(f"{config["dag_id"]}.py")

for filename in os.listdir(generated_dags_path):
    if filename not in generated_dags:
        os.remove(f"{generated_dags_path}/{filename}")
