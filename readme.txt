Application Name
================
lan_client_detection


Application Version
===================
1.0

NCOS Devices Supported
======================
ALL


External Requirements
=====================
None


Application Purpose
===================
This application will generate syslogs and an alert when the connected client count is less than the configured threshold


Expected Output
===============
Uptime check passed, continuing...
{description} - fewer than {required_clients} clients connected for at least {detection_count * sleep_timer} seconds
LAN client detection supression enabled, sleeping for {supression_timer - sleep_timer} seconds
LAN client check complete, sleeping for {sleep_timer} seconds