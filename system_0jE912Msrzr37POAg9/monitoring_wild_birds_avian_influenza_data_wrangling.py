import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df_vor2024 = pd.read_excel("./ogd/monitoring_wild_birds_avian_influenza/input/Liste AI Wildvögel vor 2024.xlsx")
df_vor2024.columns = [col.split('\n')[0] for col in df_vor2024.columns]
df_vor2024['Fundort'] = df_vor2024['Fundort'].str.replace('\n', ' ')
df_vor2024['Probenahme-Datum'] = pd.to_datetime(df_vor2024['Probenahme-Datum'], format='%d.%m.%Y')
df_vor2024['Ergebnis'] = df_vor2024['Ergebnis'].str.replace('négatif', 'negativ')
df_vor2024['Ergebnis'] = df_vor2024['Ergebnis'].str.replace('positiv ', 'positiv')
df_vor2024['Ergebnis'] = df_vor2024['Ergebnis'].str.replace('Influenza A positiv', 'positiv')

df = pd.read_excel("./ogd/monitoring_wild_birds_avian_influenza/input/monitoring-wild-birds-avian-influenza.xlsx")
df.columns = [col.split('\n')[0] for col in df.columns]
df['Fundort'] = df['Fundort'].str.replace('\n', ' ')
df['Probenahme-Datum'] = pd.to_datetime(df['Probenahme-Datum'], format='%d.%m.%Y')


result = pd.concat([df_vor2024, df], ignore_index=True)
result = result.sort_values(by="Probenahme-Datum")
result.to_csv("./ogd/monitoring_wild_birds_avian_influenza/monitoring_wild_birds_avian_influenza.csv", index=False)

filtered_df = result.copy()
filtered_df = filtered_df[filtered_df['Probenahme-Datum'] >= "2024-01-01"]
filtered_df = filtered_df[filtered_df['Pathogenitaet'].isin(['highly pathogenic avian influenza (HPAI)']) | filtered_df['Pathogenitaet'].isna()]
filtered_df['Monat'] = filtered_df['Probenahme-Datum'].dt.to_period('M')
grouped = filtered_df.groupby(['Monat', 'Ergebnis']).size().reset_index(name='Anzahl')
grouped['Ergebnis'] = grouped['Ergebnis'].replace('positiv', '1')
grouped['Ergebnis'] = grouped['Ergebnis'].replace('negativ', '2')
grouped.to_csv("./ogd/monitoring_wild_birds_avian_influenza/Cubes/monitoring-wild-birds-avian-influenza-aggregated-cube.csv", index=False)

# Pivot-Tabelle erstellen
df_pivot = grouped.pivot(index="Monat", columns="Ergebnis", values="Anzahl")

# Plotting
x = np.arange(len(df_pivot))  # X-Achsen-Positionen basierend auf den Monaten
width = 0.25  # Breite der Balken

fig, ax = plt.subplots(figsize=(10, 6))

# Für jede Ergebnis-Gruppe Balken hinzufügen
for i, column in enumerate(df_pivot.columns):
    ax.bar(x + i * width, df_pivot[column], width, label=column)

# Achsen und Beschriftungen anpassen
ax.set_xlabel("Monat")
ax.set_ylabel("Anzahl")
ax.set_title("Untersuchungen von Wildvögeln auf Aviäre Influenza (AI)")
ax.set_xticks(x + width)  # Zentrieren der xticks
ax.set_xticklabels(df_pivot.index.astype(str), rotation=45)
ax.legend()
# Layout anpassen und anzeigen
plt.tight_layout()

plt.savefig("./ogd/monitoring_wild_birds_avian_influenza/plot.png", dpi=200, bbox_inches="tight")  # DPI und Bounding Box für Qualität

data = {
    'ID': [1,2],
    'DE': ['Anzahl positive HPAI H5N1', 'Anzahl negativ getestete Wildvögel'],
    'FR': ['Nombre de résultats positifs HPAI H5N1', 'Nombre d´oiseaux sauvages examinés négatifs'],
    'IT': ['Numero di HPAI H5N1 positivi', 'Numero di volatici selvatici analizzati negativi'],
    'EN': ['Number of positive HPAI H5N1', 'Number of wild birds tested negative']
}

# DataFrame erstellen
df_translation = pd.DataFrame(data)
df_translation.to_csv("./ogd/monitoring_wild_birds_avian_influenza/Cubes/monitoring-wild-birds-avian-influenza-translation.csv", index=False)
