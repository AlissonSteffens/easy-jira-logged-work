import pandas as pd
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

properties = ["user", "project", "requester", "company", "initial_time", "interval_start", "interval_end", "complete_day_hours"]

usuario, projeto, solicitante, empresa, initial_time, interval_start, interval_end, complete_day_hours = (configs.get(prop).data for prop in properties)

complete_day_hours = float(complete_day_hours)

def preprocess(file):
  a = pd.read_csv(file)
  # get first row
  newCols = a.iloc[0].copy()
  newCols.iloc[0] = a.columns[0]
  a.columns = newCols
  # drop first 2 rows
  a = a.iloc[2:-1]
  # drop second column
  a = a.iloc[:, [0] + list(range(2, len(a.columns)))]
  a = a.set_index(a.columns[0])
  a = a.T
  a = a.iloc[:-1]
  return a

def hourStringToMinutes(time_string):
  hours, minutes = map(int, time_string.split(":"))
  return hours * 60 + minutes

def minutesToHourString(minutes):
  hours, minutes = divmod(minutes, 60)
  return "{:02d}:{:02d}".format(int(hours), int(minutes))

def get_issues(df):
  saidas = {}
  for i, r in df.iterrows():
    temp = [{"issue": c.split(" ")[0], "tempo": hourStringToMinutes(val)} for c, val in r.dropna().items()]
    if temp:
      saidas[i] = temp
  return saidas

def getTotalTime(dailyIssues):
  if forceCompleteDay:
    return complete_day_hours*60

  total = sum(issue["tempo"] for issue in dailyIssues)

  if forceAtLeastCompleteDay and total < complete_day_hours*60:
    return complete_day_hours*60
  
  return total

def getIssuesString(dailyIssues):
  issues_str = ", ".join(issue["issue"] for issue in dailyIssues)
  return issues_str

def generate_table(issues):
  table = []
  day_count = 0
  for key, daily_issues in issues.items():
    day_issue = 0
    if shouldSplitByIssue:
      day_issue_total_time = getTotalTime(daily_issues)
      for issue in daily_issues:
        novo = get_line(usuario, empresa, key, projeto, solicitante, issue["issue"], issue["tempo"], day_issue, day_issue_total_time, day_count)
        day_issue += 1
        table.append(novo)
    else:
      tempo_total = getTotalTime(daily_issues)
      issues_str = getIssuesString(daily_issues)
      novo = get_line(usuario, empresa, key, projeto, solicitante, issues_str, tempo_total, day_issue, tempo_total, day_count)
      table.append(novo)
    day_count += 1

  df_saidas = pd.DataFrame(table)
  writeToExcel(df_saidas)

meses = {
  "JAN": 1,
  "FEV": 2,
  "MAR": 3,
  "ABR": 4,
  "MAI": 5,
  "JUN": 6,
  "JUL": 7,
  "AGO": 8,
  "SET": 9,
  "OUT": 10,
  "NOV": 11,
  "DEZ": 12
}

def writeToExcel(df):
  max_col = chr(64 + len(df.columns))
  mes, ano = sheet.split(" ")
  mes_num = str(meses[mes]).zfill(2)
  username_with_underline = usuario.replace(" ", "-")
  empresa_name = empresa.split(" ")[0]
  filename = f"{empresa_name.upper()}_{username_with_underline.upper()}_{ano}_{mes_num}"

  writer = pd.ExcelWriter(f"{filename}.xlsx", engine="xlsxwriter")
  df.to_excel(writer, sheet_name=sheet, index=False)
  workbook = writer.book
  worksheet = writer.sheets[sheet]

  # auto adjust columns
  for idx, col in enumerate(df):
    
    max_len = max(df[col].astype(str).map(len).max(), len(str(df[col].name))) + 1
    worksheet.set_column(idx, idx, max_len)

  # first row bold
  format_bold = workbook.add_format({'bold': True})
  worksheet.set_row(0, None, format_bold)

  all_cols = f"A2:{max_col}{len(df.index) + 1}"

  # border for every cell
  format_border = workbook.add_format({'border': 1})
  worksheet.conditional_format(all_cols, {'type': 'cell', 'criteria': '!=', 'value': '"-999"', 'format': format_border})

  # "Data" column should be bold
  worksheet.conditional_format(f"C2:C{len(df.index) + 1}", {'type': 'no_blanks', 'format': format_bold})

  # font should be Arial 10
  format_font = workbook.add_format({'font_name': 'Arial', 'font_size': 10})
  worksheet.conditional_format(all_cols, {'type': 'no_blanks', 'format': format_font})

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
  line = {
    "Nome": "",
    "Empresa": "",
    "Data": "",
    "Entrada manhã (Hs)": "",
    "Saída manhã (Hs)": "",
    "Entrada tarde (Hs)": "",
    "Saída tarde (Hs)": "",
    "Total (Hs)": "",
    "Projeto": projeto,
    "Solicitante": solicitante,
    "Tempo": minutesToHourString(tempo),
    "Atividade": issue
  }

  if day_count == 0 and day_issue == 0:
    line["Nome"] = usuario
    line["Empresa"] = empresa

  if day_issue == 0:
    line["Data"] = key
    line["Entrada manhã (Hs)"] = initial_time
    line["Saída manhã (Hs)"] = getProbableMorningExitTime(total)
    line["Entrada tarde (Hs)"] = getProbableAfternoonEnteringTime(total)
    line["Saída tarde (Hs)"] = getProbableAfternoonExitTime(total)
    line["Total (Hs)"] = minutesToHourString(total)

  return line

df = preprocess(file)
issues = get_issues(df)
generate_table(issues)