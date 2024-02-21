import json

v, r = 2.2, "baikal"
with open("settings.json") as file:
    JSON = json.load(file)

# retrieve config variables
try:
    BOT_TOKEN = JSON['BOT_TOKEN']
    BOT_OWNERS = JSON['BOT_OWNERS']
    AD_MESSAGE = JSON['AD_MESSAGE']
    DEBUG = JSON['DEBUG']
    ITEMS = JSON['ITEMS']
    GET = JSON['GET']
    SITES = JSON['SITES']
    VERSION = JSON['Version']
    if VERSION != v:
        update = input(f"⚠️ New installed version! Upgrade to {v}? [y/N]: ")
        if update in ['y', 'Y', 'yes', 'Yes', '1']:
            with open('settings.json', 'r+') as file:
                data = file.read().split("\n\n")[1]
                file.seek(0)
                file.write("{\n" + f'  "Version": {v},\n  "Release": "{r}",\n\n{data}')
                JSON['Version'], JSON['Release'] = v, r
        else: exit()
    DEBUG_MSG = " / DEBUG MODE" if DEBUG else ""
    MSG = f"✅ Success ⚡️v{JSON['Version']}({JSON['Release']})" + DEBUG_MSG

except (TypeError, ValueError) as ex:
    print("Error while reading config:", ex)
