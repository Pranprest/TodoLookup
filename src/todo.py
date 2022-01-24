import mmap
from colorama import Fore
import os
import argparse
from pathlib import Path

currosslash = "\\" if (os.name == "nt") else "/"
currfilepath = f"{Path(__file__).parent.absolute()}{currosslash}"


def argParser():
    _parser = argparse.ArgumentParser(
        description='Find TODO(s), FIXME(s) or whatever your are searching')

    _parser.add_argument("file",
                         type=Path,
                         help="file or directory that will be used for searching")

    _parser.add_argument("keyword",
                         type=str,
                         help="keyword that will be searched instead of TODOs",
                         default="TODO")

    return _parser


def find_in_file(file_abs_path: Path, search_string: str, color: bool = True) -> None:
    with open(file_abs_path, mode='rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as s:
            for index, line in enumerate(iter(s.readline, b"")):
                line = line.decode("utf-8")
                if line.find(search_string) != -1:
                    if color == True:
                        line = line.replace(
                            search_string, f"{Fore.BLUE}{search_string}{Fore.WHITE}")
                    print(f"line {index}: {line}", end="")


def main() -> None:
    args = argParser().parse_args()
    filepath = Path(os.path.abspath(args.file))

    if not filepath.exists():
        raise OSError("File does not exist.")
    if filepath.is_dir():
        raise NotImplementedError(
            "This script still doesnt support directories!")

    find_in_file(file_abs_path=filepath, search_string=args.keyword)


if __name__ == '__main__':
    main()
