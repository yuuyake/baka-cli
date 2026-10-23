"""Lets you pick the command name (baka-cli, b-cli, baka or bcli) by adding a symlink next to it."""
import os
import shutil

ALIASES = ["b-cli", "baka", "bcli"]


def apply(name):
    """Returns (ok, message). baka-cli itself always keeps working."""
    main = shutil.which("baka-cli")
    if not main:
        return False, "could not find baka-cli on your PATH"
    d = os.path.dirname(main)
    try:
        for a in ALIASES:  # drop alias links we made before
            link = os.path.join(d, a)
            if a != name and os.path.islink(link) and os.readlink(link) == main:
                os.remove(link)
        if name in ALIASES:
            link = os.path.join(d, name)
            if os.path.lexists(link):
                if not (os.path.islink(link) and os.readlink(link) == main):
                    return False, f"{link} already exists and is not ours"
            else:
                os.symlink(main, link)
            return True, f"you can now run [bold]{name}[/] (baka-cli still works too)"
        return True, "using [bold]baka-cli[/]"
    except OSError as e:
        return False, f"could not create the alias ({e})"
