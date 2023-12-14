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
# -------------------------------------------------------------------------------------------------------------------- #
########################################################################################################################
########################################################################################################################
########################################################################################################################
def last_version_details():
    api_url = "https://api.github.com/repos/danielbitonn/V12PressSide/releases/latest"
    return requests.get(api_url).json()
def download_and_run(resp):
    save_path  = "./auto_last_version"
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    file_url = resp['assets'][0]['browser_download_url']
    file_name = resp['assets'][0]['name']
    if file_url.endswith(".exe"):
        downloaded_file = requests.get(file_url).content                                                                # Download the .exe file
        try:
            with open(os.path.join(save_path, file_name), 'wb') as exe_file:
                exe_file.write(downloaded_file)
            try:
                subprocess.run([os.path.join(save_path, file_name)], check=True)                                        # Execute the .exe file
                1/0
            except Exception as ex:
                logger.exception(f'{ex}')
                logger.error(f'{ex}')
        except Exception as ex:
            logger.error(f'{ex}')
    elif file_url.endswith(".py"):
        downloaded_file = requests.get(file_url).text                                                                   # Download py script
        try:
            with open(os.path.join(save_path, file_name), 'w') as script_file:
                script_file.write(downloaded_file)
                try:
                    subprocess.run(['python', os.path.join(save_path, file_name)], check=True)                          # Run the Python script
                except Exception as ex:
                    logger.error(f'{ex}')
        except Exception as ex:
            logger.error(f'{ex}')
def main():
    try:
        response = last_version_details()
        # TODO: Error mechanism if there isn't response.
        #       HTTPSConnectionPool(host='api.github.com'; port=443): Max retries exceeded with url: /repos/danielbitonn/V12PressSide/releases/latest (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x0000027BAAC7E208>: Failed to establish a new connection: [Errno 11001] getaddrinfo failed'))
        try:
            download_and_run(response)
        except Exception as ex:
            logger.error(f'{ex}')
    except Exception as ex:
        logger.error(f'{ex}')
if __name__ == "__main__":
    main()
