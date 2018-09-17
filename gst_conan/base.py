'''
A 'base' layer of utility methods.
'''

import ctypes
import os
import shlex
import shutil
import subprocess
import sys

def basenames(filenames:list) -> list:
    '''
    Executes `os.path.basename` on each element of the input to provide each element of the output.
    :param filenames: The input filenames.
    :return: The return value of `os.path.basename` for each of the input filenames.
    '''

    output = []
    for filename in filenames:
        output.append(os.path.basename(filename))

    return output

def copytree(srcFolder:str, destFolder:str, includeSubfolders:bool=True, onlyNewerSources:bool=True):
    '''
    Copy elements under `srcFolder` to under `destFolder`.
    :param srcFolder: The source folder.
    :param destFolder:  The destination folder.
    :param includeSubfolders:  If true, subfolders are also copied (with full contents).
    :param onlyNewerSources:  If true, a file is only copied if it does not exist at the destination location, or if the
    file at the destination location is older than the file to be copied.
    :return: None
    '''

    if not os.path.isdir(srcFolder):
        raise Exception("The source folder is not valid.")

    os.makedirs(destFolder, exist_ok=True)

    for item in os.listdir(srcFolder):
        src = os.path.join(srcFolder, item)
        dest = os.path.join(destFolder, item)
        if os.path.isdir(src) and includeSubfolders:
            copytree(src, dest)
        else:
            doCopy = True
            if onlyNewerSources and os.path.isfile(dest):
                doCopy = os.path.getmtime(src) > os.path.getmtime(dest)
            if doCopy:
                shutil.copy2(src, dest)

def currentUserIsPrivileged() -> bool:
    '''
    Determines whether the user has root (on linux) or administrative (on windows) privileges.
    :return: [bool]  On Linux, returns true if the effective user ID is 0 (meaning `root`), false otherwise.
    '''
    if isWindows():
        return 1 == ctypes.windll.shell32.IsUserAnAdmin()
    else:
        return 0 == os.geteuid()

def evaluate(cmd:str, throwable:bool=True, verbose:bool=True, workingFolder:str=None, fake:bool=False, env:dict=None) -> str:
    '''
    Executes the specified shell command and captures the console output.
    :param cmd:  The shell command.
    :param throwable:  If true, an exception is thrown if the command generates an error.
    :param verbose:  If true, the executed command is printed to the console.
    :param workingFolder:  The working folder for command execution.
    :param fake: If true, the command is not actually executed.  A stub message is sent to stdout.
    :param env:  The environment variables.  If None, the default environment variables are used (from os.environ).
    :return: The captured console output
    '''

    win = isWindows()

    if fake:
        if workingFolder == None:
            print("Fake command execution:")
        else:
            print("Fake command execution from "+workingFolder+":")
        print("\t" + cmd)
        return 0

    if verbose:
        if workingFolder == None:
            print("Executing command:")
        else:
            print("Executing command from "+workingFolder+":")
        print("\t" + cmd)

    sys.stdout.flush()

    try:
        if win:
            # windows will lex the command
            cmdLex = cmd
        else:
            cmdLex = shlex.split(cmd)
    except:
        if throwable:
            raise Exception("Unable to lex the command string:  " + cmd)
        return None

    if workingFolder != None:
        priorWorkingFolder = os.getcwd()
        os.chdir(workingFolder)

    try:
        if env is None:
            output = subprocess.check_output(cmdLex, shell=win)
        else:
            output = subprocess.check_output(cmdLex, shell=win, env=env)

        if (sys.version_info[0] >= 3):
            output = output.decode("utf-8", errors='replace')

        if win and len(output) >= 2:
            output = output[:-2]  # it always ends with "\r\n"
        elif len(output) >= 1:
            output = output[:-1]  # it always ends with "\n"

        return output
    except:
        if throwable:
            raise
        else:
            return None
    finally:
        if workingFolder != None:
            os.chdir(priorWorkingFolder)

def execute(cmd:str, throwable:bool=True, verbose:bool=True, workingFolder:str=None, fake:bool=False, env:dict=None) -> int:
    '''
    Executes the specified shell command.
    :param cmd:  The shell command.
    :param throwable:  If true, an exception is thrown if the command generates an error.
    :param verbose:  If true, the executed command is printed to the console.
    :param workingFolder:  The working folder for command execution.
    :param fake: If true, the command is not actually executed.  A stub message is sent to stdout.
    :param env:  The environment variables.  If None, the default environment variables are used (from os.environ).
    :return: The exit code of the function call.
    '''

    win = isWindows()

    if fake:
        if workingFolder == None:
            print("Fake command execution:")
        else:
            print("Fake command execution from "+workingFolder+":")
        print("\t" + cmd)
        return 0

    if verbose:
        if workingFolder == None:
            print("Executing command:")
        else:
            print("Executing command from "+workingFolder+":")
        print("\t" + cmd)

    sys.stdout.flush()

    try:
        if win:
            cmdLex = cmd
        else:
            cmdLex = shlex.split(cmd)
    except:
        if throwable:
            raise Exception("Unable to lex the command string:  " + cmd)
        return 1

    if workingFolder != None:
        priorWorkingFolder = os.getcwd()
        os.chdir(workingFolder)

    try:
        if throwable:
            if env is None:
                return subprocess.check_call(cmdLex, shell=win)
            else:
                return subprocess.check_call(cmdLex, shell=win, env=env)
        else:
            if env is None:
                return subprocess.call(cmdLex, shell=win)
            else:
                return subprocess.call(cmdLex, shell=win, env=env)
    finally:
        if workingFolder != None:
            os.chdir(priorWorkingFolder)

def getEnv(name:str) -> str:
    '''
    Gets the environment variable, where any internal variables are already decoded.
    :param name: The name of the variable.
    :return:  The value of the decoded variable.
    '''

    if isWindows():
        # Nested variables don't always resolve with `os.environ.get()` on Windows
        output = evaluate("echo %" + name + "%", verbose=False)
    else:
        output = os.environ.get(name)

    return output

def gstConanFolder() -> str:
    '''
    Gets the folder inside which the `gst-conan` script is located (i.e. the root folder of this repo).
    :return: The absolute folder path.
    '''
    output = os.path.dirname(os.path.dirname(__file__))
    return output

def isDarwin() -> bool:
    '''
    Determines whether the platform is Darwin (mac).
    :return: [bool] True if the platform is Darwin, false otherwise.
    '''
    return sys.platform.startswith("darwin")

def isLinux() -> bool:
    '''
    Determines whether the platform is Linux.
    :return: [bool] True if the platform is Linux, false otherwise.
    '''
    return sys.platform.startswith("linux")

def isWindows() -> bool:
    '''
    Determines whether the platform is Windows.
    :return: [bool] True if the platform is Windows, false otherwise.
    '''
    return sys.platform.startswith("win")

def messFolder() -> str:
    '''
    Gets the mess folder (i.e. the folder where intermediate files are stored, which are ignored from the git repo).
    :return: The absolute folder path.
    '''
    output = os.path.join(gstConanFolder(), "mess")
    return output