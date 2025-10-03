import pandas as pd

df = pd.read_excel("catalogo_sev.xlsx")
df = df.dropna(subset=["NÚMERO"])
df = df.dropna(subset=["GRAVEDAD"])

high_dicc = []
for index, row in df.iterrows():

  

    numero = str(row["NÚMERO"]).strip()
    if not numero:
        continue

    severity = str(row["GRAVEDAD"]).strip()
    severity = severity.upper()

    if severity == "GRAVE":
        high_dicc.append(numero)
    
print(high_dicc)
with open("high_list.txt", "w") as f:
    for i in high_dicc:
        f.write(str(i) + "\n")


