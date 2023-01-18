import logging
from logging import FileHandler
from logging import Formatter
import os
import shutil

# global constants
KEYWORDS = ["zeugniss", "xml", "xlsx"]
DEBUG = True

# set the logger settings
FULL_LOG_FILE = "full_log.txt"
ERROR_LOG_FILE = "error_log.txt"
LOG_FORMAT = ('%(asctime)s [%(levelname)s] - %(message)s')

error_log = logging.getLogger("error_log")
error_log.setLevel(logging.ERROR)
error_log_handler = FileHandler(ERROR_LOG_FILE)
error_log_handler.setLevel(logging.ERROR)
error_log_handler.setFormatter(Formatter(LOG_FORMAT))
error_log.addHandler(error_log_handler)


# get all files in dirs by the path given as path: str
# forms and return a dict in form {folder:[files]}
def get_all_files(path: str)-> dict:
    files_dict = {}
    folders = [ f.path for f in os.scandir(os.path.join(os.getcwd(),path)) if f.is_dir() ]
    for folder in folders:
        files_dict[folder] = [ f.path for f in os.scandir(folder) if f.is_file() ]
    return files_dict



# categorize files by the given keywords in KEYWORDS list
# get the dict formed with get_all_files func as argument
# files without matches in names will get 'nicht_zugewiesen' category
# returs a list of dicts in form {"category":category, "file":file, "folder":folder, "user":username, "filename":filename}
def categorize_files(folders: dict) -> list:
    if DEBUG:
        [print(k,v) for k,v in folders.items()]
    categorized_lsit = []
    for folder, files in folders.items():
        if files:
            for file in files:
                category = create_category(file=file)
                if category == 'nicht_zugewiesen':
                    error_log.error(f'Datei: "{file}" kann nicht zugewiesen werden!')
                filename = os.path.basename(file)
                username = os.path.basename(folder)
                categorized_lsit.append({"category":category, "file":file, "folder":folder, "user":username, "filename":filename})
        else:
            error_log.error(f'Ordner: {folder} enthält keine Dateien')
    return categorized_lsit



# form category for a file based on keywords given in KEYWORDS list
def create_category(file: str) -> str:
    filename = os.path.basename(file)
    category = "nicht_zugewiesen"
    for keyword in KEYWORDS:
        if keyword.lower() in filename.lower():
            category = keyword
        if DEBUG:
            print(f'keyword: {keyword}, filename: {filename}')
    return category



# cretes folders in new given path with the same name as before,
# then creates a new folder for each found category and then
# copy the files into the folder with corresponding category
# takes list formed with categorize_files method and a new path
def replace_files(files: list, new_path: str) -> None:
    if DEBUG:
        [print(x) for x in files]
    for item in files:
        existing_files = []
        new_folder = os.path.join(new_path, item['user'])
        new_category_folder = os.path.join(new_path, new_folder, item['category'])
        new_filepath = os.path.join(new_path, new_folder, new_category_folder, item['filename'])
        
        if not os.path.exists(new_folder):
            os.makedirs(new_folder)
        if os.path.exists(new_category_folder):
            existing_files = [ f.path for f in os.scandir(new_category_folder) if f.is_file() ]
        else:
            os.makedirs(new_category_folder)
            
        same_name = True
        if DEBUG:
            print(existing_files)
        while same_name:
            if DEBUG:
                print(f'new_fp: {new_filepath}')
            if new_filepath in existing_files:
                new_filepath = f"{new_filepath.rsplit('.', 1)[0]} Kopie.{new_filepath.rsplit('.', 1)[1]}"
            else:
                same_name = False
        shutil.copyfile(item['file'], new_filepath)



# main method of the script
def main():
    files = categorize_files(get_all_files("old_location"))
    # create result folder to place files into
    curr_path = os.path.join(os.getcwd(), "00-bearbeitet")
    if not os.path.exists(curr_path):
        os.makedirs(curr_path)
    replace_files(files, str(curr_path))



if __name__ == '__main__':
    main()