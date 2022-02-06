import configparser
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import shutil
import sys


class ProcessBar:
    def __init__(self, total):
        self.total = total
        self.curr = 0

    def incr(self):
        self.curr = self.curr + 1

    def run(self):
        percent = round(self.curr / self.total, 2)*100
        print("\r", end="")
        print("Progress: {}{}%: ".format(
            "▋" * int(percent // 4), str(percent)[:4]), end="")
        sys.stdout.flush()


def work(root_cmd, cif_dir, cif, lock, output_file, zeo_output_dir, process_bar):
    cif_name = cif[:-4]
    cmd = root_cmd + ' ' + os.path.join(cif_dir, cif)
    LCD, PLD, density, VSA, GSA, Vp, void_fraction = 0, 0, 0, 0, 0, 0, 0
    if os.system(cmd + "> /dev/null") == 0:
        try:
            with open(os.path.join(cif_dir, cif_name + '.res')) as f:
                LCD, PLD = get_LCD_PLD(f.read())

            with open(os.path.join(cif_dir, cif_name + '.sa')) as f:
                density, VSA, GSA = get_density_VSA_GSA(f.read())

            with open(os.path.join(cif_dir, cif_name + '.vol')) as f:
                Vp, void_fraction = get_Vp_voidFraction(f.read())

            lock.acquire()
            with open(output_file, 'a') as f:
                f.write("{},{},{},{},{},{},{},{}\n".format(
                    cif_name, LCD, PLD, density, VSA, GSA, Vp, void_fraction))
            process_bar.incr()
            process_bar.run()
            lock.release()
        except Exception as e:
            lock.acquire()
            with open(output_file, 'a') as f:
                f.write("{},error\n".format(cif_name))
            process_bar.incr()
            process_bar.run()
            lock.release()
        try:
            for suffix in [".sa", ".vol", ".res"]:
                shutil.move(os.path.join(
                    cif_dir, cif_name + suffix), zeo_output_dir)
        except Exception as e:
            print(e)
            pass
    else:
        lock.acquire()
        with open(output_file, 'a') as f:
            f.write("{},error\n".format(cif_name))
        lock.release()


def get_LCD_PLD(string):
    strs = string.split()
    PLD = strs[2]
    LCD = strs[3]
    return LCD, PLD


def get_density_VSA_GSA(string):
    strs = string.split()
    density = strs[5]
    VSA = strs[9]
    GSA = strs[11]
    return density, VSA, GSA


def get_Vp_voidFraction(string):
    strs = string.split()
    void_fraction = strs[9]
    Vp = strs[11]
    return Vp, void_fraction


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

    if os.path.exists(os.path.join(cur_path, zeo_output_dir)):
        print("zeo_results目录已存在，请手动删除后重试！(The zeo_results fold already exists, please delete it and try again !)")
        exit()
    os.makedirs(zeo_output_dir)

    root_cmd = "{} -ha -res -sa {} {} {} -vol {} {} {}".format(os.path.join(
        zeo_dir, 'network'), area_radius, area_radius, area_monte_carlo_samples, volume_radius, volume_radius,
        porosity_monte_carlo_samples)

    pool = ThreadPoolExecutor(max_workers=max_threads)
    lock = Lock()
    process_bar = ProcessBar(len(cifs))
    with open(output_file, 'w') as f:
        f.write(
            'name,LCD,PLD,desity(g/cm^3),VSA(m^2/cm^3),GSA(m^2/g),Vp(cm^3/g),void_fraction\n')
    print("calculating.....")
    for cif in cifs:
        pool.submit(work, root_cmd, cif_dir, cif, lock, output_file,
                    os.path.abspath(zeo_output_dir), process_bar)

    pool.shutdown(wait=True)
    print("\033[0;30;42m\n完成！(Finish)\n\033[0m")
