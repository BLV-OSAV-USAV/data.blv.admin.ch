import pandas as pd


df = pd.read_excel('./ogd/foot_rot_control_program/in/Moderhinke Dashboard.xlsx')

df.to_csv("./ogd/foot_rot_control_program/Cubes/moderhinke-cube.csv", sep=";")
df.to_csv("./ogd/foot_rot_control_program/eradication-foot-rot.csv", index=False)