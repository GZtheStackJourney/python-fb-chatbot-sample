import os
import sys
import json
import random
from utils import wit_response
from datetime import datetime
from enum import Enum
import logging

import requests
from flask import Flask, request


ATTACHMENT_FIELD = "attachment"
TYPE_FIELD = "type"
TEMPLATE_TYPE_FIELD = "template_type"
TEXT_FIELD = "text"
TITLE_FIELD = "title"
SUBTITLE_FIELD = "subtitle"
ITEM_FIELD = "item_url"
IMAGE_FIELD = "image_url"
BUTTONS_FIELD = "buttons"
PAYLOAD_FIELD = "payload"
URL_FIELD = "url"
ELEMENTS_FIELD = "elements"
QUICK_REPLIES_FIELD = "quick_replies"
CONTENT_TYPE_FIELD = "content_type"

# received message fields
POSTBACK_FIELD = "postback"

class ContentType(Enum):
    TEXT = "text"
    LOCATION = "location"

class AttachmentType(Enum):
    IMAGE = "image"
    TEMPLATE = "template"

class TemplateType(Enum):
    GENERIC = "generic"
    BUTTON = "button"
    RECEIPT = "receipt"

class ButtonType(Enum):
    WEB_URL = "web_url"
    POSTBACK = "postback"

class GenericElement:
    def __init__(self, title, subtitle, item_url, image_url, buttons):
        self.title = title
        self.subtitle = subtitle
        self.item_url = item_url
        self.image_url = image_url
        self.buttons = buttons

    def to_dict(self):
        element_dict = {BUTTONS_FIELD: [
            button.to_dict() for button in self.buttons]}
        if self.title:
            element_dict[TITLE_FIELD] = self.title
        if self.subtitle:
            element_dict[SUBTITLE_FIELD] = self.subtitle
        if self.item_url:
            element_dict[ITEM_FIELD] = self.item_url
        if self.image_url:
            element_dict[IMAGE_FIELD] = self.image_url
        return element_dict

class ActionButton:
    def __init__(self, button_type, title, url=None, payload=None): #button_type: WEB_URL or POSTBACK
        self.button_type = button_type
        self.title = title
        self.url = url
        self.payload = payload

    def to_dict(self):
        button_dict = {TYPE_FIELD: self.button_type.value}
        if self.title:
            button_dict[TITLE_FIELD] = self.title
        if self.url:
            button_dict[URL_FIELD] = self.url
        if self.payload:
            button_dict[PAYLOAD_FIELD] = self.payload
        return button_dict

class QuickReply:
    def __init__(self, title, payload,
                 image_url=None,
                 content_type=ContentType.TEXT):
        self.title = title
        self.payload = payload
        self.image_url = image_url
        self.content_type = content_type

    def to_dict(self):
        reply_dict = {CONTENT_TYPE_FIELD: self.content_type.value,
                      PAYLOAD_FIELD: self.payload}
        if self.title:
            reply_dict[TITLE_FIELD] = self.title
        if self.image_url:
            reply_dict[IMAGE_FIELD] = self.image_url
        log(reply_dict)
        return reply_dict

def send_generic(recipient_id, element_list):
	elements = [element.to_dict() for element in element_list]
	params = {
		"access_token": os.environ["PAGE_ACCESS_TOKEN"]
	}
	headers = {
		"Content-Type": "application/json"
	}
	data = json.dumps({
			"recipient": {
				"id": recipient_id
			},
			"message": {
					"attachment": {
						TYPE_FIELD: AttachmentType.TEMPLATE.value,
						PAYLOAD_FIELD: {
							TEMPLATE_TYPE_FIELD: TemplateType.GENERIC.value,
							ELEMENTS_FIELD: elements
						}
					}
				}
			})

	r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
	if r.status_code != 200:
		log(r.status_code)
		log(r.text)

def send_buttons(recipient_id, title, button_list):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=title))
    buttons = [button.to_dict() for button in button_list]
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
            "recipient": {
                "id": recipient_id
            },
            "message": {
                    "attachment": {
                        TYPE_FIELD: AttachmentType.TEMPLATE.value,
                        PAYLOAD_FIELD: {
                            TEMPLATE_TYPE_FIELD: TemplateType.BUTTON.value,
                            TEXT_FIELD: title,
                            BUTTONS_FIELD: buttons
                        }
                    }
                }
            })

    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def set_get_started_button_payload(payload):
		params = {
			"access_token": os.environ["PAGE_ACCESS_TOKEN"]
		}
		headers = {
			"Content-Type": "application/json"
	    }
		data = json.dumps({
				"setting_type": "call_to_actions",
				"thread_state": "new_thread",
				"call_to_actions": [{"payload": payload}]


				})

		r = requests.post("https://graph.facebook.com/v2.6/me/thread_settings", params=params, headers=headers, data=data)
		if r.status_code != 200:
			log(r.status_code)
			log(r.text)

def set_greeting_text(message_text):

        params = {
            "access_token": os.environ["PAGE_ACCESS_TOKEN"]
        }
        headers = {
            "Content-Type": "application/json"
        }
        data = json.dumps({
                 "setting_type":"greeting",
                 "greeting":{
                    "text":"Hi {{user_full_name}}!" + " " + message_text
                  }
                })

        r = requests.post("https://graph.facebook.com/v2.6/me/thread_settings", params=params, headers=headers, data=data)
        if r.status_code != 200:
            log(r.status_code)
            log(r.text)

def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_image(recipient_id, image):
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "image",
                "payload": {
                    "url": image
                }
            }
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_quick_replies(recipient_id, message_text, reply_list):
        log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

        params = {
            "access_token": os.environ["PAGE_ACCESS_TOKEN"]
        }
        headers = {
            "Content-Type": "application/json"
        }
        replies = list(dict())
        for r in reply_list:
            replies.append(r.to_dict())
        data = json.dumps({
        "recipient": {
                        "id": recipient_id
                    },
                    "message": {
                        "text": message_text,
                        "quick_replies": replies
                    }
        })

        r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
        if r.status_code != 200:
            log(r.status_code)
            log(r.text)

def typing(recipient_id, on=True):

	sender_action = "typing_on" if on else "typing_off"
	log("robot typing")
	params = {
		"access_token": os.environ["PAGE_ACCESS_TOKEN"]
	}
	headers = {
		"Content-Type": "application/json"
	}
	data = json.dumps({
		"recipient": {
			"id": recipient_id
		},
		"sender_action": sender_action
	})
	r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
	if r.status_code != 200:
		log(r.status_code)
		log(r.text)

def set_get_started_menu(Payload):
	params = {
		"access_token": os.environ["PAGE_ACCESS_TOKEN"]
	}
	headers = {
		"Content-Type": "application/json"
	}
	data = json.dumps({
		"get_started":{
			"payload":Payload
		}
			
	})

	r = requests.post("https://graph.facebook.com/v2.6/me/messenger_profile", params=params, headers=headers, data=data)
	if r.status_code != 200:
		log(r.status_code)
		log(r.text)

# def set_persistent_menu(Payload):
# 	params = {
# 		"access_token": os.environ["PAGE_ACCESS_TOKEN"]
# 	}
# 	headers = {
# 		"Content-Type": "application/json"
# 	}
# 	data = json.dumps({
# 		"setting_type" : "call_to_actions",
# 		"thread_state" : "existing_thread",
# 		"call_to_actions":[
# 			{
# 				"title":"Do Survey",
# 				"type":"postback",
# 				"payload":Payload
# 			},
# 			{
# 				"type":"web_url",
# 				"title":"Visit Page",
# 				"url":"https://www.facebook.com/testpageauto123/?ref=aymt_homepage_panel",
# 				"webview_height_ratio":"full"
# 			},
# 			{
# 				"title":"Show Templates",
# 				"type":"postback",
# 				"payload":"SHOW_TEMPLATES"
# 			}
# 		]
			
# 		})

# 	r = requests.post("https://graph.facebook.com/v2.6/me/thread_settings", params=params, headers=headers, data=data)
# 	if r.status_code != 200:
# 		log(r.status_code)
# 		log(r.text)

def set_persistent_menu(Payload, true=False):
	params = {
		"access_token": os.environ["PAGE_ACCESS_TOKEN"]
	}
	headers = {
		"Content-Type": "application/json"
	}
	data = json.dumps({
		"persistent_menu":[
			{
				"locale":"default",
				"composer_input_disabled": true,
				"call_to_actions":[
					{
						"title":"Do Survey",
						"type":"postback",
						"payload":Payload
					},
					{
						"type":"web_url",
						"title":"Visit Page",
						"url":"https://www.facebook.com/testpageauto123/?ref=aymt_homepage_panel",
						"webview_height_ratio":"full"
					},
					{
						"type":"nested",
						"title":"More Tools",
						"call_to_actions":[
							{
								"title":"Show Templates",
								"type":"postback",
								"payload":"SHOW_TEMPLATES"
							},
							{
								"type":"web_url",
								"title":"Latest News",
								"url":"https://news.google.com",
								"webview_height_ratio":"full"
							}
						]
					}
				]
			}
		]
			
		})

	r = requests.post("https://graph.facebook.com/v2.6/me/messenger_profile", params=params, headers=headers, data=data)
	if r.status_code != 200:
		log(r.status_code)
		log(r.text)

def remove_persistent_menu():
	params = {
		"access_token": os.environ["PAGE_ACCESS_TOKEN"]
	}
	headers = {
		"Content-Type": "application/json"
	}
	data = json.dumps({
		"setting_type" : "call_to_actions",
		"thread_state" : "existing_thread",
		"call_to_actions":[ ]
			
		})

	r = requests.post("https://graph.facebook.com/v2.6/me/thread_settings", params=params, headers=headers, data=data)
	if r.status_code != 200:
		log(r.status_code)
		log(r.text)




def log(msg, *args, **kwargs):  # simple wrapper for logging to stdout on heroku
    try:
        if type(msg) is dict:
            msg = json.dumps(msg)
        else:
            msg = unicode(msg).format(*args, **kwargs)
        print u"{}: {}".format(datetime.now(), msg)
    except UnicodeEncodeError:
        pass  # squash logging errors in case of non-ascii text
    sys.stdout.flush()


