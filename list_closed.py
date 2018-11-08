import os
import Log as log

def list_closed(list_dir, outfile=None):
    closed_str = "subscribers.closed.dump"

    log.basicConfig(level=2)

    log.info("List data directory:", list_dir)
    
    log.debug("Lists:")
    lists = os.listdir(list_dir)
    log.debug("\n".join(lists))

    if outfile:
        f = open(outfile, "w+")

    closed_lists = []

    for entry in lists:
        if closed_str in entry:
            closed_lists.append(entry)

    log.info("Closed lists:")
    log.info("\n".join(closed_lists))

    if outfile:
        f.write("\n".join(closed_lists))
        f.close()
        log.info("Closed lists written to", outfile)

if __name__ == "__main__":
    list_closed("/mnt/sympa02_files/list_data/sympa.bard.edu/", outfile="/home/hsartoris/sympa-testing/closed_lists")
