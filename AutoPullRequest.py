import getopt
import sys
import os
import ntpath
import shutil
from datetime import date
from random import randint

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def run_command(cmd):
    print cmd
    return os.system(cmd);

def main(argv):

    PROJECT_GIT_REPO = ""
    PROJECT_GIT_BRANCH = "master"

    GITHUB_USER = ""
    GITHUB_PASSWORD = ""

    source_dir = None
    workspace_dir = None
    pullrequest_message = None
    command = None
    commit_message = None

    try:
        opts, args = getopt.getopt(argv,
            "hc:w:u:p:a:x:m:",
            ["create-workspace=","workspace=","upgrade-from-source=","pullrequest=","repo=", "branch=", "message="])
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
        elif opt in ("--repo"):
            PROJECT_GIT_REPO = arg
        elif opt in ("--branch"):
            PROJECT_GIT_BRANCH = arg
        elif opt in ("-p", "--pullrequest"):
            pullrequest_message = arg
        elif opt in ("-m", "--message"):
            commit_message = arg


    if workspace_dir is not None:
        workspace_dir = os.path.abspath(os.path.normpath(workspace_dir))
    if source_dir is not None:
        source_dir = os.path.abspath(os.path.normpath(source_dir))
    
    print "workspace_dir = " + str(workspace_dir)
    print "source_dir = " + str(source_dir)
    print "repo = " + PROJECT_GIT_REPO
    print "branch = " + PROJECT_GIT_BRANCH
    print "command = " + command

    if commit_message is None or commit_message == "":
        commit_message = pullrequest_message

    if commit_message is None or commit_message == "":
        print 'need to set commit message'
        sys.exit()

    if PROJECT_GIT_REPO == "":
        print 'need to define --repo'
        sys.exit()
    else:
        if GITHUB_USER != "" and GITHUB_PASSWORD != "":
            PROJECT_GIT_REPO = PROJECT_GIT_REPO.replace('https://', "https://" + GITHUB_USER + ":" + GITHUB_PASSWORD + "@")

    if command == "c":
        if os.path.exists(workspace_dir):
            shutil.rmtree(workspace_dir)

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
        branch_name = "localization-" + today.isoformat() + "-" + str(randint(0,1000))
        print "create branch: " + branch_name
        run_command("cd " + workspace_dir + " && git branch " + branch_name);
        run_command("cd " + workspace_dir + " && git checkout " + branch_name);

        
        if os.path.exists(workspace_sub_dir):
            shutil.rmtree(workspace_sub_dir)

        shutil.copytree(source_dir, workspace_sub_dir)

        run_command("cd " + workspace_dir + " && git status");
        run_command("cd " + workspace_dir + " && git add \"" + dir_name + "\"");
        run_command("cd " + workspace_dir + " && git commit -a -m \"" + commit_message + "\"");
        run_command("cd " + workspace_dir + " && git push origin " + branch_name);

        if pullrequest_message is not None:
            # hub pull-request -m "Implemented feature X"
            run_command("cd " + workspace_dir 
                + " && export GITHUB_USER=" + GITHUB_USER 
                + " && export GITHUB_PASSWORD=" + GITHUB_PASSWORD 
                + " && hub pull-request -o -b " + PROJECT_GIT_BRANCH + " -m \"" + branch_name + "\"");

        run_command("cd " + workspace_dir + " && git checkout " + PROJECT_GIT_BRANCH);

    else:
        print 'need command'
        sys.exit()
   
if __name__ == "__main__":
   main(sys.argv[1:])