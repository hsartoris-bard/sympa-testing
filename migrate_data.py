from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
from subprocess import call
import os, shutil, sys
import Log as log

def load_closed_lists(closed_lists_f, whitelist_f):
    log.info("Reading closed lists file {}".format(closed_lists_f))
    with open(closed_lists_f, "r") as f:
        closed_lists = [line.strip("\n") for line in f.readlines()]
    log.info("Loaded {} closed lists".format(len(closed_lists)))

    log.debug("Closed lists (including any whitelisted):")
    log.debug("\n".join(closed_lists))
    
    log.info("Reading whitelist file {}".format(whitelist_f))
    with open(whitelist_f, "r") as f:
        whitelist = [line.strip("\n") for line in f.readlines()]
    log.info("Whitelist:")
    log.info("\n".join(whitelist))

    errcheck = False
    # could just stop at first discovered, but it would be nice to know about all of them 
    for l in whitelist:
        if not l in closed_lists:
            log.warning("Whitelisted list {} not present in closed_lists".format(l))
            errcheck = True
    if errcheck:
        log.error("Some whitelisted lists not present in closed_lists. Check your inputs.")
        sys.exit()

    closed_lists = sorted(list(set(closed_lists) - set(whitelist)))
    log.info("See debug for closed lists excluding whitelist")
    log.debug("Closed lists excluding whitelist:")
    log.debug("\n".join(closed_lists))
    log.info("Final closed lists: {}".format(len(closed_lists)))
    return closed_lists

def lists_to_copy(closed_lists, from_dir, list_subdir):
    # extracts lists from original directory and removes non-whitelisted closed lists
    list_dir = os.path.join(from_dir, list_subdir)
    log.info("Getting lists to copy from {}".format(list_dir))

    lists = os.listdir(list_dir)
    log.info("Got {} lists to copy".format(len(lists)))

    lists_final = sorted(list(set(lists) - set(closed_lists)))
    if not len(lists_final) == len(lists) - len(closed_lists):
        log.error("Some closed lists not present in {}".format(list_dir))
        sys.exit()

    log.info("Copying {} lists after removing closed lists".format(len(lists_final)))
    log.debug("Lists to copy (excluding closed lists):")
    log.debug("\n".join(lists_final))
    return lists_final

def archives_to_copy(lists_final, from_dir, arc_subdir, domain):
    # validates list of lists to copy against list of archives
    arc_dir = os.path.join(from_dir, arc_subdir)
    log.info("Checking that each list has a corresponding archive in {}".format(arc_dir))

    arc_list = os.listdir(arc_dir)
    log.info("Got {} list archives".format(len(arc_list)))
    log.debug("Archives:")
    log.debug("\n".join(arc_list))

    arc_list_final = []
    for l in lists_final:
        l_arc = l + "@" + domain
        if l_arc in arc_list:
            arc_list_final.append(l_arc)
        else:
            log.warning("List {} does not have an archive entry".format(l))

    log.debug("Pruned archives:")
    log.debug("\n".join(arc_list_final))
    return arc_list_final

def copy_entry(entry, from_dir, to_dir):
    shutil.copytree(os.path.join(from_dir, entry), os.path.join(to_dir, entry))

def main():
    # do a dry run
    no_copy = True

    if len(sys.argv) < 3:
        print("Syntax: migrate_data.py from_dir to_dir")
        exit()

    logfile = "migrate_data_log"
    closed_lists_f = "closed_lists"
    whitelist_f = "whitelist"
    #from_dir = "/mnt/sympa02_files/"
    #to_dir = "/var/lib/sympa/"
    from_dir = sys.argv[1]
    to_dir = sys.argv[2]
    domain = "sympa.bard.edu"
    arc_subdir = "arc"
    list_subdir = os.path.join("list_data", domain)

    log.basicConfig(1, filename = logfile)

    closed_lists = load_closed_lists(closed_lists_f, whitelist_f)

    log.info("Copying from: {}".format(from_dir))
    log.info("Copying to: {}".format(to_dir))
    if no_copy: log.info("(Actually not copying anything: no_copy set to True)")
    log.info("Subdirectories: archives={} lists={}".format(arc_subdir, list_subdir)) 

    lists_final = lists_to_copy(closed_lists, from_dir, list_subdir)

    arc_list_final = archives_to_copy(lists_final, from_dir, arc_subdir, domain)
    
    log.info("Making curried functions:")
    # make curried functions
    copy_arc_entry = partial(copy_entry,
            from_dir = os.path.join(from_dir, arc_subdir),
            to_dir = os.path.join(to_dir, arc_subdir))
    log.info(copy_arc_entry)

    copy_list_entry = partial(copy_entry,
            from_dir = os.path.join(from_dir, list_subdir),
            to_dir = os.path.join(to_dir, list_subdir))
    log.info(copy_list_entry)

    # some multithreaded copying
    list_pool = ThreadPool(4)
    arc_pool = ThreadPool(4)

    if no_copy:
        log.info("no_copy is set; exiting before copying")
        sys.exit()

    log.info("Starting archive copy")
    arc_pool.map(copy_arc_entry, arc_list_final)
    log.info("Starting lists copy")
    list_pool.map(copy_list_entry, lists_final)

    arc_pool.close()
    list_pool.close()
    arc_pool.join()
    log.info("Archive copy complete")
    list_pool.join()
    log.info("Lists copy complete")
    log.info("Transferring ownership to sympa:sympa")
    call(['chown', '-R', 'sympa:sympa', os.path.join(to_dir, list_subdir)])
    call(['chown', '-R', 'sympa:sympa', os.path.join(to_dir, arc_subdir)])
    log.info("Completed transfer")


if __name__ == "__main__":
    main()
