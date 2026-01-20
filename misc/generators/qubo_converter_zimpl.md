# Zimpl File Converter LP to QUBO (@Thorsten comment on other formats supported?)

[Github repo](https://github.com/JuliaQUBO/QUBO.jl)
[Zimpl user guide](https://zimpl.zib.de/download/zimpl.pdf)

## Installation

1. Install Zimpl. The newest version is available under this [link](https://zimpl.zib.de/index.php#download).

2. Install GMP. The newest version can be found [here](https://gmplib.org/#DOWNLOAD).

## Execution

1. Move to folder with problem description (@Thorsten what formats are supported?)
2. Convert file into a format that Zimpl can work with
```shell
awk -f ../misc/todat.awk [source_path] > [output_file_name].txt
```
5. Convert problem into QUBO
```shell
[path_to_zimpl]/zimpl-3.6.1.darwin.x86_64.gnu.static.opt -tq -o [output_file_name] -Dfilename=[output_file_name].txt
[path_to_original_model?]
```
-tq: defines QUBO output
<\br>
-o [output_file_name]: instantiates that output will be a [output_file_name].qs file
