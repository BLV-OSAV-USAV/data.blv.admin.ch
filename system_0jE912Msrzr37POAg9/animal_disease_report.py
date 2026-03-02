import requests
import pandas as pd

# SPARQL Endpoint
endpoint_url = "https://ld.admin.ch/query"

# Deine SPARQL-Abfrage
query = """
PREFIX schema: <http://schema.org/>
PREFIX cube: <https://cube.link/>
PREFIX admin: <https://schema.ld.admin.ch/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX disease: <https://agriculture.ld.admin.ch/fsvo/animal-disease/>

SELECT 
  (?date AS ?REPORTDATE)
  ?canton
  (?town AS ?MUNICIPALITY)

  ?diseasesGroup_de ?diseasesGroup_fr ?diseasesGroup_it ?diseasesGroup_en
  ?diseases_de ?diseases_fr ?diseases_it ?diseases_en
  ?species_de ?species_fr ?species_it ?species_en

  (COUNT(DISTINCT ?obs) AS ?count)
WHERE {
  <https://agriculture.ld.admin.ch/fsvo/animal-disease/observation/> cube:observation ?obs .

  ?obs disease:epidemics ?diseasesIRI ;
       disease:animal-specie ?speciesIRI ;
       schema:containedInPlace/schema:name ?town ;
       disease:internet-publication ?date ;
       disease:canton/schema:alternateName ?canton .

  # Disease labels
  OPTIONAL { ?diseasesIRI schema:name ?diseases_de FILTER(LANG(?diseases_de)="de") }
  OPTIONAL { ?diseasesIRI schema:name ?diseases_fr FILTER(LANG(?diseases_fr)="fr") }
  OPTIONAL { ?diseasesIRI schema:name ?diseases_it FILTER(LANG(?diseases_it)="it") }
  OPTIONAL { ?diseasesIRI schema:name ?diseases_en FILTER(LANG(?diseases_en)="en") }

  # Disease group
  ?diseasesIRI skos:broader ?diseasesGroupIRI .
  OPTIONAL { ?diseasesGroupIRI schema:name ?diseasesGroup_de FILTER(LANG(?diseasesGroup_de)="de") }
  OPTIONAL { ?diseasesGroupIRI schema:name ?diseasesGroup_fr FILTER(LANG(?diseasesGroup_fr)="fr") }
  OPTIONAL { ?diseasesGroupIRI schema:name ?diseasesGroup_it FILTER(LANG(?diseasesGroup_it)="it") }
  OPTIONAL { ?diseasesGroupIRI schema:name ?diseasesGroup_en FILTER(LANG(?diseasesGroup_en)="en") }

  # Species labels
  OPTIONAL { ?speciesIRI schema:name ?species_de FILTER(LANG(?species_de)="de") }
  OPTIONAL { ?speciesIRI schema:name ?species_fr FILTER(LANG(?species_fr)="fr") }
  OPTIONAL { ?speciesIRI schema:name ?species_it FILTER(LANG(?species_it)="it") }
  OPTIONAL { ?speciesIRI schema:name ?species_en FILTER(LANG(?species_en)="en") }

  # Filter "Alle" (de)
  FILTER (!BOUND(?diseasesGroup_de) || STR(?diseasesGroup_de) != "Alle")
}
GROUP BY 
  ?date ?canton ?town
  ?diseasesGroup_de ?diseasesGroup_fr ?diseasesGroup_it ?diseasesGroup_en
  ?diseases_de ?diseases_fr ?diseases_it ?diseases_en
  ?species_de ?species_fr ?species_it ?species_en
ORDER BY DESC(?date) ASC(?canton)
"""

# Anfrage an den Endpoint
response = requests.get(
    endpoint_url,
    params={"query": query},
    headers={"Accept": "application/sparql-results+json"}
)

response.raise_for_status()
data = response.json()

# JSON → pandas DataFrame
rows = []
for result in data["results"]["bindings"]:
    row = {var: result[var]["value"] for var in result}
    rows.append(row)

df = pd.DataFrame(rows)

# Datentypen anpassen (optional)
if "count" in df.columns:
    df["count"] = df["count"].astype(int)

# CSV speichern
output_file = "./ogd/animal_disease_notifications/animal_disease_report.csv"

df.to_csv(output_file, index=False, encoding="utf-8")

print(f"CSV erfolgreich gespeichert: {output_file}")
#df.shape