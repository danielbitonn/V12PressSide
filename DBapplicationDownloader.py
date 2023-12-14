import json

import requests
import subprocess
import os
########################################################################################################################
# -------------------------------------------------------------------------------------------------------------------- #
# logger.debug("Message"): Log a debug message (level 10).
# logger.info("Message"): Log an informational message (level 20).
# logger.error("Message"): Log an error message (level 40).
# In case of unhandled exceptions, the logger will automatically log the details.
# -------------------------------------------------------------------------------------------------------------------- #
import logging
import csv
import sys
class CsvFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None):
        fmt = fmt or "%(asctime)s,%(levelname)s,%(filename)s,%(funcName)s,%(lineno)d,%(message)s"
        datefmt = datefmt or "%Y-%m-%d %H:%M:%S"
        super().__init__(fmt=fmt, datefmt=datefmt)
class CsvLogHandler(logging.FileHandler):
    def __init__(self, filename, mode='a', encoding=None, delay=False):
        super().__init__(filename, mode, encoding, delay)
    def emit(self, record):
        formatted_record = self.format(record)
        with open(self.baseFilename, self.mode, encoding=self.encoding, newline='') as file:                            # Write the formatted log record to the CSV file
            writer = csv.writer(file)
            writer.writerow(formatted_record.split(','))
def setup_logger(name, log_file, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = CsvLogHandler(log_file)
    handler.setFormatter(CsvFormatter())
    logger.addHandler(handler)
    return logger
def fata_error(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("fatal_crash", exc_info=(exc_type, exc_value, exc_traceback))
sys.excepthook = fata_error
log_file_name = 'standardLogger'
log_file_path = f'{log_file_name}.csv'
csv_header = 'Timestamp,Level,Filename,Function,Line,Message'
with open(log_file_path, mode='w') as log_file:
    log_file.write(csv_header + '\n')
# -------------------------------------------------------------------------------------------------------------------- #
### Initialize Logger ###
logger = setup_logger(log_file_name, log_file_path)
logger.info("My logger has been created!")
# -------------------------------------------------------------------------------------------------------------------- #
########################################################################################################################
########################################################################################################################
########################################################################################################################
def last_version_details():
    api_url = "https://api.github.com/repos/danielbitonn/V12PressSide/releases/latest"
    return requests.get(api_url).json()
def get_app_details(resp, app_details_path):
    logger.info("getting application details!")
    if os.path.exists(app_details_path):
        with open(app_details_path, 'r') as json_file:
            app_details = json.load(json_file)
    else:
        # files_in_folder = os.listdir(folder_path)
        app_details = {
            "update": True,
            "name": resp["assets"][0]["name"] or None,
            "tag": resp.get("tag_name", None) or None,
            "date_of_last_update": resp["assets"][0]["updated_at"] or None,
            "created_date": resp["assets"][0]["created_at"] or None,
            "published_at": resp["published_at"] or None,
            "browser_download_url": resp["assets"][0]["browser_download_url"] or None,
            "download_count": resp["assets"][0]["download_count"] or None
            }
    update_flag = app_details.get('update', False)
    app_details["update"] = False
    logger.info(f'Flag has been redefined to: {app_details["update"]}')
    with open(app_details_path, 'w') as file:
        json.dump(app_details, file, indent=4)
    logger.info(f'Existing app:{app_details["name"]} Download new app: {update_flag}')
    return app_details, update_flag
def download_and_run(resp):
    folder_path = "./auto_last_version"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    app_details_file_name = 'app_details.json'
    app_details_path = os.path.join(folder_path, app_details_file_name)
    app_details, update_flag = get_app_details(resp, app_details_path=app_details_path)
    file_url = resp['assets'][0]['browser_download_url'] if update_flag else None
    exe_files = [os.path.join(folder_path, entry) for entry in os.listdir(folder_path) if entry.endswith('.exe')] or None
    file_name = resp['assets'][0]['name'] if update_flag else os.path.basename(max(exe_files, key=os.path.getmtime))    # Sort files by modification time - basename = Extract just the file name
    if update_flag:
        # TODO: Internet issues handler mechanism
        if file_url.endswith(".exe"):
            try:
                downloaded_file = requests.get(file_url).content
                logger.info(f'{file_url} downloaded!')
                with open(os.path.join(folder_path, file_name), 'wb') as exe_file:
                    exe_file.write(downloaded_file)
                try:
                    subprocess.run([os.path.join(folder_path, file_name)], check=True)
                    logger.info(f'{file_name} Downloaded and running!')
                except Exception as ex:
                    logger.exception(f'{ex}')
            except Exception as ex:
                logger.exception(f'{ex}')
        elif file_url.endswith(".py"):
            try:
                downloaded_file = requests.get(file_url).text
                logger.info(f'{file_url} downloaded!')
                with open(os.path.join(folder_path, file_name), 'w') as script_file:
                    script_file.write(downloaded_file)
                try:
                    subprocess.run(['python', os.path.join(folder_path, file_name)], check=True)
                    logger.info(f'{file_name} Downloaded and running!')
                except Exception as ex:
                    logger.exception(f'{ex}')
            except Exception as ex:
                logger.exception(f'{ex}')
    else:
        if file_url.endswith(".exe"):
            try:
                subprocess.run([os.path.join(folder_path, file_name)], check=True)
                logger.info(f'{file_name} existed and running!')
            except Exception as ex:
                logger.exception(f'{ex}')
        elif file_url.endswith(".py"):
            try:
                subprocess.run(['python', os.path.join(folder_path, file_name)], check=True)
                logger.info(f'{file_name} Downloaded and running!')
            except Exception as ex:
                logger.exception(f'{ex}')
def main():
    try:
        response = last_version_details()
        try:
            download_and_run(response)
        except Exception as ex:
            logger.exception(f'{ex}')
    except Exception as ex:
        logger.error(f'{ex}')
if __name__ == "__main__":
    main()
