from time import time
from todolookup.todo import main
from pathlib import Path
from os import name as ossname

# Use this file just like you'd use todo.py normally!!


def profile(profpath: Path = Path(__file__).absolute().parent) -> None:
    # Use snakeviz to visualize this if you feel like it!
    import cProfile
    import pstats

    with cProfile.Profile() as pr:
        main()

    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.dump_stats(
        Path(f"{profpath}\\prof_results\\todolookup_profiling_{time()}.prof")
    )


if __name__ == "__main__":
    profile()
