import os
import time
from datetime import datetime
import re
import random
from slackclient import SlackClient


# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
noodlebot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
# EXAMPLE_COMMAND = "do"
SALUTATIONS = ["hi", "hello", "greetings", "cheers", "konnichiwa", "nihao", "hey", "woof", "yo", "what's up", "how's it hanging"]
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
OXFORD_TIME = datetime.strptime('2019-09-01', "%Y-%m-%d")

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == noodlebot_id:
                return message, event["channel"]
    return None, None


def parse_direct_mention(message_text):
    """    
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """  
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "I dunno how to do that. Do you need `help`?"

    # Finds and executes the given command, filling in response
    response = None
    
    # This is where you start to implement more commands!
    # remove case from command for processing
    command == command.lower()

    # if command.startswith(EXAMPLE_COMMAND):
    #   response = "Sure...write some more code then I can do that!"

    if command.startswith("do math"):
        command = command.replace("do math", "")
        number_list = command.split()
        
        try:
            if number_list[1] == '*':
                response = int(number_list[0]) * int(number_list[2])
            elif number_list[1] == '+':
                response = int(number_list[0]) + int(number_list[2])
            elif number_list[1] == '-':
                response = int(number_list[0]) - int(number_list[2])
            elif number_list[1] == '/':
                response = int(number_list[0]) / int(number_list[2])
            else:
                response = "Umm is your mathematical operator in the right place???"
        except:
            response = "Too hard for me. Did you format your problem like `do math 1 + 1`?"

    # some hard-coded commands
    if command.find("erin") != -1:
        erin_remarks = ["shoutout 2 my roomie! luv u xoxo", "erin's the bee's knees", "woof.", "erin carey! I know her.", "it's cuddletime with erin!!!", "do you have a peanut butter chicken bone 4 me?"]
        response = random.choice(erin_remarks)

    if command.find("weather") != -1:
        weather_type_list = ["balmy", "positively delightful", "stormy", "dreadfully humid", "dang cold", "really windy", "tornado-y", "jambala-y"]
        city_list = ["the French Riviera", "the Rockies", "Austin", "Chicago", "Tokyo", "Jakarta", "Bangalore", "Paris, Michigan", "Tampa", "the D", "Colorado", "Beijing", "Frankfurt", "Phnom Penh"]
        response = "I hear it's {} in {} this time of year.".format(random.choice(weather_type_list), random.choice(city_list))

    # repeat for say command
    if command.startswith("say"):
        command = command.replace("say", "")
        response = command
    
    # greeting
    if command in SALUTATIONS:
        response = random.choice(SALUTATIONS)

    if command == 'bark':
        response = "woof!"

    # countdowns
    if command == "oxford countdown" and (datetime.today() < OXFORD_TIME):
        response = str(abs(OXFORD_TIME - datetime.today()).days) + " days until OXFORD"

    if command.startswith("create countdown"):
        command = command.replace("create countdown", "")
        countdown_date = command.split()
        countdown_date = datetime.strptime(countdown_date[1], "%Y-%m-%d")
        response = str(abs(countdown_date - datetime.today()).days) + " days left"

    # catch-all for help
    if command.lower() == "help":
        response = "Right now I can `say` stuff, `do math`, `create countdown to yyyy-mm-dd` and `bark`."

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Robot Noodles connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        noodlebot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
