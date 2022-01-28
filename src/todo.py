import mmap
from colorama import Fore
import os
import sys
import argparse
from pathlib import Path
from io import TextIOBase
# TODO: Make this an installable package

currosslash = "\\" if (os.name == "nt") else "/"
currfilepath = f"{Path(__file__).parent.absolute()}{currosslash}"


def argParser():
    _parser = argparse.ArgumentParser(
        description='Find TODO(s), FIXME(s) or whatever your are searching')

    _parser.add_argument("file",
                         type=Path,
                         nargs="?",
                         default=(None if sys.stdin.isatty() else sys.stdin),
                         help="file or directory that will be used for searching, if empty, stdin is used"
                         )

    _parser.add_argument("-s",
                         "--keyword", "--search",
                         type=str,
                         nargs="*",
                         default=["TODO"],
                         help="keywords that will be searched instead of TODOs"
                         )

    _parser.add_argument("-b",
                         "--bare",
                         help="removes colors and line count",
                         action="store_true",
                         default=False,
                         )

    return _parser


def find_in_file(file_abs_path: Path, search_list: list[str], bare: bool = False) -> None:
    with open(file_abs_path, mode='rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as s:
            for index, line in enumerate(iter(s.readline, b"")):
                line = line.decode("utf-8")
                if any((search_string := x) in line for x in search_list):
                    if bare == True:
                        print(line, end="")
                    else:
                        line = line.replace(
                            search_string, f"{Fore.BLUE}{search_string}{Fore.WHITE}")
                        print(
                            f"{Fore.RED}line {index}:{Fore.WHITE} {line}", end="")


def find_from_stdin(stdin, search_list: list[str], bare: bool = False) -> None:
    for index, line in enumerate(sys.stdin):
        if any((search_string := x) in line for x in search_list):
            if bare == True:
                print(line, end="")
            else:
                line = line.replace(
                    search_string, f"{Fore.BLUE}{search_string}{Fore.WHITE}")
                print(
                    f"{Fore.RED}line {index}:{Fore.WHITE} {line}", end="")


def main() -> None:
    parser = argParser()
    args = parser.parse_args()

    if args.file == None:
        parser.print_help()
        sys.exit(0)

    if not sys.stdin.isatty():
        find_from_stdin(args.file, args.keyword)
        sys.exit(0)

    filepath = Path(os.path.abspath(args.file))

    if not filepath.exists():
        raise OSError("File does not exist.")

    if filepath.is_dir():
        # TODO: make it possible to search things in a whole dir
        raise NotImplementedError(
            "This script still doesnt support directories!")
    else:
        find_in_file(file_abs_path=filepath,
                     search_list=args.keyword, bare=args.bare)


if __name__ == '__main__':
    main()
