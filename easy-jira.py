import pandas as pd
import sys
# Get the file from param
file = sys.argv[1]


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
  usuario = "Alisson Steffens Henrique"
  projeto = 123456
  solicitante = "xxxxx"
  empresa = "Empresa"
  for key in issues:
    if len(issues[key])>0:
      novo = {
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
          "Atividade": ", ".join(issues[key])
      }
    table.append(novo)
  df_saidas = pd.DataFrame(table)
  # save to excel, no index
  df_saidas.to_excel("saida.xlsx", index=False)

df = preprocess(file)
issues = get_issues(df)
generate_table(issues)