import getopt
import sys
import os
import ntpath
import shutil
from datetime import date

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def run_command(cmd):
    print cmd
    return os.system(cmd);

def main(argv):

    PROJECT_GIT_REPO = "https://github.com/willsbor/AutoRepoTest.git"
    PROJECT_GIT_BRANCH = "master"

    GITHUB_USER = None
    GITHUB_PASSWORD = None

    source_dir = None
    workspace_dir = None
    pullrequest_message = None
    command = None

    try:
        opts, args = getopt.getopt(argv,
            "hc:w:u:r:a:x:",
            ["create-workspace=","workspace=","upgrade-from-source=","pullrequest="])
    except getopt.GetoptError:
        print 'error: parse.py wrong command'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
           print 'parse.py ????'
           sys.exit()
        elif opt in ("-c", "--create-workspace"):
            command = "c"
            workspace_dir = arg
        elif opt in ("-u", "--upgrade-from-source"):
            command = "u"
            source_dir = arg
        elif opt in ("-w", "--workspace"):
            workspace_dir = arg
        elif opt in ("-a"):
            GITHUB_USER = arg
        elif opt in ("-x"):
            GITHUB_PASSWORD = arg
        elif opt in ("-r", "--pullrequest"):
            command = "r"
            pullrequest_message = arg


    if workspace_dir is not None:
        workspace_dir = os.path.abspath(os.path.normpath(workspace_dir))
    if source_dir is not None:
        source_dir = os.path.abspath(os.path.normpath(source_dir))
    
    print "workspace_dir = " + str(workspace_dir)
    print "source_dir = " + str(source_dir)

    if command == "c":
        if not os.path.exists(workspace_dir):
            os.makedirs(workspace_dir)

        if os.path.exists(os.path.join(workspace_dir, '.git')):
            run_command("cd " + workspace_dir + " && git reset --hard HEAD");
            run_command("cd " + workspace_dir + " && git pull origin " + PROJECT_GIT_BRANCH);
        else:
            run_command("cd " + workspace_dir + " && git clone " + PROJECT_GIT_REPO + " --branch " + PROJECT_GIT_BRANCH + " --single-branch .")
            
    elif command == "u":
        dir_name = path_leaf(source_dir)
        workspace_sub_dir = os.path.join(workspace_dir, dir_name)

        today = date.today()
        branch_name = "localization-" + today.isoformat()
        print "create branch: " + branch_name
        run_command("cd " + workspace_dir + " && git branch " + branch_name);
        run_command("cd " + workspace_dir + " && git checkout " + branch_name);

        if os.path.exists(workspace_sub_dir):
            shutil.rmtree(workspace_sub_dir)

        shutil.copytree(source_dir, workspace_sub_dir)

        run_command("cd " + workspace_dir + " && git status");
        run_command("cd " + workspace_dir + " && git add \"" + dir_name + "\"");
        run_command("cd " + workspace_dir + " && git commit -a -m \"" + "test" + "\"");
        run_command("cd " + workspace_dir + " && git push origin " + branch_name);
        run_command("cd " + workspace_dir + " && git checkout " + PROJECT_GIT_BRANCH);

    elif command == "r":
        today = date.today()
        branch_name = "localization-" + today.isoformat()
        run_command("cd " + workspace_dir + " && git checkout " + branch_name);

        # hub pull-request -m "Implemented feature X"
        run_command("cd " + workspace_dir 
            + " && export GITHUB_USER=" + GITHUB_USER 
            + " && export GITHUB_PASSWORD=" + GITHUB_PASSWORD 
            + " && hub pull-request -o -m \"" + pullrequest_message + "\"");
        run_command("cd " + workspace_dir + " && git checkout " + PROJECT_GIT_BRANCH);
    else:
        print 'parse.py ????'
        sys.exit()
   
if __name__ == "__main__":
   main(sys.argv[1:])