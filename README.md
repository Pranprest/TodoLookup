# Todo Lookup
## Overview
Finds TODO(s) and other comment warnings in your project folder(s)
- It's pretty much just a copy of GREP, but it searches for TODOs, FIXMEs when used on a file by default
- It searches your whole directory for the keyword (on only non-excluded extensions)

```
usage: todo [-h] [-s [KEYWORD ...]] [-b] [--add-ext [EXTENSION ...]] [--list-ext] [--remove-ext [EXTENSION ...]]
            [file]

Find TODO(s), FIXME(s) or whatever your are searching

positional arguments:
  file                  file or directory that will be used for searching, if empty, stdin is used

options:
  -h, --help            show this help message and exit
  -s [KEYWORD ...], --keyword [KEYWORD ...], --search [KEYWORD ...]
                        keywords that will be searched instead of TODOs
  -b, --bare            removes colors and line count

extension management:
  ways to manage which extensions are looked after when directories are inputed

  --add-ext [EXTENSION ...]
                        adds an extension to the list of allowed extensions
  --list-ext            list all allowed extensions
  --remove-ext [EXTENSION ...]
                        remove an extension to the list of allowed extensions
```

## Note
- Made for fun, I hope it will be useful for someone.
