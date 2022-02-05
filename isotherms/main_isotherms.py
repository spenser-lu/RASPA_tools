import configparser
import os
import random
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from functions_isotherms import work, generate_simulation_input

def check_parameters():
    cur_path = os.path.abspath(os.path.dirname(__file__))
    os.chdir(cur_path)
    config = configparser.ConfigParser()
    config.read("config.ini", encoding='utf8')
    section = "ISOTHERM_CONFIG"
    full_options = ['raspa_dir', 'cif_location',
                    'temperature', 'pressures', 'cutoffvdm', 'max_threads']
    options_in_config = config.options(section)
    missing_options = []
    option_dic = {}
    for op in full_options:
        if op not in options_in_config:
            missing_options.append(op)
        else:
            option_dic[op] = config.get(section, op)

    if len(missing_options) > 0:
        print("配置文件中参数不完整! (The parameters in the configuration file are incomplete !)")
        print("缺少的选项 (missing options) : " + str(missing_options))
        exit()

    raspa_dir = option_dic['raspa_dir']
    cif_dir = option_dic['cif_location']
    temperature = option_dic['temperature']
    pressures_str = option_dic['pressures']
    cutoffvdm = option_dic['cutoffvdm']
    max_threads = option_dic['max_threads']

    if len(raspa_dir) > 0:
        raspa_dir = os.path.abspath(raspa_dir)

    if len(cif_dir) > 0:
        cif_dir = os.path.abspath(cif_dir)

    if not os.path.exists(os.path.join(raspa_dir, "bin", "simulate")):
        print('RASPA目录无效！(Invalid RASPA_dir!)')
        exit()

    if not os.path.exists(cif_dir):
        print('cif目录无效！(Invalid cif_location!)')
        exit()

    pressures = pressures_str.split(",")
    try:
        for p in pressures:
            float(p)
    except:
        print("压力必须为数字或者使用科学计数法！(Pressures must be numerical or use scientific notation !)")
        exit()

    try:
        float(temperature)
    except:
        print("温度必须为数字！(Temperature must be numerical !)")
        exit()

    try:
        cutoffvdm = float(cutoffvdm)
    except:
        print("截断半径必须为数字！(CutOffVDM must be numerical !)")
        exit()

    try:
        max_threads = int(max_threads)
    except:
        print("线程数必须为整数！(max_threads must be integer !)")
        exit()

    if os.path.isfile(cif_dir):
        cifs = []
        cifs.append(os.path.basename(cif_dir))
        cif_dir = os.path.dirname(cif_dir)
        return raspa_dir, cif_dir, cifs, temperature, pressures, cutoffvdm, max_threads

    cifs = os.listdir(cif_dir)
    dels = []
    for cif in cifs:
        if not cif.endswith('.cif'):
            dels.append(cif)
    for s in dels:
        cifs.remove(s)
    if len(cifs) == 0:
        print('cif目录中缺乏有效的cif文件！(There are no valid cif files in the cif_location)')
        exit()

    return raspa_dir, cif_dir, cifs, temperature, pressures, cutoffvdm, max_threads


def main():
    cur_path = os.path.abspath(os.path.dirname(__file__))
    os.chdir(cur_path)
    print(sys.path[0])
    raspa_dir, cif_dir, cifs, temperature, pressures, cutoffvdm, max_threads = check_parameters()
    pool = ThreadPoolExecutor(max_workers=max_threads)
    lock = Lock()

    with open("./simulation_template.input", "r") as f:
        template = f.read()

    results_dir = os.path.join(cur_path, "results")
    if os.path.exists(results_dir):
        shutil.rmtree(results_dir)
    os.makedirs(results_dir)

    for cif in cifs:
        for pressure in pressures:
            input_text = generate_simulation_input(template=template, temperature=temperature, pressure=pressure,
                                                   cutoff=cutoffvdm, cif_dir=cif_dir, cif_file=cif)
            pool.submit(work, cif_dir, cif, raspa_dir,
                        pressure, input_text, lock)
            time.sleep(random.randint(1, 15) / 10)
    pool.shutdown(wait=True)
    print("\033[0;30;42m\n完成！(Finish)\n\033[0m")


if __name__ == '__main__':
    main()
