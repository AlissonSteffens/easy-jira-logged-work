import pandas as pd
import sys
# Get the file from param
file = sys.argv[1]

shouldSplitByActivity = False

# check if has flag --split-by-issue
if len(sys.argv) >= 3:
  for arg in sys.argv:
    if arg == "--split-by-issue":
      shouldSplitByActivity = True
      
# check if 'metadata.properties' exists
try:
  open('metadata.properties')
except IOError:
  print("metadata.properties file not found")
  exit()

# read properties from metadata.properties
with open('metadata.properties') as f:
  lines = f.readlines()
  for line in lines:
    if line.startswith("user"):
      usuario = line.split("=")[1].strip()
    if line.startswith("project"):
      projeto = line.split("=")[1].strip()
    if line.startswith("requester"):
      solicitante = line.split("=")[1].strip()
    if line.startswith("company"):
      empresa = line.split("=")[1].strip()


def preprocess(file):
  a = pd.read_csv(file)
  # get first row
  newCols = a.iloc[0]
  # get only values
  newCols.values
  newCols[0] = a.columns[0]
  a.columns = newCols
  # drop first 2 rows
  a = a.iloc[2:-1]
  # drop seccond column
  a = a.drop(columns=[a.columns[1]])
  a = a.set_index(a.columns[0])
  a = a.T
  a = a.iloc[:-1]
  return a

def get_issues(df):
  saidas = {}
  for i,r in df.iterrows():
    temp = []
    for c in df.columns:
      if pd.notna(r[c]):
        #split c by space and get the first element
        temp.append(c.split(" ")[0])
    if len(temp) > 0:
      saidas[i] = temp
  return saidas

def generate_table(issues):
  table = []
  for key in issues:
    if len(issues[key])>0:
      if(shouldSplitByActivity):
        for issue in issues[key]:
          novo = get_line(usuario, empresa, key, projeto, solicitante, issue)
          table.append(novo)
      else:
        novo = get_line(usuario, empresa, key, projeto, solicitante, ", ".join(issues[key]))
        table.append(novo)
  df_saidas = pd.DataFrame(table)
  # save to excel, no index
  df_saidas.to_excel("saida.xlsx", index=False)
  # df_saidas.to_csv("saida.csv", index=False)


def get_line(usuario, empresa, key, projeto, solicitante, issue):
  return {
          "Nome": usuario,
          "Empresa": empresa,
          "Data": key,
          "Entrada manhã (Hs)": "7:30",
          "Saída manhã (Hs)": "12:00",
          "Entrada tarde (Hs)": "13:00",
          "Saída tarde (Hs)": "17:18",
          "Total (Hs)": "08:48",
          "Projeto": projeto,
          "Solicitante": solicitante,
          "Tempo": "08:48",
          "Atividade": issue
      }

df = preprocess(file)
issues = get_issues(df)
generate_table(issues)