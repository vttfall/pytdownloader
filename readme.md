# Pytdownloader
A simple GUI for download videos and audios.    
**Made for remembering POO, tkinter, composables but with classes and testing pytube.*

**Linux setup (debian 12)**
```shell
# The version of python recommended to use is the same as mine
$ python3 --version
Python 3.11

# If you already have python installed, omit python3 in the next
$ sudo apt install python3 python3-pip python3-venv python3-tk        
```

**Setup virtual environment**   
*I don't recommend using virtual environment with anaconda due to problems in its tkinter package, in other cases I think anaconda is great.*
*[More details, here](https://stackoverflow.com/questions/49187741/tkinter-looks-extremely-ugly-in-linux)*.
```shell
# GNU Linux
$ python3 -m venv pytdenv
$ source pytdenv/bin/activate
$ pip install -r requirements.txt

# Windows (Powershell)
> python -m venv pytdenv
> .\pytdenv\Scripts\activate
> pip install -r requirements.txt
```
See here the [requirements.txt](requirements.txt), all packages used and their versions.

**Icon**    
https://www.svgrepo.com/svg/250232/download
