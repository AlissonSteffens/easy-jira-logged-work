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
```

## Running

```bash
python3 easy-jira.py path/jira_trock.csv
```

You can also use a optional flag to change the default process to split days by issue (default is join issues by day)

```bash
python3 easy-jira.py path/jira_trock.csv --split-by-issue
```
