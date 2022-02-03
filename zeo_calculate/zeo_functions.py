import os
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
        print("Progress: {}{}%: ".format("▋" * int(percent // 4),percent), end="")
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
                f.write("{},{},{},{},{},{},{},{}\n".format(cif_name, LCD, PLD, density, VSA, GSA, Vp, void_fraction))
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
                shutil.move(os.path.join(cif_dir, cif_name + suffix), zeo_output_dir)
        except Exception as e:
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
