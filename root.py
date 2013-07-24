###########################################################
# Startup the moneydog script
# the initial file path:
# - MoneyDog
#  - trunk
#  - branches
#  - google_appengine
###########################################################
import os
import sys

cwd = os.path.abspath('.')

PROJECT_DIR   = cwd
GAE_DIR       = os.path.join(cwd,     '../google_appengine-1.1')
dev_appserver = os.path.join(GAE_DIR, 'dev_appserver.py'   )

#change the global variable for execute dev_appserver file.
my_globals = globals()
my_globals['__file__'] = dev_appserver

#sys.argv = [dev_appserver, 'moneydog-tw']
sys.argv[0] = dev_appserver
if len(sys.argv) == 1:
    sys.argv.append(cwd)
else:
    sys.argv[1] = cwd

#change current working dir
os.chdir( GAE_DIR )

#execute GAE
execfile(dev_appserver, my_globals)
