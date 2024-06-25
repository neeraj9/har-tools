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


## Extract multipart data from browser devtool copy as response

When you use chromium tools copy as response for multipart/mixed data then
the browser will copy the base64 encoded data. In such cases you can use
another tool to selectively extract multipart data as individual files.

1. Create a new file as multipart.txt (or anything else) when you paste
   the content after copying respose within network tab for the multipart
   data call.
2. Note down the multipart boundary from the response header within the
   "content-type" response header within the browser network tab.
3. Use the boundary value and multipart.txt file (or whatever you used as the name)
   within the following tool to extract files. See below for reference.

```console
python extract_base64_multipart_data.py "2f9825ee3f2949949f1210caa1978960" multipart.txt
```