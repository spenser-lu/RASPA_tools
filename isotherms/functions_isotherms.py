import math
import os
import re
import shutil
from threading import Lock

class RASPA_Output_Data():
    '''
        RASPA输出文件对象
    '''
    '''
    示例：
        with open('./output.data','r') as f:
            str = f.read()
        output = RASPA_Output_Data(str)
        print(output.is_finished())
        print(output.get_absolute_adsorption())

    '''
    def __init__(self, output_string):
        '''
            初始化时传入RASPA输出文件的字符串
        '''
        self.output_string = output_string
        self.components = re.findall(
            r'Component \d+ \[(.*)\] \(Adsorbate molecule\)', self.output_string)

    def get_components(self):
        return self.components

    def is_finished(self):
        '''
            返回该任务是否已完成
        '''
        pattern = r'Simulation finished'
        result = re.findall(pattern, self.output_string)
        return len(result) > 0

    def get_warnings(self):
        '''
            返回存储警告信息的列表
        '''
        if len(re.findall(r'0 warnings', self.output_string)) > 0:
            return []
        pattern = r'WARNING: (.*)\n'
        return list(set(re.findall(pattern, self.output_string)))

    def get_pressure(self):
        '''
            返回压力，单位是Pa
        '''
        pattern = r'Pressure:\s+(.*)\s+\[Pa\]'
        result = re.findall(pattern, self.output_string)
        return result[0]

    def get_excess_adsorption(self, unit='cm^3/g'):
        '''
            指定单位，返回超额吸附量，返回值是一个字典，键是吸附质的名称，值是吸附量
            若不指定单位，默认为cm^3/g
            unit: 'mol/uc','cm^3/g','mol/kg','mg/g','cm^3/cm^3'
        '''
        patterns = {'mol/uc': r"Average loading excess \[molecules/unit cell\]\s+(\d+\.?\d*)\s+",
                    'cm^3/g': r"Average loading excess \[cm\^3 \(STP\)/gr framework\]\s+(\d+\.?\d*)\s+",
                    'mol/kg': r"Average loading excess \[mol/kg framework\]\s+(\d+\.?\d*)\s+",
                    'mg/g': r"Average loading excess \[milligram/gram framework\]\s+(\d+\.?\d*)\s+",
                    'cm^3/cm^3': r"Average loading excess \[cm\^3 \(STP\)/cm\^3 framework\]\s+(\d+\.?\d*)\s+"
                    }
        if unit not in patterns.keys():
            raise ValueError('单位错误！')
        result = {}
        data = re.findall(patterns[unit], self.output_string)
        for i, j in zip(self.components, data):
            result[i] = j
        return result

    def get_absolute_adsorption(self, unit='cm^3/g'):
        '''
            指定单位，返回绝对吸附量，返回值是一个字典，键是吸附质的名称，值是吸附量;
            若不指定单位，默认为cm^3/g
            unit: 'mol/uc','cm^3/g','mol/kg','mg/g','cm^3/cm^3'
        '''
        patterns = {'mol/uc': r"Average loading absolute \[molecules/unit cell\]\s+(\d+\.?\d*)\s+",
                    'cm^3/g': r"Average loading absolute \[cm\^3 \(STP\)/gr framework\]\s+(\d+\.?\d*)\s+",
                    'mol/kg': r"Average loading absolute \[mol/kg framework\]\s+(\d+\.?\d*)\s+",
                    'mg/g': r"Average loading absolute \[milligram/gram framework\]\s+(\d+\.?\d*)\s+",
                    'cm^3/cm^3': r"Average loading absolute \[cm\^3 \(STP\)/cm\^3 framework\]\s+(\d+\.?\d*)\s+"
                    }
        if unit not in patterns.keys():
            raise ValueError('单位错误！')
        result = {}
        data = re.findall(patterns[unit], self.output_string)
        for i, j in zip(self.components, data):
            result[i] = j
        return result

    def get_adsorption_heat(self):
        '''
            返回吸附热(KJ/mol)
            返回值是一个字典，键是吸附质的名称，值是吸附热;
        '''
        result = {}
        if len(self.components) > 1:
            pattern = r'Component \d+ \[(.*)\]\n\s*-*\n.*\n.*\n.*\n.*\n.*\n\s*-*\n.*\n\s+(\-?\d+\.?\d*)\s'
        else:
            pattern = r'Enthalpy of adsorption:\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n\s+(\-?\d+\.?\d*)\s'
        data = re.findall(pattern, self.output_string)
        for i, j in zip(self.components, data):
            result[i] = j
        return result

    def get_henry_coefficient(self):
        '''
            返回亨利系数(mol/kg/Pa)
            返回值是一个字典，键是吸附质的名称，值是亨利系数;
        '''
        pattern = r'\[.*\]\s+Average Henry coefficient:\s+(\d+\.?\d*)\s+'
        data = re.findall(pattern, self.output_string)
        result = {}
        for i, j in zip(self.components, data):
            result[i] = j
        return result


def get_unit_cell(cif_location, cutoff):
    with open(cif_location, 'r') as f:
        text = f.readlines()
    for i in text:
        if (i.startswith('_cell_length_a')):
            a = float(i.split()[-1].strip().split('(')[0])
        elif (i.startswith('_cell_length_b')):
            b = float(i.split()[-1].strip().split('(')[0])
        elif (i.startswith('_cell_length_c')):
            c = float(i.split()[-1].strip().split('(')[0])
        elif (i.startswith('_cell_angle_alpha')):
            alpha = float(i.split()[-1].strip().split('(')[0])
        elif (i.startswith('_cell_angle_beta')):
            beta = float(i.split()[-1].strip().split('(')[0])
        elif (i.startswith('_cell_angle_gamma')):
            gamma = float(i.split()[-1].strip().split('(')[0])
            break
    pi = 3.1415926

    a_length = a * math.sin(beta / 180 * pi)
    b_length = b * math.sin(gamma / 180 * pi)
    c_length = c * math.sin(alpha / 180 * pi)

    a_unitcell = int(2 * cutoff / a_length + 1)
    b_unitcell = int(2 * cutoff / b_length + 1)
    c_unitcell = int(2 * cutoff / c_length + 1)

    return "{} {} {}".format(a_unitcell, b_unitcell, c_unitcell)


def generate_simulation_input(template: str, temperature: str, pressure: str, cutoff: float, cif_dir: str,
                              cif_file: str):
    unitcell = get_unit_cell(os.path.join(cif_dir, cif_file), cutoff)
    cif_name = cif_file[:-4]
    return template.format(cif_name=cif_name, cutoff=cutoff, unitcell=unitcell, temperature=temperature,
                           pressure=pressure)


def work(cif_dir: str, cif_file: str, RASPA_dir: str, pressure: str, input_text: str, lock: Lock):
    cif_name = cif_file[:-4]
    curr_dir = os.path.abspath(os.path.dirname(__file__))
    result_file = os.path.join(curr_dir, "results", cif_name + "_result.csv")
    components = get_components_from_input(input_text)
    headers = get_field_headers(components)
    lock.acquire()
    if not os.path.exists(result_file):
        with open(result_file, 'w') as f:
            for i in range(len(headers)):
                if i != len(headers) - 1:
                    f.write(headers[i] + ",")
                else:
                    f.write(headers[i] + "\n")

    if not os.path.exists(os.path.join(curr_dir, cif_name)):
        os.makedirs(os.path.join(curr_dir, cif_name))
    lock.release()
    cmd_dir = os.path.join(curr_dir, cif_name, pressure)
    if not os.path.exists(cmd_dir):
        os.makedirs(cmd_dir)
    shutil.copy(os.path.join(cif_dir, cif_file), cmd_dir)
    cmd = os.path.join(RASPA_dir, "bin", "simulate") + " simulation.input"
    os.chdir(cmd_dir)
    with open("simulation.input", "w") as f1:
        f1.write(input_text)
        f1.close()
    if os.system(cmd) == 0:
        lock.acquire()
        try:
            output_file = os.listdir(os.path.join(cmd_dir, "Output", "System_0"))[0]
            with open(os.path.join(cmd_dir, "Output", "System_0",output_file), 'r') as f2:
                result = get_result(f2.read(), components)
                f2.close()
            write_result(result_file, result, headers)
            print("\033[0;30;42m\n{}__{} has completed\n\033[0m".format(cif_name, pressure))
        except Exception as e:
            write_error(result_file, pressure)
            print("\033[0;37;41m\n{}__{} error: {} !\n\033[0m".format(cif_name, pressure, e))
        lock.release()
    else:
        lock.acquire()
        write_error(result_file, pressure)
        print("\033[0;37;41m\n{}__{} error !\n\033[0m".format(cif_name, pressure))
        lock.release()

def get_result(output_str: str, components: list):
    res = {}
    units = ['mol/uc', 'cm^3/g', 'mol/kg', 'mg/g', 'cm^3/cm^3']
    output = RASPA_Output_Data(output_str)
    res["pressure"] = output.get_pressure()
    res["finished"] = str(output.is_finished())
    res["warning"] = ""
    if res["finished"] == 'True':
        for w in output.get_warnings():
            res["warning"] += (w + "; ")

        for unit in units:
            absolute_capacity = output.get_absolute_adsorption(unit=unit)
            excess_capacity = output.get_excess_adsorption(unit=unit)
            for c in components:
                res[c + "_absolute_" + unit] = absolute_capacity[c]
                res[c + "_excess_" + unit] = excess_capacity[c]
    else:
        for unit in units:
            for c in components:
                res[c + "_absolute_" + unit] = " "
                res[c + "_excess_" + unit] = " "
    return res


def get_field_headers(components: list):
    headers = ["pressure", "finished"]
    units = ['mol/uc', 'cm^3/g', 'mol/kg', 'mg/g', 'cm^3/cm^3']
    for i in ["absolute", "excess"]:
        for j in components:
            for unit in units:
                headers.append(j + "_" + i + "_" + unit)
    headers.append("warning")
    return headers


def get_components_from_input(input_text: str):
    components = re.findall(r'MoleculeName\s+(.+)', input_text)
    return components


def write_result(result_file, result: dict, headers: list):
    with open(result_file, 'a') as f:
        for i in range(len(headers)):
            if i != len(headers) - 1:
                f.write(result[headers[i]] + ",")
            else:
                f.write(result[headers[i]] + "\n")
        f.close()

def write_error(result_file, pressure):
    with open(result_file, 'a') as f:
        f.write(pressure + ",error,\n")
        f.close()

