# har-tools

A collection of HAR tools for everyone to help with debugging.


## Extract multipart data from HAR

You can conveniently save multipart data as individual files from
a HAR file as follows. Note that replace `name.har` with the
actual path and name of the har file.

> Note that the script will write files into current working
> directory and will NOT overwrite files if they exist already.

```console
python extract_multipart_data_from_har.py name.har
```
