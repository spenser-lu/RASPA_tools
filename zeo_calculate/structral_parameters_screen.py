import configparser
import os
from concurrent.futures import ThreadPoolExecutor
from zeo_functions import work, ProcessBar
from threading import Lock


if __name__ == "__main__":
    cur_path = os.path.abspath(os.path.dirname(__file__))
    os.chdir(cur_path)
    config = configparser.ConfigParser()
    config.read("config.ini", encoding='utf8')
    section = "ZEO_CONFIG"
    full_options = ['zeo++_dir', 'cif_dir', 'number_of_threads', 'radius_of_area_probe', 'radius_of_porosity_probe',
                    'area_monte_carlo_samples', 'porosity_monte_carlo_samples', 'output_file_name']
    options_in_config = config.options(section)
    missing_options = []
    option_dic = {}
    for op in full_options:
        if op not in options_in_config:
            missing_options.append(op)
        else:
            option_dic[op] = config.get(section, op)

    if len(missing_options) > 0:
        print("配置文件中参数不完整！（The parameters in the configuration file are incomplete!）")
        print("缺少的选项（missing options）： " + str(missing_options))
        exit()

    zeo_dir = option_dic["zeo++_dir"]
    cif_dir = option_dic["cif_dir"]
    max_threads = int(option_dic["number_of_threads"])
    area_radius = option_dic["radius_of_area_probe"]
    volume_radius = option_dic["radius_of_porosity_probe"]
    area_monte_carlo_samples = option_dic["area_monte_carlo_samples"]
    porosity_monte_carlo_samples = option_dic["porosity_monte_carlo_samples"]
    output_file = option_dic["output_file_name"]
    zeo_output_dir = "zeo_results"

    if len(zeo_dir) > 0:
        zeo_dir = os.path.abspath(zeo_dir)

    if len(cif_dir) > 0:
        cif_dir = os.path.abspath(cif_dir)

    if not os.path.isfile(os.path.join(zeo_dir, 'network')):
        print('zeo++目录无效！(Invalid zeo++_dir!)')
        exit()

    if not os.path.isdir(cif_dir):
        print('cif目录无效！(Invalid cif_dir!)')
        exit()

    cifs = os.listdir(cif_dir)
    dels = []
    for cif in cifs:
        if not cif.endswith('.cif'):
            dels.append(cif)

    for s in dels:
        cifs.remove(s)
    if len(cifs) == 0:
        print('cif目录中缺乏有效的cif文件！(There are no valid cif files in the cif_dir)')
        exit()

    if not os.path.exists(os.path.join(cur_path, zeo_output_dir)):
        os.makedirs(zeo_output_dir)

    root_cmd = "{} -ha -res -sa {} {} {} -vol {} {} {}".format(os.path.join(
        zeo_dir, 'network'), area_radius, area_radius, area_monte_carlo_samples, volume_radius, volume_radius,
        porosity_monte_carlo_samples)

    pool = ThreadPoolExecutor(max_workers=max_threads)
    lock = Lock()
    process_bar = ProcessBar(len(cifs))
    with open(output_file,'w') as f:
        f.write('name,LCD,PLD,desity(g/cm^3),VSA(m^2/cm^3),GSA(m^2/g),Vp(cm^3/g),void_fraction\n')

    for cif in cifs:
        pool.submit(work, root_cmd, cif_dir, cif, lock, output_file, os.path.abspath(zeo_output_dir), process_bar)

    pool.shutdown(wait=True)
    print("\033[0;30;42m\n完成！(Finish)\n\n\033[0m")
