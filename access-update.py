#!/usr/bin/env python3
import os
import sys
import json
import http.client
import logging

# ENVIRONMENT VARIABLES
EMAIL = os.environ.get('EMAIL', '')
API_KEY = os.environ.get('API_KEY', '')
ACCOUNT_ID = os.environ.get('ACCOUNT_ID', '')
NETWORK_NAME = os.environ.get('NETWORK_NAME', '')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

# Check for required environment variables
if not EMAIL or not API_KEY or not ACCOUNT_ID or not NETWORK_NAME:
    logging.error("Error: Missing required environment variables")
    exit(1)

# Logging configuration
log = logging.getLogger()
log.setLevel(LOG_LEVEL)
log.addHandler(logging.StreamHandler(sys.stdout)) # defaults to sys.stderr


# Get public IP address - using AWS CheckIP API
def get_public_ip():
    try:
        conn = http.client.HTTPSConnection("checkip.amazonaws.com")
        conn.request("GET", "/")
        res = conn.getresponse()
        data = res.read()
        ip = data.decode("utf-8").strip()
        logging.debug("Public IP: " + ip)
        return ip + "/32"
    except Exception as e:
        logging.error("Error getting public IP: " + str(e))
        exit(1)

# JSON data success check from API
def check_for_success(data):
    if data['success'] == True:
        return True
    else:
        logging.error("Error: " + data['errors'][0]['message'] + " Code: " +  str(data['errors'][0]['code']))
        return False

# List all network locations
def list_newtwork_locations():
    conn = http.client.HTTPSConnection("api.cloudflare.com")

    headers = {
        'Content-Type': "application/json",
        'X-Auth-Email': EMAIL,
        'X-Auth-Key': API_KEY
        }

    conn.request("GET", "/client/v4/accounts/" + ACCOUNT_ID + "/gateway/locations", headers=headers)

    res = conn.getresponse()
    data = res.read()
    data = json.loads(data)

    if not check_for_success(data):
        exit(1)

    # Get the location ID for the network that matches the NETWORK_NAME
    for location in data['result']:
        try:
            if location['name'] == NETWORK_NAME:
                logging.info("Network location found: " + NETWORK_NAME)
                logging.debug("Location Name: " + location['name'])
                logging.debug("Location ID: " + location['id'])
                logging.debug("Location Updated: " + location['updated_at'])
                for network in location['networks']:
                    logging.debug("Network ID: " + network['id'])
                    logging.debug("Network IP: " + network['network'])
                return location['id']
        except Exception as e:
            logging.error("Error: " + str(e))
            exit(1)
            
    logging.error("Error: Network location not found: " + NETWORK_NAME)
    exit(1)


# Get network location
def get_network_location(location_id):
    conn = http.client.HTTPSConnection("api.cloudflare.com")

    headers = {
        'Content-Type': "application/json",
        'X-Auth-Email': EMAIL,
        'X-Auth-Key': API_KEY
        }

    conn.request("GET", "/client/v4/accounts/" + ACCOUNT_ID + "/gateway/locations/" + location_id, headers=headers)

    res = conn.getresponse()
    data = res.read()
    data = json.loads(data)

    if not check_for_success(data):
        logging.error("Error getting location: " + location_id)
        exit(1)

    return data['result']

def update_network_location(location, ip_cidr):
    location_id = location['id']

    logging.info("Updating location: " + location['name'] + "|" + location_id +  " with IP: " + ip_cidr[0].get('network'))

    conn = http.client.HTTPSConnection("api.cloudflare.com")

    headers = {
        'Content-Type': "application/json",
        'X-Auth-Email': EMAIL,
        'X-Auth-Key': API_KEY
        }

    payload = {
        "name": location['name'],
        "client_default": location['client_default'],
        "ecs_support": location['ecs_support'],
        "networks": ip_cidr
          
    }

    conn.request("PUT", "/client/v4/accounts/" + ACCOUNT_ID + "/gateway/locations/" + location_id, json.dumps(payload), headers=headers)

    res = conn.getresponse()
    data = res.read()
    data = json.loads(data)

    if not check_for_success(data):
        logging.error("Error updating location: " + location['name'] + "|" + location_id)
        exit(1)
    
    logging.info("Location updated successfully: " + location['name'] + "|" + location_id)
    logging.info("New IP: " + ip_cidr[0].get('network'))
    logging.info("Last updated: " + data['result']['updated_at'])
    


# MAIN function execution
location_id = list_newtwork_locations()
location = get_network_location(location_id)

# Update the network location with the new IP
ip_cidr = []
public_ip = get_public_ip()
ip_cidr.append({"network": public_ip})

# Check if the IP is already in the network
if location['networks'][0]['network'] == public_ip:
    logging.info("IP is already in the network: " + public_ip)
    exit(0)
else:
    update_network_location(location, ip_cidr)
    exit(0)
