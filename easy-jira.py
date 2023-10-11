import pandas as pd
import sys
import argparse
from jproperties import Properties

configs = Properties()


parser = argparse.ArgumentParser(description="Easy Jira CSV to WEG XLSX converter")
parser.add_argument("file", help="CSV file to be processed")
parser.add_argument("sheet", help="Sheet name")

parser.add_argument("--split-by-issue", help="Split by issue", action="store_true")
parser.add_argument("--force-complete-day", help="Force complete day", action="store_true")
parser.add_argument("--force-at-least-complete-day", help="Force complete day", action="store_true")

args = parser.parse_args()
# Get the file from param
file = args.file
sheet = args.sheet

shouldSplitByIssue = args.split_by_issue
forceCompleteDay = args.force_complete_day
forceAtLeastCompleteDay = args.force_at_least_complete_day

      
# check if 'metadata.properties' exists
try:
  open('metadata.properties')
except IOError:
  print("metadata.properties file not found")
  exit()

# read properties from metadata.properties
with open('metadata.properties', 'rb') as f:
  configs.load(f, 'utf-8')

# get properties from metadata.properties
usuario = configs.get("user").data
projeto = configs.get("project").data
solicitante = configs.get("requester").data
empresa = configs.get("company").data
initial_time = configs.get("initial_time").data
interval_start = configs.get("interval_start").data
interval_end = configs.get("interval_end").data
complete_day_hours = float(configs.get("complete_day_hours").data)

def preprocess(file):
  a = pd.read_csv(file)
  # get first row
  newCols = a.iloc[0].copy()
  # get only values
  newCols.values
  newCols.iloc[0] = a.columns[0]
  a.columns = newCols
  # drop first 2 rows
  a = a.iloc[2:-1]
  # drop seccond column
  a = a.drop(columns=[a.columns[1]])
  a = a.set_index(a.columns[0])
  a = a.T
  a = a.iloc[:-1]
  return a

def hourStringToMinutes(string):
  # split by :
  splitted = string.split(":")
  # get first element and multiply by 60
  hours = int(splitted[0])*60
  # get second element
  minutes = int(splitted[1])
  # sum both
  return hours + minutes

def minutesToHourString(minutes):
  # get hours
  hours = int(minutes/60)
  # get minutes
  minutes = int(minutes%60)
  # if minutes < 10, add a 0 before
  if minutes < 10:
    minutes = "0"+str(minutes)
  if hours < 10:
    hours = "0"+str(hours)
  # return string
  return str(hours)+":"+str(minutes)

def get_issues(df):
  saidas = {}
  for i,r in df.iterrows():
    temp = []
    for c in df.columns:
      if pd.notna(r[c]):
        #split c by space and get the first element
        temp.append({
          "issue": c.split(" ")[0],
          "tempo": hourStringToMinutes(r[c])
          })
    if len(temp) > 0:
      saidas[i] = temp
  return saidas

def getTotalTime(dailyIssues):
  if forceCompleteDay:
    return complete_day_hours*60
  total = 0
  for issue in dailyIssues:
    total += issue["tempo"]

  if forceAtLeastCompleteDay and total < complete_day_hours*60:
    return complete_day_hours*60
  
  return total

def getIssuesString(dailyIssues):
  issues_str = ""
  for issue in dailyIssues:
    # issues divided by comma
    issues_str += issue["issue"] + ", "
  issues_str = issues_str[:-2]
  return issues_str

def generate_table(issues):
  table = []
  day_count = 0
  for key in issues:
    if len(issues[key])>0:
      day_issue = 0
      if(shouldSplitByIssue):
        day_issue_total_time = getTotalTime(issues[key])
        for issue in issues[key]:
          novo = get_line(usuario, empresa, key, projeto, solicitante, issue["issue"], issue["tempo"], day_issue, day_issue_total_time, day_count)
          day_issue += 1
          table.append(novo)
      else:
        tempo_total = getTotalTime(issues[key])
        issues_str = getIssuesString(issues[key])
        issues_str = issues_str[:-2]
        novo = get_line(usuario, empresa, key, projeto, solicitante,issues_str , tempo_total, day_issue, tempo_total,day_count)
        table.append(novo)
      day_count += 1
  df_saidas = pd.DataFrame(table)
  # save to excel, no index
  writeToExcel(df_saidas)
  # df_saidas.to_csv("saida.csv", index=False)

def writeToExcel(df):
  max_col = len(df.columns)
  max_col = chr(64+max_col)
  ano = sheet.split(" ")[1]
  mes = sheet.split(" ")[0]
  filename = str.upper(empresa)+"_"+str.upper(usuario)+"_"+ano+"_"+mes
  total_lines = len(df.index)

  writer = pd.ExcelWriter(filename+".xlsx", engine="xlsxwriter")
  df.to_excel(writer, sheet_name=sheet, index=False)
  workbook = writer.book
  worksheet = writer.sheets[sheet]
  # auto adjust columns
  for idx, col in enumerate(df):
    series = df[col]
    max_len = max((
      series.astype(str).map(len).max(),
      len(str(series.name))
      )) + 1
    worksheet.set_column(idx, idx, max_len)
  # first row bold
  format = workbook.add_format({'bold': True})
  worksheet.set_row(0, None, format)

  all_cols = "A2:"+max_col+str(total_lines+1)

  # border for every cell
  format = workbook.add_format({'border': 1})
  worksheet.conditional_format(all_cols, {'type': 'cell',
                                          'criteria': '!=',
                                          'value': '"-999"',
                                          'format': format})
  # "Data" column should be bold
  format = workbook.add_format({'bold': True})
  worksheet.conditional_format("C2:C"+str(total_lines+1), {'type': 'no_blanks',
                                          'format': format})
  
   # font should be Arial 10
  format = workbook.add_format({'font_name': 'Arial', 'font_size': 10})
  worksheet.conditional_format(all_cols, {'type': 'no_blanks',
                                          'format': format})
  
  # save
  writer.close()


def getTotalMorningMinutesLimit():
  return hourStringToMinutes(interval_start) - hourStringToMinutes(initial_time)

def getProbableMorningExitTime(totalTime):
  if totalTime > getTotalMorningMinutesLimit():
    return interval_start
  else:
    return minutesToHourString(hourStringToMinutes(initial_time) + totalTime)

def getProbableAfternoonEnteringTime(totalTime):
  if totalTime > getTotalMorningMinutesLimit():
    return interval_end
  else:
    return ""
  
def getProbableAfternoonExitTime(totalTime):
  if totalTime > getTotalMorningMinutesLimit():
    afternoonTime = totalTime - getTotalMorningMinutesLimit()
    return minutesToHourString(hourStringToMinutes(interval_end)+afternoonTime)
  else:
    return ""

def get_line(usuario, empresa, key, projeto, solicitante, issue, tempo, day_issue, total,day_count):
  line = {}
  if day_count == 0 and day_issue == 0:
    line["Nome"] = usuario
    line["Empresa"] = empresa
  else:
    line["Nome"] = ""
    line["Empresa"] = ""

  if day_issue == 0:
    line["Data"] = key
    line["Entrada manhã (Hs)"] = initial_time
    line["Saída manhã (Hs)"] = getProbableMorningExitTime(total)
    line["Entrada tarde (Hs)"] = getProbableAfternoonEnteringTime(total)
    line["Saída tarde (Hs)"] = getProbableAfternoonExitTime(total)
    line["Total (Hs)"] = minutesToHourString(total)
  else:
    line["Data"] = ""
    line["Entrada manhã (Hs)"] = ""
    line["Saída manhã (Hs)"] = ""
    line["Entrada tarde (Hs)"] = ""
    line["Saída tarde (Hs)"] = ""
    line["Total (Hs)"] = ""

  line["Projeto"] = projeto
  line["Solicitante"] = solicitante
  line["Tempo"] = minutesToHourString(tempo)
  line["Atividade"] = issue
  return line

df = preprocess(file)
issues = get_issues(df)
generate_table(issues)