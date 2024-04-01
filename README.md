# easy-jira-logged-work

Python script to simplify creating reports from jira's TROCK logged works

## Setup

First of all, you need to install the requirements

```bash
pip3 install -r requirements.txt
```

Then, you need to change the file "metadata.properties" with your contract information

```properties
user = Alisson Steffens Henrique
project = Projeto 1
requester = Nome do Chefe
company = Acme Inc.
initial_time = 7:30
interval_start = 12:00
interval_end = 13:00
complete_day_hours = 8.8
hour_value = 30
meeting_time = 30 //in minutes
```

## Running

### Simple
```bash
python3 easy-jira.py path/jira_trock.csv "DEZ 2019"
```

### Optional flags

#### Force complete day
You can force your days to be complete (configurable in the metadata file) by using the optional flag

```bash
python3 easy-jira.py path/jira_trock.csv "DEZ 2019" --force-complete-day
```

#### Split by issue
You can also use a optional flag to change the default process to split days by issue (default is join issues by day)

```bash
python3 easy-jira.py path/jira_trock.csv "DEZ 2019" --split-by-issue
```

#### Force at least complete day
You can force your days to be at least complete (configurable in the metadata file) by using the optional flag

```bash
python3 easy-jira.py path/jira_trock.csv "DEZ 2019" --force-at-least-complete-day
```

#### Add daily meeting time
You can add a daily meeting time to your report by using the optional flag, this will add the meeting time (configurable in the metadata file) to each day

```bash
python3 easy-jira.py path/jira_trock.csv "DEZ 2019" --add-meeting-time
```
