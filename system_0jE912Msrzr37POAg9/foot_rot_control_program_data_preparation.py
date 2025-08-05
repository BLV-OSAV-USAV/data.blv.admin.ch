#import pandas as pd
#import openpyxl

#df = pd.read_excel('./ogd/foot_rot_control_program/in/Moderhinke Dashboard.xlsx')

#df.to_csv("./ogd/foot_rot_control_program/Cubes/moderhinke-cube.csv", sep=";")
#df.to_csv("./ogd/foot_rot_control_program/eradication-foot-rot.csv", index=False)


import os
import re
from ftplib import FTP
import pandas as pd

# GitHub secret
FTP_PASS = os.environ["FTP_PASS_DATEN_ALVPH"]

# Local directory to save downloaded files
local_directory = "temporary_files"

# Connect to the FTP server
ftp = FTP('ftp.blv-data-ingest.ch')
ftp.login(user='Daten_ALVPH@blv-data-ingest.ch', passwd=FTP_PASS)
ftp.cwd('Moderhinke_2024_2025')

# Get a list of files on the server
files = []
ftp.retrlines('LIST', files.append)

ftp.quit()

# Speicherort der Textdatei
output_path = os.path.join(local_directory, "ftp_file_list.txt")

# Stelle sicher, dass das Verzeichnis existiert
os.makedirs(local_directory, exist_ok=True)

# Inhalt in Datei schreiben
with open(output_path, "w", encoding="utf-8") as f:
    for line in files:
        f.write(line + "\n")