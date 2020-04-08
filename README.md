# Duplicates

The "Duplicates" is a tool for convenient duplicate file removal. 
"Duplicates" is a wrapper over excellent duplicate search tool "https://github.com/michaelkrisper/duplicate-file-finder." 

* It can list duplicates. It prints duplicated files sorted by the size and number of clones.

* It can remove duplicates when --purge flag provided. The original (single copy) always preserved.
  
  Note: if --purge flag provided, MacOS ".DS_Store" files and all empty directories deleted in --work (but not in --golden).

* It can search duplicates in two separate directories as in one; however, it removes duplicates only from one (--work) and changes nothing in other (--golden). Even if --purge flag provided, golden directory never changed.  


## What it can help with

Removing duplicates from a specified directory and keeping a "golden" files collection intact (even if there are duplicates there too). For example, remove duplicated photos on a flash drive and not changing your existing photos library.

Or having multiple directories that you want to clean up. However, there is one master folder that you don't want to mess with.

The "Duplicates" removes files only in the working directory (always keep one copy if all duplicates under the work folder). The golden directory used to search for duplicates; however, no files deleted there.

## Usage

Find and print duplicates (sorted by file size - largest first). Nothing deleted/ changed
```sh
duplicates --work work 
```

Remove duplicates under the folder (keep one copy only)
```sh
duplicates --work work  --purge    
```

Search for duplicates in both folders as in one but remove duplicated files from **need_cleanup** only. Nothing modified in **never_change_me**
```sh
duplicates --work need_cleanup --golden never_change_me --purge
```

Usage
```sh
usage: duplicates [-h] [-v] [-g GOLDEN] -w WORK [-p]

Finds duplicates in both `work` and `golden` folders. 
If --purge flag set,
Only the duplicates that are in `work` folder are removed.
Keeps an oldest duplicate file.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         display debug info
  -g GOLDEN, --golden GOLDEN
                        (optional) path to the folder where duplicates will be
                        searched though this folder will be unchanged
  -w WORK, --work WORK  work folder that will be stripped from the duplicates
                        found in both itself and `golden`
  -p, --purge           purge/ delete extra files from `work` folder. If all
                        copies are under work, single (with oldest
                        modification time) file will be preserved. All
                        duplicates in golden also preserved/skipped.
```

## Install

Get the source code, go to duplicates directory and run
```sh
git clone https://github.com/AlexeyMavrin/duplicates.git
cd duplicates
python setup.py install
python setup.py test
```

## Test command

```shell script
python3 setup.py test
```
Alternatively
```shell script
python3 test_all.py
```

## Run Duplicates without installing
```shell script
python3 duplicates.py -h
```

## TODO
* Allow multiple work directories at the same time
