import requests

incoming_message_string ={
    "plantSignal": "2500"
}
post_response = requests.post("http://0.0.0.0:6000/update", headers={"Content-Type": "application/json"}, json=incoming_message_string)

print("response http request:{}".format(post_response))