##import sys
##sys.path.append("C:\\Users\\Liew\\Envs\\test_bot\\Lib\\site-packages")
from wit import Wit

access_token = "YOUR_KEY"

client = Wit(access_token = access_token)

def wit_response(message_text):
    resp = client.message(message_text)
    entity = None
    value = None
    ##extract name and value of entity

    try:
        entity = list(resp['entities'])[0]
        value = resp['entities'][entity][0]['value']
    except:
        pass
    return (entity, value)

    
#print(wit_response("I live in Malaysia"))


