import os, shutil, sys
import Log as log

def migrate_lists(from_dir, to_dir, closed_lists, archive=False):
    log.info("Moving " + ("archive" if archive else "list") + " data from", from_dir, "to", to_dir)
    log.debug("Using following closed_lists:")
    log.debug("\n".join(closed_lists))

    lists = os.listdir(from_dir)

    for entry in lists:
        if (entry if not archive else entry.split("@")[0]) in closed_lists:
            log.info("Skipping closed list", entry)
            continue
        try:
            log.debug("Copying", entry)
            shutil.copytree(os.path.join(from_dir, entry), os.path.join(to_dir, entry))
        except Exception as e:
            log.critical("Failure:", e)
            sys.exit(-1)

if __name__ == "__main__":
    with open("closed_lists", "r") as f:
        closed_lists = [line.strip("\n") for line in f.readlines()]
    log.basicConfig(2, filename = "archive_migrate_log")
    list_from_dir = "/mnt/sympa02_files/list_data/sympa.bard.edu/"
    list_to_dir = "/var/lib/sympa/list_data/sympa.bard.edu/"

    arc_from_dir = "/mnt/sympa02_files/arc/"
    arc_to_dir = "/var/lib/sympa/arc/"
    migrate_lists(arc_from_dir, arc_to_dir, closed_lists, archive=True)
