import json
import constants


def donation_to_seconds(donation_amount):
    sorted_donations = sorted(constants.PATREON_PRICE_CHART.keys(), reverse=True)
    
    for amount in sorted_donations:
        if float(donation_amount) >= float(amount):
            return constants.PATREON_PRICE_CHART[amount]

    return 0
