from multiprocessing.dummy import Pool
from functools import partial
from subprocess import call
import os, shutil, sys
import Log as log

def load_closed_lists(closed_lists_f, whitelist_f):
    """Loads closed lists and whitelisted lists from file.

    Validates that all whitelisted items are actually present in closed_lists;
    i.e., no typos leading to accidental exclusion.

    Most of this function is logging calls.
    """

    # read in closed lists file
    log.info("Reading closed lists file {}".format(closed_lists_f))
    with open(closed_lists_f, "r") as f:
        closed_lists = [line.strip("\n") for line in f.readlines()]
    log.info("Loaded {} closed lists".format(len(closed_lists)))

    # print all lists in file to debug output
    log.debug("Closed lists (including any whitelisted):")
    log.debug("\n".join(closed_lists))
    
    # read in whitelist file
    log.info("Reading whitelist file {}".format(whitelist_f))
    with open(whitelist_f, "r") as f:
        whitelist = [line.strip("\n") for line in f.readlines()]

    # print whitelist to info-level output (presumably much shorter than closed_lists)
    log.info("Whitelist:")
    log.info("\n".join(whitelist))

    closed_lists = set(closed_lists)
    whitelist = set(whitelist)

    # check that all whitelisted items are actually present in closed_lists
    if not len(whitelist - closed_lists) == 0:
        log.error("Some whitelisted lists not present in closed_lists. Check your inputs.")
        log.error("Missing lists:")
        log.error("\n".join(sorted(whitelist - closed_lists)))
        sys.exit()

    # subtract whitelist set from closed list set; sort for good measure
    closed_lists = sorted(closed_lists - whitelist)

    # print final closed_lists to debug
    log.info("See debug for closed lists excluding whitelist")
    log.debug("Closed lists excluding whitelist:")
    log.debug("\n".join(closed_lists))
    log.info("Final closed lists: {}".format(len(closed_lists)))
    return closed_lists

def lists_to_copy(closed_lists, from_dir, list_subdir):
    """Gets available lists to copy from data source directory.

    Validates that all closed lists are actually present to avoid typos
    causing unwanted copying.

    Because this is fed the result of load_closed_lists, there is the possibility
    of an identical typo in both the closed_lists and whitelist files not being caught,
    as it would be removed in load_closed lists. In that case, though, we must want the list
    to be copied, as it's on the whitelist, so it doesn't matter.
    """

    # sets easier to work with
    closed_lists = set(closed_lists)

    # extracts lists from original directory
    list_dir = os.path.join(from_dir, list_subdir)
    log.info("Getting lists to copy from {}".format(list_dir))

    lists = set(os.listdir(list_dir))
    log.info("Got {} lists to copy".format(len(lists)))

    # check for strict subset
    if not len(closed_lists - lists) == 0:
        log.error("Some closed lists not present in {}".format(list_dir))
        log.error("Missing lists:")
        log.error("\n".join(sorted(closed_lists - lists)))
        sys.exit()

    lists_final = sorted(lists - closed_lists)

    log.info("Copying {} lists after removing closed lists".format(len(lists_final)))
    log.debug("Lists to copy (excluding closed lists):")
    log.debug("\n".join(lists_final))
    return lists_final

def archives_to_copy(lists_final, from_dir, arc_subdir, domain):
    """Uses final list of lists to copy to produce archive directory strings.
    """

    arc_dir = os.path.join(from_dir, arc_subdir)
    log.info("Checking that each list has a corresponding archive in {}".format(arc_dir))

    arc_list = os.listdir(arc_dir)
    log.info("Got {} list archives".format(len(arc_list)))
    log.debug("Archives:")
    log.debug("\n".join(arc_list))

    # compiles archive directory strings from lists_final
    # warns on missing archives but does not exit
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
    # default to a dry run
    no_overwrite = True


    logfile = "migrate_data_log"
    closed_lists_f = "closed_lists"
    whitelist_f = "whitelist"
    from_dir = "/mnt/sympa02_files/"
    to_dir = "/var/lib/sympa/"
    domain = "sympa.bard.edu"
    arc_subdir = "arc"
    list_subdir = os.path.join("list_data", domain)

    # set up logger
    log.basicConfig(1, filename = logfile)

    if len(sys.argv) > 1:
        for arg in sys.argv:
            if arg == "overwrite":
                no_overwrite = False
                log.warning("Setting no_overwrite to False; data will be DESTROYED")
                break


    log.info("Copying from: {}".format(from_dir))
    log.info("Copying to: {}".format(to_dir))
    if no_overwrite: log.info("(Actually not copying anything: no_overwrite set to True)")
    log.info("Subdirectories: archives={} lists={}".format(arc_subdir, list_subdir)) 

    # loads closed lists from file with the exclusion of whitelisted lists
    closed_lists = load_closed_lists(closed_lists_f, whitelist_f)

    # gets list of list directories to copy, excluding non-whitelisted closed lists
    lists_final = lists_to_copy(closed_lists, from_dir, list_subdir)

    # gets list of archive directories to copy based on lists_final
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


    if no_overwrite:
        log.info("no_overwrite is set; exiting before copying")
        sys.exit()

    # SAFE UNTIL HERE

    # some multithreaded copying
    pool = Pool(30)

    log.info("Copying is gonna take a while, sorry")
    log.info("Starting archive copy")
    pool.map_async(copy_arc_entry, arc_list_final)


    log.info("Starting lists copy")
    pool.map_async(copy_list_entry, lists_final)

    pool.close()

    pool.join()
    log.info("Archive copy complete")
    log.info("Lists copy complete")

    log.info("Transferring ownership to sympa:sympa")
    call(['chown', '-R', 'sympa:sympa', os.path.join(to_dir, list_subdir)])
    call(['chown', '-R', 'sympa:sympa', os.path.join(to_dir, arc_subdir)])
    log.info("Completed transfer")


if __name__ == "__main__":
    main()
