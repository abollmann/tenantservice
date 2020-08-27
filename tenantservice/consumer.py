from threading import Thread

from bson import ObjectId
from kafka import KafkaConsumer

from tenantservice import logger
from tenantservice.shared.error_handlers import handle_kafka_errors
from tenantservice.model import Tenant
from config import KAFKA_HOST, KAFKA_PORT, KAFKA_PREFIX
from tenantservice.shared.util import parse_message


class TenantsConsumer(Thread):
    daemon = True

    def run(self):
        consumer = KafkaConsumer(
            F'{KAFKA_PREFIX}-tenants-commands',
            bootstrap_servers=[F'{KAFKA_HOST}:{KAFKA_PORT}'],
            client_id=F'{KAFKA_PREFIX}-tenants-consumer',
            group_id=F'{KAFKA_PREFIX}-tenants-commands')

        for message in consumer:
            handle_message(message)


def handle_distribute(data):
    tenant_id = ObjectId(data['tenant_id'])
    device_ids = [ObjectId(device_id) for device_id in data['device_ids']]
    tenant = list(Tenant.objects.raw({'_id': tenant_id}))[0]
    device_ids += tenant.devices
    Tenant.objects.raw({'_id': tenant_id}).update(
        {'$set': {'devices': device_ids}})
    logger.warn(F'Updated {tenant_id}')


def handle_remove(data):
    tenant_id = ObjectId(data['tenant_id'])
    Tenant.objects.raw({'_id': tenant_id}).update(
        {'$set': {'devices': []}})
    logger.warn(F'Removed devices from {tenant_id}')


ALLOWED_MESSAGE_TYPES = ['REMOVE_DEVICES', 'DISTRIBUTE_DEVICES']
METHOD_MAPPING = {'REMOVE_DEVICES': handle_remove,
                  'DISTRIBUTE_DEVICES': handle_distribute}


@handle_kafka_errors
def handle_message(message):
    data, command_type = parse_message(message, ALLOWED_MESSAGE_TYPES)
    METHOD_MAPPING[command_type](data)
