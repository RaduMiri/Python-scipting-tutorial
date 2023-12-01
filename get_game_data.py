import os
import json
import shutil
from subprocess import PIPE, run
import sys

GAME_DIR_PATTERN = "game" #The string we are looking for in the dir names
GAME_CODE_EXTENSION = ".go"
GAME_COMPILE_COMMAND = ["go", "build"] #Commands are just lists of all the different words you want to write

def find_all_game_paths(source):
    game_paths = []
    
    for root, dirs, files in os.walk(source): #walk gives you files, dirs, etc, then recusively look though all the dirs
        for directory in dirs: #dirs here are just the names of the directories, so we need to make the path with it
            if GAME_DIR_PATTERN in directory.lower():
                path = os.path.join(source, directory)
                game_paths.append(path)
        break #this time we only want to look in the first directory, so we break after the first itteration
    
    return game_paths

def get_name_from_paths(paths, to_strip):
    new_names = []
    for path in paths:
        _, dir_name = os.path.split(path)
        new_dir_name = dir_name.replace(to_strip, "")
        new_names.append(new_dir_name)
        
    return new_names

def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def copy_and_overwrite(source, dest): #Most copy dirs just copy the first layer of a dir, if you want the rest you need to call a rescusive function to go though the direcotries
    if os.path.exists(dest):
        shutil.rmtree(dest) #remove tree, it is a recursive delete
    shutil.copytree(source, dest) #copies recursively, I think
    
def make_json_metadata_file(path, game_dirs):
    data = {
        "gameNames": game_dirs,
        "numberOfGames": len(game_dirs)
    }
    
    with open(path, "w") as f: #using with, after we exit here the file is automatically closed
        json.dump(data, f) #saves json into a file
        
def compile_game_code(path):
    code_file_name = None
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(GAME_CODE_EXTENSION): #so that freak examples like .go.py are not classified as .go files
                code_file_name = file
                break
        break
    if code_file_name is None:
        return
    command = GAME_COMPILE_COMMAND + [code_file_name]
    run_command(command, path)
    
def run_command(command, path):
    cwd = os.getcwd()
    os.chdir(path) #change dir
    
    result = run(command, stdout = PIPE, stdin=PIPE, universal_newlines=True)
    #stdout standard output is where the command returns stuff
    #Pipe is a bridge between python code and where we run this command, allows communication with terminal
    print("compile result", result)
    
    os.chdir(cwd) #good practice when working with files is to reutrn to the original directory that you were in before running the function

def main(source, target): #We want to get the full path
    cwd = os.getcwd() #get currrent dir
    source_path = os.path.join(cwd, source) #better than just join or concat so that the path is made for the OS you are using
    target_path = os.path.join(cwd, target)
    
    game_paths = find_all_game_paths(source_path)
    new_game_dirs = get_name_from_paths(game_paths, "_game")
    
    create_dir(target_path)
    
    for src, dest in zip(game_paths, new_game_dirs): #zip makes a list of tuples that has are matched 2 by 2 like a cartesian product
        dest_path = os.path.join(target_path, dest)
        copy_and_overwrite(src, dest_path)
        compile_game_code(dest_path) #Here we compile the game, it give exe files for windows
    
    json_path = os.path.join(target_path, "metadata.json")
    make_json_metadata_file(json_path, new_game_dirs)
    
if __name__ == "__main__": #So the code works only if we specifically run this file directly, not when importing from here or sth else
    args = sys.argv
    if len(args)!= 3:
        raise Exception("Source and target dir ONLY!")
    source, target = args[1:]
    main(source, target)
    