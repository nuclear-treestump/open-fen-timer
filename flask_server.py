from flask import Flask, request, jsonify
from queue import Queue
import json
import donation_utils
import constants
import plugin_patreon

app = Flask(__name__)
shared_queue = Queue()

@app.route('/donation',methods=['POST'])

def receive_donation():
    SUB_TIER = {
    "prime": {
        "name": "prime",
        "cost": float(constants.PRIME_COST)
    },
    "tier1": {
        "name": "tier1",
        "cost": float(constants.TIER1_COST)
    },
    "tier2": {
        "name": "tier2",
        "cost": float(constants.TIER2_COST)
    },
    "tier3": {
        "name": "tier3",
        "cost": float(constants.TIER3_COST)
    }
    }
    BIT_RATIO = float((constants.minute_multiplier * 60) / 100)
    SUB_COST_RATIO = float(constants.subcost)
    COST_MULTIPLIER = float(constants.minute_multiplier)
    # data = request.json
    #print(request.data)  # This will print the received JSON to the console
    #print(request.args)
    #print(request.__dict__)
    #return jsonify({'message': 'Donation received'}), 200
    print(request.form)
    extra_time = 0
    donation_json = {
        "datetime": request.form.get("datetime"),
        "donation_type": request.form.get("type"),
        "anonymous": (request.form.get("isanon", False)),
        "username" : request.form.get("username"),
        "time_added" : 0
    }
    if donation_json["donation_type"] == "bits":
        bitsamount = request.form.get('bitsamount')
        donation_json["time_added"] = int(bitsamount) * BIT_RATIO
    elif donation_json["donation_type"] == "patreon":
        patreonamount = float(request.form.get('patreonamount'))
        patreon_timeadded = plugin_patreon.donation_to_seconds(donation_amount=patreonamount)
        final_patreon_timeadded = float(patreon_timeadded)
        donation_json["time_added"] = int(final_patreon_timeadded)
    elif (donation_json["donation_type"] == "sub" or donation_json["donation_type"] == "giftsub" or donation_json["donation_type"] == "masssub"):
        subsmonthsdonation = (int(request.form.get("submonth", 1)))
        subsamount = request.form.get("subnumber").lower()
        substier = request.form.get("subtype").lower()
        print(f"SA: {subsamount}, SMD: {subsmonthsdonation}")
        if (int(subsamount) >= int(constants.subbomb_limit) and donation_json["donation_type"] == "masssub"):
            donation_json["subs"] = dict()
            donation_json["subs"]["number"] = subsamount
            donation_json["subs"]["subbomb"] = True
            subbomb_count = donation_utils.check_subbomb(donation_json=donation_json)
            extra_time = ((int(subbomb_count) * int(constants.subbomb)) * 60)
        if substier == SUB_TIER[substier]["name"]:
            subtime_add = ((((float(SUB_TIER[substier]["cost"]) * (int(subsamount)) * SUB_COST_RATIO)) * 60) * int(subsmonthsdonation)) # Sub Amount Prime / Tier 1 = $5.00 , which needs to equal 10$
        donation_json["time_added"] = int((subtime_add + extra_time))
    elif (donation_json["donation_type"] == "chatcmd" or donation_json["donation_type"] == "streamlabs"):
        print("Recieved ChatCMD request")
        chatcmd_add = request.form.get("dollarvalue")
        chatcmd_value = ((float(chatcmd_add) * COST_MULTIPLIER) * 60)
        print(chatcmd_value)
        print(f"chatCMD: {int(chatcmd_value)}")
        donation_json["time_added"] = chatcmd_value
    elif donation_json["donation_type"] == "chatctrl":
        print(f"Received C2 Command. Action: {request.form.get('action')}")
        donation_json["action"] = request.form.get('action')
    shared_queue.put(donation_json)
    return jsonify({'message': 'Donation received'}), 600

def run_flask_app():
    app.run(port=7878)
