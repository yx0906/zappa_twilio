#! /usr/bin/env python
from datetime import date, datetime
import pytz

from flask import Flask, request, render_template
from twilio.twiml.messaging_response import MessagingResponse
import boto3
from boto3.dynamodb.conditions import Key, Attr

app = Flask(__name__)
tz_sh = pytz.timezone("Asia/Shanghai")


@app.route("/sms", methods=['GET', 'POST'])
def sms_store():
    """Save incoming messages to dynamoDB."""
    now = datetime.now(tz=tz_sh)
    sms = {
            "text": request.values.get('Body', None),
            "from": request.values.get('From', None),
            "date": now.strftime("%F"),
            "time": now.strftime("%T")
    }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('SMS')
    table.put_item(Item=sms)
    return str(sms)

@app.route("/demo")
def query_display():
    "query all items today saved and display"
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('SMS')
    response = table.query(
                    KeyConditionExpression=Key('date').eq(datetime.now(tz=tz_sh).strftime("%F")))
    sms_texts = (f"{i['from']} {i['time']}:   {i['text']}"
                        for i in sorted(response['Items'], key=lambda x:x["time"]))
    return render_template("demo.html", texts=sms_texts)

if __name__ == "__main__":
    app.run(debug=True)

