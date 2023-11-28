import json
import constants

def check_subbomb(donation_json):
    subsamount = donation_json["subs"]["number"]
    if constants.subbomb_type == 1:
        return 1
    if constants.subbomb_type == 2:
        subbomb_count = int(subsamount) // int(constants.subbomb_limit)
        return subbomb_count
    
def seconds_to_hms(seconds):
    """Converts seconds to a HH:MM:SS string."""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return h, m, s