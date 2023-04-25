# alerTender
This repository contains a script to get alerts from [tender.gov.mn](https://www.tender.gov.mn/mn/index/) using customized keywords.

### Before running the script
Make sure to follow these steps before running the script:

- Delete the `config.json` uploaded list
- Update your custom keywords in the `config.json` file
- Update your `.env` file

### Running the script
To run the script, use the following command in the terminal:

```
python main.py
```

### Cronjob
If you want to run the script automatically, you can set up a cronjob. For example, the following cronjob will run the script every hour:

```
crontab -e
0 * * * * cd <THIS_REPO_PATH>; python main.py >/tmp/alertender.suc 2>/tmp/alertender.err;
```

### Dependencies
This script has the following dependencies:

- requests
- lxml
- datetime
- discord
- python-dotenv
