# Duplicates

The "Duplicates" is a tool for convenient duplicate file removal. 
"Duplicates" is a wrapper over excellent duplicate search tool "https://github.com/michaelkrisper/duplicate-file-finder." So far, this is the fastest and most reliable duplicate finder tool I've tried.

## Primary use case

Removing duplicates from a specified directory and keeping a "golden" files collection intact (even if there are duplicates there too). For example, remove duplicated photos you have from someone on a flash drive and not changing your existing photos library.

The "Duplicates" removes files only in the working directory (always keep one copy if all duplicates under the work folder). The golden directory used to search for duplicates; however, no files deleted there.

## Usage

Find and print duplicates (sorted by file size - largest first). Nothing deleted/ changed
```sh
duplicates --work work 
```

Search for duplicates in both folders but remove duplicated files from **new_pics** only. Nothing deleted in **my_photos_library**
```sh
duplicates --work new_pics --golden my_photos_library --purge
```

Remove duplicates under the folder (keep one copy only)
```sh
duplicates --work work  --purge    
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
