#import pandas as pd
#import openpyxl

#df = pd.read_excel('./ogd/foot_rot_control_program/in/Moderhinke Dashboard.xlsx')

#df.to_csv("./ogd/foot_rot_control_program/Cubes/moderhinke-cube.csv", sep=";")
#df.to_csv("./ogd/foot_rot_control_program/eradication-foot-rot.csv", index=False)

import os
from ftplib import FTP

# GitHub secret
FTP_PASS = os.environ["FTP_PASS_DATEN_ALVPH"]

# Lokaler Speicherort für heruntergeladene Datei
local_directory = "temporary_files"
filename = "moderhinke-aktuelle-situation-input.csv"
local_path = os.path.join(local_directory, filename)

# Sicherstellen, dass das lokale Verzeichnis existiert
os.makedirs(local_directory, exist_ok=True)

# Verbindung zum FTP-Server
ftp = FTP('ftp.blv-data-ingest.ch')
ftp.login(user='Daten_ALVPH@blv-data-ingest.ch', passwd=FTP_PASS)

# In das richtige Verzeichnis wechseln
ftp.cwd("Moderhinke_2024_2025")

# Datei herunterladen
with open(local_path, "wb") as f:
    ftp.retrbinary(f"RETR {filename}", f.write)

ftp.quit()