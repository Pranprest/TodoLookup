import itertools as it
from glob import iglob
import mmap
import os
import sys
import argparse
import toml
from pathlib import Path
from colorama import Fore
from typing import Final

# The methods started with "__" arent necessarily private per-se, but,
# it would be a lot better if anyone that imports this module were to not
# use these functions, because even if they're required for this package
# to work, they'll probably break everything in other contexts.

# TODO: Add parameters to docstrings
# HACK: Fix "# noqa: F821" comments!
# TODO: Implement generators and use pyahocorasick to find strings!
# TODO: Add logging module for debug information.

def __argParser() -> argparse.ArgumentParser:
    """Creates argument parser object for handeling arguments"""
    _parser = argparse.ArgumentParser(
        description="Find TODO(s), FIXME(s) or whatever your are searching"
    )

    _parser.add_argument(
        "file",
        type=Path,
        nargs="?",
        default=(None if sys.stdin.isatty() else sys.stdin),
        help="file or directory that will be used for searching, if it's value is '-', stdin is used",
    )

    _parser.add_argument(
        "-s",
        "--keyword",
        "--search",
        type=str,
        nargs="*",
        default=["TODO", "FIXME"],
        help="keywords that will be searched instead of TODOs",
    )

    _parser.add_argument(
        "-b",
        "--bare",
        help="removes colors and line count",
        action="store_true",
        default=False,
    )

    _parser.add_argument(
        "-r",
        "--recursive",
        help="checks directories recursively if specified",
        action="store_true",
        default=False
    )

    ext_group = _parser.add_argument_group(
        "extension management",
        "ways to manage which extensions are looked after when directories are inputed",
    )

    ext_group.add_argument(
        "--add-ext",
        help="adds an extension to the list of allowed extensions",
        nargs="*",
        metavar="EXTENSION",
    )

    ext_group.add_argument(
        "--list-ext",
        help="list all allowed extensions",
        action="store_true",
    )

    ext_group.add_argument(
        "--remove-ext",
        help="remove an extension to the list of allowed extensions",
        nargs="*",
        metavar="EXTENSION",
    )
    return _parser


def __gen_cfg_file(cfg_file: Path) -> None:
    if not cfg_file.exists() or os.stat(cfg_file).st_size == 0:
        with open(cfg_file, "w") as f:
            file_gen_dict: dict = {"config": {"allowed_extensions": []}}
            f.seek(0)
            toml.dump(file_gen_dict, f)
            f.truncate()


def __get_extensions(cfg_file_path: Path) -> set[str]:
    """Gets all the allowed extensions from config file"""
    with open(cfg_file_path, "r") as f:
        cfg = toml.load(f)

    if "config" not in cfg:
        print("Config key not found in config file")
        sys.exit(1)

    if len(cfg["config"]["allowed_extensions"]) <= 0:
        print("No allowed extensions were added, add one with --add-ext!")
        sys.exit(1)

    return set(cfg["config"]["allowed_extensions"])


def find_in_dir(
    dir: Path,
    search_list: list[str],
    allowed_extensions: set[str],
    bare: bool = False,
    recursive: bool = False
) -> None:
    """Finds any string list in every file in folder"""
    files_any_depth: list[str] = []
    files_curr_dir: list[str] = []

    # Get every allowed-extension file's abs. path in selected dir and put it on a set
    # Apparently, by the way that iglob works, being recursive includes the "previous" path?
    # So its kind of weird, this is kind if a hack, but still, works great!
    if recursive:
        files_any_depth = list(
            it.chain.from_iterable(
                # Root directory / whatever else
                iglob(
                    # src/(folders)/*.py
                    f"{dir}/**/*{extension}",
                    recursive=recursive,
                )
                for extension in allowed_extensions
            )
        )
    else:
        files_curr_dir = list(
            it.chain.from_iterable(
                # Root directory / whatever else
                iglob(
                    # src/(folders)/*.py
                    f"{dir}/*{extension}",
                    recursive=recursive,
                )
                for extension in allowed_extensions
            )
        )
        files_any_depth.extend(files_curr_dir)

    for file in files_any_depth:
        # FIXME: Don't print result message to files that doesn't have any results!
        actual_file_path = Path(f"{os.path.abspath(dir)}/{file}")

        if bare:
            print(f"\nResults in {file}:")
        else:
            print(f"\n{Fore.GREEN}Results in {file}:{Fore.WHITE}")
        find_in_file(actual_file_path, search_list=search_list, bare=bare)


def find_in_file(
    file_abs_path: Path,
    search_list: list[str],
    bare: bool = False,
) -> None:
    """Find a strings in a file!"""
    try:
        with open(file_abs_path, mode="rb") as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as s:
                for index, line in enumerate(iter(s.readline, b"")):
                    line_str = line.decode("utf-8")
                    # TODO: make this work when 2+ values found in the same file
                    if any((search_string := x) in line_str for x in search_list):
                        if bare:
                            print(line_str, end="")
                        else:
                            line_str = line_str.replace(
                                search_string,  # noqa: F821
                                f"{Fore.BLUE}{search_string}{Fore.WHITE}",  # noqa: F821
                            )
                            print(
                                f"{Fore.RED}line {index}:{Fore.WHITE} {line_str}",
                                end="",
                            )
    except ValueError:
        if bare:
            print(f"File {file_abs_path} is empty")
        else:
            print(f"{Fore.RED}File {file_abs_path} is empty{Fore.WHITE}")


def find_from_stdin(search_list: list[str], bare: bool = False) -> None:
    """Find a strings in sdin! (piped file output)"""
    for index, line in enumerate(sys.stdin):
        if any((search_string := x) in line for x in search_list):
            if bare:
                print(line, end="")
            else:
                line = line.replace(
                    search_string,  # noqa: F821
                    f"{Fore.BLUE}{search_string}{Fore.WHITE}",  # noqa: F821
                )
                print(f"{Fore.RED}line {index}:{Fore.WHITE} {line}", end="")


def __arg_handler(
    args: argparse.Namespace,
    cfg_file: Path,
) -> None:
    """Handles all the arguments, made for cleaning the main funcion"""
    with open(cfg_file, "r") as f:
        cfg = toml.load(f)
    allowed_ext = cfg["config"]["allowed_extensions"]

    if args.add_ext is not None and len(args.add_ext) >= 1:
        # Make sure there aren't any duplicates
        args.add_ext = set(args.add_ext)

        for ext in args.add_ext:
            ext.strip()
            if ext[0] != ".":
                # Add "." BEFORE extension!
                ext = "." + ext
            if ext in allowed_ext:
                print(
                    f"Extension {ext} is already on the list of allowed extensions, skipping..."
                )
            else:
                allowed_ext.append(ext)
                print(f"Extension {ext} added")

        with open(cfg_file, "w") as f:
            f.seek(0)
            toml.dump(cfg, f)
            f.truncate()
        sys.exit(0)

    if args.list_ext:
        print("These are the current allowed extensions:")
        print(", ".join(allowed_ext))
        sys.exit(0)

    if args.remove_ext is not None and len(args.remove_ext) >= 1:
        for ext in args.remove_ext:
            ext.strip()
            if ext[0] != ".":
                ext = "." + ext
            if ext not in allowed_ext:
                print(
                    f"Extension {ext} is not in the list of allowed extensions, skipping."
                )
            else:
                allowed_ext.remove(ext)
                print(f"Extension {ext} removed")
        with open(cfg_file, "w") as f:
            f.seek(0)
            toml.dump(cfg, f)
            f.truncate()
        sys.exit(0)


def main() -> None:
    CURROSSLASH: Final = "\\" if (os.name == "nt") else "/"
    CFG_FILE: Final = Path(
        f"{Path(__file__).parent.absolute()}{CURROSSLASH}config.toml"
    )

    parser = __argParser()
    args = parser.parse_args()

    __gen_cfg_file(CFG_FILE)

    if len(args.keyword) < 1:
        args.keyword.append("TODO")

    __arg_handler(args, CFG_FILE)

    # Put this before handeling arguments, because it might conflict with
    # some argument options (such as --list/add/rm-ext)
    usr_file: Path = args.file

    if usr_file is None:
        parser.print_help()
        sys.exit(0)

    if usr_file.name == "-":
        find_from_stdin(args.keyword, args.bare)
        sys.exit(0)

    if not usr_file.exists():
        raise OSError("File or directory does not exist.")

    if usr_file.is_dir():
        find_in_dir(
            dir=args.file,
            search_list=args.keyword,
            allowed_extensions=__get_extensions(CFG_FILE),
            bare=args.bare,
            recursive=args.recursive,
        )
    else:
        find_in_file(file_abs_path=usr_file, search_list=args.keyword, bare=args.bare)


if __name__ == "__main__":
    main()
