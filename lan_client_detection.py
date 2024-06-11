import ipaddress
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

        lan_clients = cp.get('status/lan/clients')
        lan_clients = [client for client in lan_clients if 'ip_address' in client and ipaddress.ip_address(client['ip_address']).version == 4]

        if len(lan_clients) < required_clients:
            detection_count += 1
            if detection_count == required_detections:
                description = cp.get('config/system/desc')
                cp.alert(f'{description} - fewer than {required_clients} clients connected for the last {detection_count * sleep_timer} seconds')
                cp.log(f'{description} - fewer than {required_clients} clients connected for the last {detection_count * sleep_timer} seconds')
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
    lan_client_alert()
