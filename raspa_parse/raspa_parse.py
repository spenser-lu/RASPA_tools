import re

'''
示例：
    with open('./output.data','r') as f:
        str = f.read()
    output = RASPA_Output_Data(str)
    print(output.is_finished())
    print(output.get_absolute_adsorption())

'''


class RASPA_Output_Data():
    '''
        RASPA输出文件对象
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
