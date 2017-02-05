# -*- coding: utf-8 -*-
import os
import urllib2
import json

APP_KEY = os.environ["APP_KEY"]
API_ENDPOINT = "http://api.openweathermap.org/data/2.5/forecast"
CITY_MAP = {
    "tokyo": "1850147",
    "kobe": "1859171",
    "seattle": "5809844",
    "london": "4119617"
}
DEFAULT_CITY = "5106292"

def lambda_handler(event, context):
    print(event)

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'])


def on_launch(request):
    print("on_launch")
    return return_weather(DEFAULT_CITY)


def on_intent(request):
    print("on_intent")

    intent_name = request['intent']['name']
    print("intent name: {}".format(intent_name))

    if intent_name == "getWeather":
        return return_weather(DEFAULT_CITY)
    elif intent_name == "getWeatherWithCity":
        print(request["intent"]["slots"]["city"]["value"])
        if request["intent"]["slots"]["city"]["value"].lower() in CITY_MAP.keys():
            city_id = CITY_MAP[request["intent"]["slots"]["city"]["value"].lower()]
        else:
            city_id = DEFAULT_CITY # new york
        return return_weather(city_id)
    else:
        raise ValueError("Invalid intent")


# --------------- Functions that control the skill's behavior ------------------

def return_weather(city_id):
    print("return_weather")

    weather = request_weather(city_id)

    title = "Weather in {}".format(weather["name"])
    speech = "at now in {} is {}. {} degree. Humidity is {}%.".format(
        weather["name"],
        weather["weather"],
        weather["temp"],
        weather["humidity"]
    )
    card_text = "{} is {}.\n{} degree.\nHumidity {}%.".format(
        weather["name"],
        weather["weather"],
        weather["temp"],
        weather["humidity"]
    )
    image_url = "https://s3.amazonaws.com/jaws-alexa-handson/{}.png".format(weather["icon"])

    return build_speechlet_response(title ,speech, card_text, image_url)

def build_speechlet_response(title, speech, card_text, image_url):

    return_message = {
        "outputSpeech": {
            "type": "PlainText",
            "text": speech
        },
        "card": {
            "type": "Standard",
            "title": title,
            "text": card_text,
            "image": {
                "smallImageUrl": image_url
            }
        },
        "shouldEndSession": True
    }

    return build_response(return_message)

def build_response(speechlet_response):
    response = {
        'version': '1.0',
        'response': speechlet_response
    }
    print(response)
    return response

# --------------- Functions to get weather data ------------------

def request_weather(city_id):

    request_url = "{}?id={}&APPID={}&units=metric".format(API_ENDPOINT, city_id, APP_KEY)
    print(request_url)
    response = urllib2.urlopen(request_url)
    json_dict = json.loads(response.read())
    print(json_dict)

    weather = json_dict["list"][0]
    for data in json_dict["list"]:
        if data["dt"] < weather["dt"]:
            weather = data

    return {
        "name": json_dict["city"]["name"],
        "temp": weather["main"]["temp"],
        "humidity": weather["main"]["humidity"],
        "weather": weather["weather"][0]["main"],
        "icon": weather["weather"][0]["icon"]
    }
