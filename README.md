# salt-conjur
Salt states for Conjur

## Functions
### machine_identity  
Provisions minions with Conjur identities using a [host factory token](https://developer.conjur.net/reference/services/host_factory/).
```
weather-service:
  conjur.machine_identity:
    - host_factory_token: {{ pillar['conjur']['host_factory_token'] }}
    - appliance_url: {{ pillar['conjur']['url'] }}
    - host_id: {{ grains['id'] }}
```