import os
import Log as log

def list_closed(list_dir, outfile=None):
    #closed_str = "subscribers.closed.dump"
    closed_str = "status closed"

    log.info("List data directory:", list_dir)
    
    log.debug("Lists:")
    lists = os.listdir(list_dir)
    log.debug("\n".join(lists))

    if outfile:
        f = open(outfile, "w+")

    closed_lists = []
    access_denied = []

    for entry in lists:
        try:
            with open(os.path.join(list_dir, entry, "config"), "r") as config:
                if closed_str in config.readlines():
                    log.debug(entry)
                    closed_lists.append(entry)
        except OSError:
            access_denied.append(entry)
            log.info("Access denied to", entry)
            continue


    log.info("Closed lists:")
    log.info("\n".join(closed_lists))

    if outfile:
        f.write("\n".join(closed_lists))
        f.close()
        log.info("Closed lists written to", outfile)

if __name__ == "__main__":
    log.basicConfig(level=1)
    list_closed("/mnt/sympa02_files/list_data/sympa.bard.edu/", outfile="/home/hsartoris/sympa-testing/closed_lists")
