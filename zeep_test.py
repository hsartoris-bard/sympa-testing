#!/usr/bin/env python3

from zeep import CachingClient as Client

client = Client(wsdl='http://sympa.bard.edu/sympa/wsdl')
with client.settings(strict=False):
    response = client.service.authenticateRemoteAppAndRun('provisioning', 'SympApR0vision', 'USER_EMAIL=hsartoris@bard.edu', 'complexWhich', [])

print(response)
for item in response:
    print(dir(item))
    print(item.values())
