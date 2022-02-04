# RASPA_tools
适用于多孔材料吸附性质模拟软件——RASPA的Python脚本工具集合，可用于并行计算等温线、高通量模拟，zeo++参数自动化计算、批量结果分析等。

A collection of Python scripting tools for RASPA, which can be used for parallel calculation of isotherms, high-throughput simulation, automatic calculation of structural parameters, batch result analysis, etc.

## 项目结构 (Structure)
```
├── raspa_parse/   
  ├── raspa_parse.py      //用于解析RASPA输出文件的工具类
├── zeo_calculate/        //使用zeo++计算结构参数
  ├── config.ini          //配置文件
  ├── zeo_functions.py    //一些工具类和函数的封装
  ├── structral_parameters_screen.py  //用于计算结构参数的主程序

```
## 用法 (Usage)
在使用之前，请在你的电脑上安装Python运行环境，版本3.0以上。

Please install the Python 3.0 or higher version on your computer before using it.

### zeo_calculate
zeo++是一款功能强大的多孔材料结构分析工具，此脚本可极大的简化利用zeo++计算材料的结构参数的操作，并可以批量的进行大规模高通量模拟，支持多线程，并可以自动完成对结果的汇总统计。`zeo_calculate/` 里有三个文件，其中`config.ini`为配置文件，`zeo_functions.py`为一些工具类和函数的集合，`structral_parameters_screen.py`是运行程序的主函数。

zeo++ is a powerful tool for structural analysis of porous materials. This script greatly simplifies the operation of calculating structural parameters of materials with zeo++, and allows to perform large scale high throughput simulations in batch, supports multi-threading, and can automatically complete summary statistics of the results. There are three files in `zeo_calculate/`, `config.ini` is the configuration file, `zeo_functions.py` is a collection of tool classes and functions, and `structral_parameters_screen.py` is the main function to run the program.

首先根据自己的需求更改`config.ini`中的参数，注意`zeo++_dir`和`cif_dir`最好使用绝对路径，`number_of_threads`建议设定为电脑的核心数。

First, change the parameters in `config.ini` to suit your needs, note that `zeo++_dir` and `cif_dir` are best set to absolute paths, and `number_of_threads` is recommended to be set to the number of cores in your computer.

```ini
[ZEO_CONFIG]
# zeo++ 的安装目录（The installation directory of zeo++）
zeo++_dir = /home/luxiuyang/zeo++-0.3

# 需要计算的材料的cif文件所在目录（The CIF files directory of the materials to be calculated）
cif_dir = /home/luxiuyang/RASPA_tools/test_cifs

# CPU核心数（Number of CPU cores on your computer）
number_of_threads = 10

# 计算比表面积所用的分子探针半径（Molecular probe radius used to calculate specific surface area）
radius_of_area_probe = 0

# 计算孔隙率、孔体积所用的分子探针半径（Molecular probe radius used to calculate porosity）
radius_of_porosity_probe = 0

# 用于计算比表面积的蒙特卡洛采样次数，大多数情况下无需更改
#（The number of Monte Carlo samples used to calculate the specific surface area,
# in most cases does not need to be changed）
area_monte_carlo_samples = 2000

# 用于计算孔隙率的蒙特卡洛采样次数，大多数情况下无需更改
#（The number of Monte Carlo samples used to calculate the porosity,
# in most cases does not need to be changed）
porosity_monte_carlo_samples = 100000

# 输出文件的名称，大多数情况下无需更改（The name of the output file, in most cases does not need to be changed）
output_file_name = result.csv
```
接下来运行`structral_parameters_screen.py`，注意要和`config.ini`，`zeo_functions.py`在一个目录下，可以使用VS Code或Pycharm等IDE，或者直接在终端运行：

Next, run `structral_parameters_screen.py`, note that it should be in the same directory as `config.ini`, `zeo_functions.py`, you can use IDE such as VS Code or Pycharm, or run it directly in the terminal:

```shell
python structral_parameters_screen.py
```

如果配置正确的话，程序会显示进度条，结束之后会在控制台输出"Finish !"，此时可以在当前目录下看到`result.csv`和`zeo_results`，分别是计算结果汇总和zeo++的输出文件。

If the configuration is correct, the program will display a progress bar and output "Finish !" in the console when it finishes, you can see `result.csv` and `zeo_results` in the current directory, which are the summary of the calculation results and the output file of zeo++, respectively.

### raspa_parse
`raspa_parse.py`提供了简洁友好的API，用于解析RASPA输出文件。`RASPA_Output_Data`是核心类，封装了一系列解析方法，其构造器需传入RASPA输出文件的字符串作为参数。

`raspa_parse.py` provides concise and friendly APIs for parsing RASPA output files. `RASPA_Output_Data` is the core class that encapsulates a set of parsing methods. Its constructor takes a string as an argument from the RASPA output file.

|Method|Parameter|Function|Return Value|
| ---- | ---- | ---- | ---- |
get_components()|None|get components in the output file|List[string: component name]|
|is_finished()|None|Determine whether the output file is finished|True if done, False otherwise|
|get_warnings()|None|get warnings in the output file|List[string: warning name]|
|get_pressure()|None|get pressure of output file|string:pressure,the unit is Pa|
|get_absolute_adsorption(unit)|unit:The unit of adsorption capacity, optional values:"mol/uc","cm\^3/g","mol/kg","mg/g","cm\^3/cm\^3",default is "cm\^3/g"|get absolute adsorption capacities|Dict:{component_name:adsorption_capacity}|
|get_excess_adsorption(unit)|unit:The unit of adsorption capacity, optional values:"mol/uc","cm\^3/g","mol/kg","mg/g","cm\^3/cm\^3",default is "cm\^3/g"|get excess adsorption capacities, If `HeliumViodFraction` is not specified in the `simulation.input`,  the result is the same as `get_absolute_adsorption(unit)` |Dict:{component_name:adsorption_capacity}|
|get_adsorption_heat()|None|get adsorption heat (KJ/mol) of components in the output file|Dict:{component_name:heat}|
|get_henry_coefficient()|None|get adsorption heat (mol/kg/Pa) of components in the output file|Dict:{component_name:heat}|

#### 示例 (example)
`RASPA_Output_Data`的构造器需传入RASPA输出文件的字符串作为参数。

`RASPA_Output_Data` 's constructor takes a string as an argument from the RASPA output file.

```python
from raspa_parse import RASPA_Output_Data
with open('./your_output.data','r') as f:
    raspa_str = f.read()
output = RASPA_Output_Data(raspa_str)
print(output.is_finished())
print(output.get_absolute_adsorption())

```
你可以借助`RASPA_Output_Data`进行快速的批量结果统计，注意当输出文件很大时，会很耗费内存。

You can use `RASPA_Output_Data` for quick batch result statistics. Note that when the output file is large, it will consume a lot of memory.



