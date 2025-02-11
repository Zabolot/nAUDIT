import shutil

def check_command(command): 
    return shutil.which(command) is not None