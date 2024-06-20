import time
from csclient import EventingCSClient

cp = EventingCSClient('lan_client_detection')

def check_uptime():
    uptime_req = 120

    uptime  = int(cp.get('status/system/uptime'))
    cp.log(f'Current uptime: {uptime} seconds')

    if uptime < uptime_req:
        cp.log(f'Sleeping for {uptime_req - uptime} seconds')  
        time.sleep(uptime_req - uptime)
    
    cp.log('Uptime check passed, continuing...')


def enable_client_usage():
    client_usage_enabled = cp.get('status/client_usage/enabled')

    while not client_usage_enabled:
        cp.log('Enabling client data usage...')
        cp.put('config/stats/client_usage/enabled', True)
        time.sleep(5)
        client_usage_enabled = cp.get('status/client_usage/enabled')

    cp.log('Client data usage enabled, continuing...')

    return client_usage_enabled


def get_client_data():
    cp.log('Getting client data...')
    client_data = cp.get('status/client_usage/stats')
    client_list = []

    for client in client_data:
        client_list.append(client['name'])

    return client_list


def lan_client_alert():
    detection_count = 0
    required_detections = 5
    required_clients = 5
    sleep_timer = 60
    supression_enabled = True
    supression_timer = 300

    while True:
        appdata = cp.get('config/system/sdk/appdata')
        
        for data in appdata:
            if data['name'] == 'required_detections':
                required_detections = int(data['value'])
            
            elif data['name'] == 'sleep_timer':
                sleep_timer = int(data['value'])
            
            elif data['name'] == 'required_clients':
                required_clients = int(data['value'])
            
            elif data['name'] == 'supression_enabled':
                supression_enabled =(data['value'])
                
                if supression_enabled.lower() == 'true':
                    supression_enabled = True
                
                else:
                    supression_enabled = False
            
            elif data['name'] == 'supression_timer':
                supression_timer = int(data['value'])

        lan_clients = get_client_data()

        if len(lan_clients) < required_clients:
            detection_count += 1

            if detection_count == required_detections:
                description = cp.get('config/system/desc')
                primary_wan = cp.get('status/wan/primary_device')

                if primary_wan.startswith('mdm-'):
                    primary_wan_info = cp.get(f'status/wan/devices/{primary_wan}/info')
                    primary_wan_name = primary_wan_info['disp_model']
                    primary_wan_carrier = primary_wan_info['carrier_id']
                else:
                    primary_wan_name = primary_wan
                    primary_wan_carrier = 'N/A'

                cp.alert(f'{description} - {len(lan_clients)} out of {required_clients} clients connected for the last {detection_count * sleep_timer} seconds. Connected clients: {lan_clients}. Primary WAN: {primary_wan_name} - {primary_wan_carrier}')
                cp.log(f'{description} - {len(lan_clients)} out of {required_clients} clients connected for the last {detection_count * sleep_timer} seconds. Connected clients: {lan_clients}. Primary WAN: {primary_wan_name} - {primary_wan_carrier}')
                detection_count = 0

                if supression_enabled:
                    cp.log(f'LAN client detection supression enabled, sleeping for {supression_timer - sleep_timer} seconds')
                    time.sleep(supression_timer - sleep_timer)

        else:
            detection_count = 0

        cp.log(f'LAN client check complete, sleeping for {sleep_timer} seconds')
        time.sleep(sleep_timer)


if __name__ == '__main__':
    cp.log('Starting LAN client alert tool')
    check_uptime()
    enable_client_usage()
    lan_client_alert()
