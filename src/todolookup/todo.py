import mmap
from xml.dom import NotFoundErr
from colorama import Fore
import os
import sys
import argparse
from pathlib import Path
import toml

currosslash = "\\" if (os.name == "nt") else "/"
currfilepath = f"{Path(__file__).parent.absolute()}{currosslash}"
cfg_file = Path(f"{Path(__file__).parent.absolute()}{currosslash}config.toml")


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
                         default=["TODO", "FIXME"],
                         help="keywords that will be searched instead of TODOs"
                         )

    _parser.add_argument("-b",
                         "--bare",
                         help="removes colors and line count",
                         action="store_true",
                         default=False,
                         )

    ext_group = _parser.add_argument_group(
        "extension management", "ways to manage which extensions are looked after when directories are inputed")

    ext_group.add_argument("--add-ext",
                           help="adds an extension to the list of allowed extensions",
                           nargs="*",
                           metavar="EXTENSION")

    ext_group.add_argument("--list-ext",
                           help="list all allowed extensions",
                           action="store_true",
                           )

    ext_group.add_argument("--remove-ext",
                           help="remove an extension to the list of allowed extensions",
                           nargs="*",
                           metavar="EXTENSION")
    return _parser


def get_extensions() -> set[str]:
    with open(cfg_file, "r") as f:
        cfg = toml.load(f)

    if not "config" in cfg:
        print("Config key not found in config file")
        sys.exit(1)

    if len(cfg["config"]["allowed_extensions"]) <= 0:
        print("No allowed extensions were added, add one with --add-ext!")
        sys.exit(1)

    return set(cfg["config"]["allowed_extensions"])


def find_in_dir(dir: Path, search_list: list[str], allowed_extensions: set[str], bare: bool = False):
    files_dir = [Path(x).absolute()
                 for x in Path(dir).iterdir() if Path(x).is_file() and Path(x).suffix in allowed_extensions]
    for file in files_dir:
        print(f"Results in {file}:")
        find_in_file(file, search_list=search_list, bare=bare)


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


def find_from_stdin(search_list: list[str], bare: bool = False) -> None:
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

    if not cfg_file.exists() or os.stat(cfg_file).st_size == 0:
        with open(cfg_file, "w") as f:
            pog = {"config": {"allowed_extensions": []}}
            f.seek(0)
            toml.dump(pog, f)
            f.truncate()
    with open(cfg_file, "r") as f:
        cfg = toml.load(f)

    if args.add_ext != None and len(args.add_ext) >= 1:
        args.add_ext = set(args.add_ext)
        for ext in args.add_ext:
            ext.strip()
            if ext[0] != ".":
                ext = "." + ext
            if ext in cfg["config"]["allowed_extensions"]:
                print(
                    f"Extension {ext} is already on the list of allowed extensions, skipping.")
            else:
                print(f"Extension {ext} added")
                cfg["config"]["allowed_extensions"].append(ext)
        with open(cfg_file, "w") as f:
            f.seek(0)
            toml.dump(cfg, f)
            f.truncate()
        sys.exit(0)

    if args.list_ext == True:
        print(f"These are the current allowed extensions:")
        print(", ".join(cfg["config"]["allowed_extensions"]))
        sys.exit(0)

    if args.remove_ext != None and len(args.remove_ext) >= 1:
        for ext in args.remove_ext:
            ext.strip()
            if ext[0] != ".":
                ext = "." + ext
            if ext not in cfg["config"]["allowed_extensions"]:
                print(
                    f"Extension {ext} is not in the list of allowed extensions, skipping.")
            else:
                cfg["config"]["allowed_extensions"].remove(ext)
                print(f"Extension {ext} removed sucessfully")
        with open(cfg_file, "w") as f:
            f.seek(0)
            toml.dump(cfg, f)
            f.truncate()
        sys.exit(0)

    if len(args.keyword) <= 1:
        args.keyword.append("TODO")

    if args.file == None:
        parser.print_help()
        sys.exit(0)

    if not sys.stdin.isatty():
        find_from_stdin(args.keyword, args.bare)
        sys.exit(0)

    filepath = Path(os.path.abspath(args.file))

    if not filepath.exists():
        raise OSError("File does not exist.")

    if filepath.is_dir():
        find_in_dir(dir=args.file, search_list=args.keyword,
                    allowed_extensions=get_extensions(), bare=args.bare)
    else:
        find_in_file(file_abs_path=filepath,
                     search_list=args.keyword, bare=args.bare)


if __name__ == '__main__':
    main()
