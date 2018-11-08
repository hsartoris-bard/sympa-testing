import os, shutil
import Log as log

def migrate_lists(from_dir, to_dir, closed_lists):
    log.info("Moving list data from", from_dir, "to", to_dir)
    log.debug("Using following closed_lists:")
    log.debug("\n".join(closed_lists))

    lists = os.listdir(from_dir)

    for entry in lists:
        if entry in closed_lists:
            log.info("Skipping closed list", entry)
            continue
        try:
            log.debug("Copying", entry)
            shutil.copytree(os.path.join(from_dir, entry), to_dir)
        except Exception as e:
            log.critical("Failure:", e)
            sys.exit(-1)


if __name__ == "__main__":
    with open("closed_lists", "r") as f:
        closed_lists = [line.strip("\n") for line in f.readlines()]
    log.basicConfig(2)
    from_dir = "/mnt/sympa02_files/list_data/sympa.bard.edu/"
    to_dir = "/var/lib/sympa/list_data/sympa.bard.edu/"
    migrate_lists(from_dir, to_dir, closed_lists)
