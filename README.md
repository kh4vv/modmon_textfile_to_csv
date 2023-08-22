# modmon_textfile_to_csv
 
Build package to translate modmon textfile to csv files.

The detail document can be found [HERE](https://github.com/kh4vv/modmon_textfile_to_csv/blob/main/Modmon_Data_Format_Documentation.pdf).

Run the package:

`python genFile.py "file location"`

File location is defaulted to the same directory. 

If there is no readable file (modbus files), the script will be ended and you have to re-run the command with a valid file location.

Once, the script finds the files, it will ask the output path route. You can write the directory where the new files are saved. It will create one if there is no directory.
