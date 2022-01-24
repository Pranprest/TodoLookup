# Todo Finder
## Overview
Finds TODO(s) and other comment warnings in your project folder(s)
- It's pretty much just a copy of GREP, but it searches for TODOs, FIXMEs when used on a file by default
- It searches your whole directory for the keyword (on only non-excluded extensions)

```
usage: todo.py [-h] file keyword

Find TODO(s), FIXME(s) or whatever your are searching

positional arguments:
  file        file or directory that will be used for searching
  keyword     keyword that will be searched instead of TODOs   

options:
  -h, --help  show this help message and exit
```

## Note
- Made for fun, I hope it will be useful for someone.