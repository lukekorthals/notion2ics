# notion2ics V1
This action creates an .ics file from your notion databases.

I use notion to manage my plants and wanted to sync their watering and fertilizing schedules with my calendar. 
As I didnt find any free and easy solutions to do just this, I created this action. 
In my case, I run the action every day using a cron job and host the .ics file on a private cloud with a persistent url such that I can subscribe to it with my email client.

# Usage
Follow the example below to setup your repo for running this action.

## What you need
A repo with...
- a `secret holding your notion integration token` to authenticate with your account (refer to https://developers.notion.com/docs/create-a-notion-integration)
- a `notion_calendar_settings.json` file to specify the databases and date properties you want to use for creating events (refer to the example below)
- a `secret holding a private access token for your repo` to authenticate the action to commit the .ics file to your repository (refer to https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
- a `github workflow` file to run the action

## Example
This example creates events for watering, fertilizing and repotting plants from a notion database.
Each plant has a property for the next watering, fertilizing and repotting date from which the events are created.

### Repo Setup
```plain text
your-workflow-repo/
│
├── .github/
│   └── workflows/
│       └── my-workflow.yml         # A workflow running this action
│
└── notion_calendar_settings.json    # A settings file
```
This repo also contains two secrets:
- `NOTION_TOKEN`: Secret holding the API credentials for a notion integration with access to the relevant databases
- `ACCESS_TOKEN`: Secret holding a private access token that gives read and write access to only this repo

### JSON Settings

```json
{
    "databases": [
        {
            "id": "NOTION DATABASE ID", 
            "date_properties" : [
                {
                    "property_name": "Next Watering Date",
                    "event_name_template": "Water <Name>",
                    "event_description_template": "I need to water <Name> today."
                },
                {
                    "property_name": "Next Fertilizer Date",
                    "event_name_template": "Fertilize <Name>",
                    "event_description_template": "<Name> needs some food."
                },
                {
                    "property_name": "Next Repot Date",
                    "event_name_template": "Repot <Name>",
                    "event_description_template": "Time to repot <Name>."
                }
            ]
        }
    ]
}
```
Description of the settings json:
- `databases`: A list of databases you want to query. Each database should have the following properties:
    - `id`: The database id for querying the database. (refer to https://developers.notion.com/reference/retrieve-a-database)
    - `date_properties`: A list of date properties you want to use for creating events. Each date property should have the following properties:
        - `property_name`: The name of the date property in your notion database, used to extract the correct property from the notion page.
        - `event_name_template`: A template for the event name. Use `<PROPERTY NAME>` to insert properties from the notion page.
        - `event_description_template`: A template for the event description. Use `<PROPERTY NAME>` to insert the name of the plant.

Tipps for creating your settings json:
- The notion_calendar_settings.json file specifies all databases and date properties you want to use for creating events.
- You can add multiple data_properties if a single page in your database has multiple date properties.
- You can use date properties and notion formula properties that evaluate as dates.
- If a date property only has a start date, or if the start and end date are the same, a whole day event is created.
- You can dynamically create the event name and description by specifying notion properties inside <>.

### Workflow
```yaml
name: Daily Cron Job

on:
  workflow_dispatch:
  schedule:
    - cron: '0 0 * * *'

jobs:
  update-notion-calendar:
    runs-on: ubuntu-latest
    steps:
    - name: notion2ics
      uses: lukekorthals/notion2ics@v1
      with:
        github-token: ${{ secrets.ACCESS_TOKEN }}
        notion-token: ${{ secrets.NOTION_TOKEN }}
        settings-path: notion_calendar_settings.json
        ics-path: notion_calendar.ics
```
The action expects four inputs:
- `github-token`: A secret holding a private access token for your repo
- `notion-token`: A secret holding your notion integration token
- `settings-path`: The path to the settings json file
- `ics-path`: The path to the .ics file that should be created

In this example, the action runs every day at midnight and creates a new .ics file in the root of the repo.


