# RASPA_tools

适用于多孔材料吸附性质模拟软件——RASPA的Python脚本工具集合，可用于并行计算等温线、高通量模拟，zeo++参数自动化计算、批量结果分析等。

A collection of Python scripting tools for RASPA, which can be used for parallel calculation of isotherms, high-throughput simulation, automatic calculation of structural parameters, batch result analysis, etc.

## 项目结构 (Structure)

```
├── raspa_parse/   
  ├── raspa_parse.py      //用于解析RASPA输出文件的工具类

├── zeo_calculate/        //使用zeo++批量计算结构参数
  ├── config.ini          //配置文件
  ├── structral_parameters_screen.py  //用于计算结构参数的主程序

├── isotherms/       //批量计算等温线（支持多线程并行、多组分吸附）
  ├── config.ini          //配置文件
  ├── simulation_template.input    //RASPA输入文件的模板
  ├── main_isotherms.py   //计算等温线的主程序

├── high_throughput_adsorption/    //批量进行吸附模拟
  ├── config.ini          //配置文件
  ├── simulation_template.input    //RASPA输入文件的模板
  ├── main_adsorption.py   //批量进行吸附模拟的主程序
```

## 用法 (Usage)

在使用之前，请在你的电脑上安装Python运行环境，版本3.0以上。如果你在使用超算或者计算集群，**请勿**使用相应的作业管理系统（如PBS、LSF等）运行脚本。

Please install the Python runtime environment, version 3.0 or higher, on your computer before using it. If you are using supercomputing or computing clusters, **Don't** run the script using the appropriate job management system (e.g. PBS, LSF, etc.).

***

### zeo_calculate

[zeo++](http://www.zeoplusplus.org/ )是一款功能强大的多孔材料结构分析工具，此脚本可极大的简化利用zeo++计算材料的结构参数的操作，并可以批量的进行大规模高通量模拟，支持多线程，并可以自动完成对结果的汇总统计。`zeo_calculate/` 里有两个文件，其中`config.ini`为配置文件，`structral_parameters_screen.py`是运行程序的主函数。

zeo++ is a powerful tool for structural analysis of porous materials. This script greatly simplifies the operation of calculating structural parameters of materials with zeo++, and allows to perform large scale high throughput simulations in batch, supports multi-threading, and can automatically complete summary statistics of the results. There are two files in `zeo_calculate/`, `config.ini` is the configuration file, and `structral_parameters_screen.py` is the main function to run the program.

首先根据自己的需求更改`config.ini`中的参数，注意`zeo++_dir`最好使用绝对路径，`number_of_threads`建议设定为电脑的核心数。

First, change the parameters in `config.ini` to suit your needs, note that `zeo++_dir` is best set to absolute path, and `number_of_threads` is recommended to be set to the number of cores in your computer.

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

接下来运行`structral_parameters_screen.py`，注意要和`config.ini`在一个目录下，可以使用VS Code或Pycharm等IDE，或者直接在终端运行：

Next, run `structral_parameters_screen.py`, note that it should be in the same directory as `config.ini`, you can use IDE such as VS Code or Pycharm, or run it directly in the terminal:

```shell
python structral_parameters_screen.py
```

如果配置正确的话，程序会显示进度条，结束之后会在控制台输出"Finish !"，此时可以在当前目录下看到`result.csv`和`zeo_results`，分别是计算结果汇总和zeo++的输出文件。

If the configuration is correct, the program will display a progress bar and output "Finish !" in the console when it finishes, you can see `result.csv` and `zeo_results` in the current directory, which are the summary of the calculation results and the output file of zeo++, respectively.

***

### raspa_parse

`raspa_parse.py`提供了简洁友好的API，用于解析RASPA输出文件。`RASPA_Output_Data`是核心类，封装了一系列解析方法，其构造器需传入RASPA输出文件的字符串作为参数。

`raspa_parse.py` provides concise and friendly APIs for parsing RASPA output files. `RASPA_Output_Data` is the core class that encapsulates a set of parsing methods. Its constructor takes a string as an argument from the RASPA output file.

| Method                        | Parameter                                                                                                                   | Function                                                                                                                                                         | Return Value                                                                                                   |
|:-----------------------------:|:---------------------------------------------------------------------------------------------------------------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------:|:--------------------------------------------------------------------------------------------------------------:|
| get_components()              | None                                                                                                                        | get components in the output file                                                                                                                                | List[string: component name]                                                                                   |
| is_finished()                 | None                                                                                                                        | Determine whether the output file is finished                                                                                                                    | True if done, False otherwise                                                                                  |
| get_warnings()                | None                                                                                                                        | get warnings in the output file                                                                                                                                  | List[string: warning name]                                                                                     |
| get_pressure()                | None                                                                                                                        | get pressure of output file                                                                                                                                      | string:pressure,the unit is Pa                                                                                 |
| get_absolute_adsorption(unit) | unit:The unit of adsorption capacity, optional values:"mol/uc","cm\^3/g","mol/kg","mg/g","cm\^3/cm\^3",default is "cm\^3/g" | get absolute adsorption capacities                                                                                                                               | Dict:{component_name:adsorption_capacity}                                                                      |
| get_excess_adsorption(unit)   | unit:The unit of adsorption capacity, optional values:"mol/uc","cm\^3/g","mol/kg","mg/g","cm\^3/cm\^3",default is "cm\^3/g" | get excess adsorption capacities, If `HeliumViodFraction` is not specified in the `simulation.input`,  the result is the same as `get_absolute_adsorption(unit)` | Dict:{component_name:adsorption_capacity}                                                                      |
| get_adsorption_heat()         | None                                                                                                                        | get adsorption heat (KJ/mol) of components in the output file                                                                                                    | Dict:{component_name:heat}                                                                                     |
| get_henry_coefficient()       | None                                                                                                                        | get adsorption heat (mol/kg/Pa) of components in the output file                                                                                                 | Dict:{component_name:heat}                                                                                     |
| get_all_adsorption_result     | None                                                                                                                        | Obtain adsorption data for each component in each unit, including absolute and excess adsorption capacities                                                      | Dict, the keys are "{component_name}_absolute_{unit}", "{component_name}_excess_{unit}", "finished" and "warnings" |

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

You can use `RASPA_Output_Data` for quick batch result statistics. Note that when the output file is large, it will consume a lot of memory

***

### isotherms

RASPA 默认情况下只能使用单核计算吸附，但是可以同时提交多个压力点的任务来实现多线程计算等温线。`main_isotherms.py` 可以自动化的完成上述过程，并快速进行结果汇总（基于`RASPA_Output_Data`），对于多组分吸附的输出文件也能正常解析。

RASPA can only use single-core computing adsorption by default, but can submit tasks for multiple pressure points at the same time to achieve multi-threads computing isotherms. `main_isotherms.py` can automate the above process and quickly summarize the results (based on `RASPA_Output_Data`), and can also parse the output file of multi-components adsorption normally.

首先，根据自己的需求更改`config.ini`中的参数，注意`RSAPA_dir`最好使用绝对路径，`max_threads`建议设定为电脑的核心数。

First, change the parameters in `config.ini` according to your needs. Note that `RSAPA_dir` is best set to an absolute path, and `max_threads` is recommended to be set to the number of cores of your computer.

```ini
[ISOTHERM_CONFIG]

# RASPA的安装目录，即/bin, /lib, /share所在目录
# The installation directory of RASPA, that is, the directory where /bin, /lib, /share are located
RASPA_dir = /usr/local/RASPA

# 如果只有1个cif需要计算，设定为cif文件所在位置，
# 如果有多个cif需要计算，设定为cif文件所在目录，程序会遍历目录中所有的cif文件并计算等温线
# If only one CIF needs to be calculated, set this parameter to the location of the CIF file.
# If multiple CIFs need to be calculated, set this parameter to the directory of the CIF files.
# The program will traverse all CIF files in the directory and calculate isotherms
cif_location = ../test_cifs/

# 建议设定为cpu的核心数
# Set this parameter to the number of CPU cores on your computer
max_threads = 10

# 温度的单位是K (The unit is kelvin)
temperature = 298

# 压力的单位是Pa, 可以使用科学计数法，数字之间以英文逗号(",")分隔
# The unit of pressure is Pascal, scientific notation can be used,
# and the numbers are separated by commas (",")
pressures = 100,300,500,1000,5000,10000,5e4,1e5

# 范德华力的截断半径，单位是埃
# Cutoff radius of van der Waals force in Angstroms
CutOffVDM = 12.0
```

接下来，修改`simulation_template.input`，你可以根据计算需求增加、删除或修改一些RASPA参数，程序会根据此模板动态生成RASPA的输入文件——`simulation.input`。***请注意，下面这几行不能修改***：

Next, modify `simulation_template.input`, you can add, delete or modify some RASPA parameters according to the calculation requirements, and the program will dynamically generate the RASPA input file - `simulation.input` - based on this template. ***Please note that the following lines cannot be modified***.

```
FrameworkName {cif_name}
CutOffVDW {cutoff}
UnitCells {unitcell}
ExternalTemperature {temperature}
ExternalPressure {pressure}
```

最后，运行`main_isotherms.py`，注意要和`config.ini`，`simulation_template.input`在一个目录下，可以使用VS Code或Pycharm等IDE，或者直接在终端运行：

Finally, run `main_isotherms.py`, note that it must be in the same directory as `config.ini`, `simulation_template.input`, you can use IDE such as VS Code or Pycharm, or run it directly in the terminal:

```shell
python main_isotherms.py
```

在程序运行过程中，控制台会输出RASPA的日志，当前目录下会出现`RASPA_Output`和`results`文件夹，里面是分别是RASPA的输出文件和结果汇总文件。运行结束时，控制台会输出"Finish!"。

During the running of the program, the console will output the RASPA log, and the `RASPA_Output` and `results` folders will appear in the current directory, which are the RASPA output files and the result summary files respectively. At the end of the run, the console will output "Finish!".

***

### high_throughput_adsorption

有时我们需要对大量的材料进行吸附模拟，这时候此脚本就会派上用场。笔者对上述的`main_isotherms.py`稍作修改，便有了`main_adsorption.py`，支持多线程并行模拟多个材料，并自动完成对模拟结果的汇总，同样支持多组分吸附。

Sometimes we need to perform adsorption simulations on a large number of materials, and this is where this script comes in handy.  I modified the above `main_isotherms.py` a little bit, then there is `main_adsorption.py`, which supports multi-threads parallel simulation of multiple materials, and automatically completes the aggregation of simulation results, also supports multi-components adsorption.

它的使用方法与`main_isotherms.py`很接近。首先，根据自己的需求更改`config.ini`中的参数，注意`RSAPA_dir`最好使用绝对路径，`max_threads`建议设定为电脑的核心数。

Its usage is very close to `main_isotherms.py`. First, change the parameters in `config.ini` according to your needs. Note that `RSAPA_dir` is best set to an absolute path, and `max_threads` is recommended to be set to the number of cores of your computer.

```ini
[ADSORPTION_CONFIG]

# RASPA的安装目录，即/bin, /lib, /share所在目录
# The installation directory of RASPA, that is, the directory where /bin, /lib, /share are located
RASPA_dir = /usr/local/RASPA

# 设定为cif文件所在目录，程序会遍历目录中所有的cif文件并使用RASPA进行吸附模拟
# Set this parameter to the directory of the CIF files.
# The program will traverse all the cif files in the directory and use RASPA for adsorption simulation
cif_location = ../test_cifs/

# 建议设定为cpu的核心数
# Set this parameter to the number of CPU cores on your computer
max_threads = 10

# 范德华力的截断半径，单位是埃
# Cutoff radius of van der Waals force in Angstroms
CutOffVDM = 12.0
```

接下来，修改`simulation_template.input`，你可以根据计算需求增加、删除或修改一些RASPA参数，程序会根据此模板动态生成RASPA的输入文件——`simulation.input`。***请注意，下面这几行不能修改***：

Next, modify `simulation_template.input`, you can add, delete or modify some RASPA parameters according to the calculation requirements, and the program will dynamically generate the RASPA input file - `simulation.input` - based on this template. ***Please note that the following lines cannot be modified***.

```
FrameworkName {cif_name}
CutOffVDW {cutoff}
UnitCells {unitcell}
```

最后，运行`main_adsorption.py`，注意要和`config.ini`，`simulation_template.input`在一个目录下，可以使用VS Code或Pycharm等IDE，或者直接在终端运行：

Finally, run `main_adsorption.py`, note that it must be in the same directory as `config.ini`, `simulation_template.input`, you can use IDE such as VS Code or Pycharm, or run it directly in the terminal:

```shell
python main_adsorption.py
```

在程序运行过程中，控制台会输出RASPA的日志，当前目录下会出现`RASPA_Output`文件夹和`adsorption_results.csv`文件，分别是RASPA的输出文件和结果汇总文件。运行结束时，控制台会输出"Finish!"。

During the running process of the program, the console will output the RASPA log, and the `RASPA_Output` folder and the `adsorption_results.csv` file will appear in the current directory, which are the RASPA output files and the result summary file respectively. At the end of the run, the console will output "Finish!".
