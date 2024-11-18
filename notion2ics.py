from ics import Calendar, Event
import json
from notion_client import Client
from notion_objects import Database, DynamicNotionObject
import os
import re
            
def compile_event_template(page_dict: dict, template_text: str) -> str:
    """Compiles the event_<>_template from the template and the Notion page"""
    
    # Find all components to replace 
    components = re.findall(r'<(.*?)>', template_text)

    # Replace each component with the corresponding page property
    for component in components:
        template_text = template_text.replace(f"<{component}>", page_dict[component])

    # Return the compiled text
    return template_text

def create_event_from_page(page: DynamicNotionObject, date_property: dict) -> Event:
    """Creates an event from a notion page for a specific date property"""

    # Get settings for this event
    property_name = date_property["property_name"]
    event_name_template = date_property["event_name_template"]
    event_description_template = date_property["event_description_template"]

    # Get start and end date
    begin = page[property_name].start
    end = page[property_name].end

    # Compile event name and description
    name = compile_event_template(page, event_name_template)
    description = compile_event_template(page, event_description_template)

    # Create event 
    event = Event(name=name, begin=begin, end=end, description=description)

    # Make all day if begin and end are the same
    if event.begin == event.end:
        event.make_all_day()
    return event

# Get required environment variables
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
SETTINGS_PATH = os.getenv('SETTINGS_PATH')
ICS_PATH = os.getenv('ICS_PATH')

# Authenticate with Notion
notion_client = Client(auth=NOTION_TOKEN)

# Get calendar settings from json file
notion_calendar_settings = json.load(open(SETTINGS_PATH))

# Create calendar
calendar = Calendar()

# Query each database in the settings
for database in notion_calendar_settings["databases"]:
    notion_database = Database(DynamicNotionObject, database["id"], notion_client)
    notion_data = notion_database.query()

    # For each page, create events for each date property
    for page in notion_data:
        for date_property in database["date_properties"]:
            
            # If the date property is None, skip
            if page[date_property["property_name"]] is None:
                continue

            # Create event and add to calendar
            calendar.events.add(create_event_from_page(page, date_property))

# Write .ics file
with open(ICS_PATH, 'w') as f:
    f.writelines(calendar)
