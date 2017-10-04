#!/usr/bin/env python
import boto3
from ruamel import yaml


class export_r53(object):
    def __init__(self):
        self.r53 = boto3.client('route53')

    def get_zone_rr_sets(self, zone_id):
        """
        Return a generator of all resource record sets for a given zone
        """
        for rr_set in self.r53.list_resource_record_sets(HostedZoneId='{}'.format(zone_id))['ResourceRecordSets']:
            yield rr_set

    def get_zones(self):
        """
        Returns a generator of all the zones
        """
        for zone in self.r53.list_hosted_zones()['HostedZones']:
            yield zone

    def dump_all_zones(self):
        """
        Dump all zones from boto3.client('route53').list_hosted_zones()['HostedZones'] output
        """
        # Top level key for use with Ansible with_items:
        zones = {'route53_zones': {}}
        for zone in self.get_zones():
            zones['route53_zones'][zone['Name']] = []
            if zone['Config']['PrivateZone']:
                private_zone = True
            else:
                private_zone = False
            for rr in self.get_zone_rr_sets(zone['Id']):
                rr['ResourceRecords'] = [list(i.values())[0] for i in rr['ResourceRecords']]
                rr['Private'] = private_zone
                rr['Zone'] = zone['Name'][:-1]
                rr['HostedZoneId'] = zone['Id'][12:]
                rr['State'] = 'present'
                zones['route53_zones'][zone['Name']].append(rr)
        return zones


def main():
    export = export_r53()
    zone_dump = export.dump_all_zones()
    with open('export.yml', mode='w') as f:
        f.write(yaml.dump(zone_dump, indent=4, block_seq_indent=2))

if __name__ == '__main__':
    main()