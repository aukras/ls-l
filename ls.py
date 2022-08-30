import os
import stat
import sys
from pwd import getpwuid
from grp import getgrgid
from datetime import datetime

# The following lists will contain strings for entity metadata for a given directory
# that will be used to generate the final "ls -l" output.
permissions = []
link_counts = []
sizes = []
mod_times = []
user_ownerships = []
group_ownerships = []
filenames = []

# The total number of blocks taken by the given directory.
total_blocks = 0

# We only accept a valid directory as a command line argument. If no directory is given, we
# use the current working directory. In any other case, we return an error.
directory = os.getcwd()
if len(sys.argv) > 2:
    print("Invalid number of arguments given")
    exit(1)
elif len(sys.argv) == 2:
    if os.path.isdir(sys.argv[1]):
        directory = sys.argv[1]
    else:
        print("Directory does not exist")
        exit(1)

# Go through each non-hidden entity in the given directory to gather their metadata.
for name in sorted(os.listdir(directory), key=str.casefold):

    # We ignore hidden entities (as the ls -l command does).
    if name[0] == '.':
        continue

    filepath = os.path.join(directory, name)
    st = os.lstat(filepath)
    mode = os.lstat(filepath).st_mode

    # We will use bold font for directories and symlinks and normal font for other types.
    if stat.filemode(mode)[0] == 'd' or stat.filemode(mode)[0] == 'l':
        name = "\033[1m" + name + "\033[0;0m"

    # If the entity is a symlink, we will indicate its target directory
    if stat.filemode(mode)[0] == 'l':
        name += " -> " + "\033[1m" + os.readlink(filepath) + "\033[0;0m"

    # Gather entity metadata and store its string data in the lists.
    permissions.append(str(stat.filemode(mode)))
    link_counts.append(str(st.st_nlink))
    sizes.append(str(st.st_size))
    mod_times.append(str(datetime.fromtimestamp(st.st_mtime).strftime('%Y %b %d [%H:%M]')))
    user_ownerships.append(str(getpwuid(st.st_uid).pw_name))
    group_ownerships.append(str(getgrgid(st.st_gid).gr_name))
    filenames.append(name)

    # Update total blocks used for the directory.
    total_blocks += st.st_blocks

# We use padding to adaptively adjust spacing between each piece of metadata so that we always have
# exactly one whitespace character between each column (only applies to columns which have data that vary in length).
padding_lc = max(map(len, link_counts))
padding_uo = max(map(len, user_ownerships))
padding_gp = max(map(len, group_ownerships))
padding_size = max(map(len, sizes))

# Printing the metadata
print("total ", int(total_blocks/2))
for i in range(0, len(permissions)):
    print("{} {} {} {} {} {} {}".format(permissions[i], link_counts[i].ljust(padding_lc),
                                        user_ownerships[i].ljust(padding_uo), group_ownerships[i].ljust(padding_gp),
                                        sizes[i].ljust(padding_size), mod_times[i], filenames[i]))
