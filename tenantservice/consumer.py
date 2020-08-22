from threading import Thread

from kafka import KafkaConsumer
from pymodm.errors import ValidationError

from tenantservice import logger
from tenantservice.producer import produce_data
from tenantservice.shared.error_handlers import handle_kafka_errors
from tenantservice.shared.exceptions import KafkaMessageException
from tenantservice.model import Tenant
from config import KAFKA_HOST, KAFKA_PORT, KAFKA_PREFIX
from tenantservice.shared.util import parse_message


class ApartmentCommandConsumer(Thread):
    daemon = True

    def run(self):
        consumer = KafkaConsumer(
            F'{KAFKA_PREFIX}-tenants-commands',
            bootstrap_servers=[F'{KAFKA_HOST}:{KAFKA_PORT}'],
            client_id=F'{KAFKA_PREFIX}-tenants-consumer',
            group_id=F'{KAFKA_PREFIX}-tenants-commands')

        for message in consumer:
            handle_message(message)


def handle_create(data, message_id):
    try:
        tenant = Tenant(**data).save().to_dict()
        logger.warn(F'Created {tenant}')
        return tenant, 200
    except ValidationError as error:
        logger.error(error.message)
        raise KafkaMessageException(error.message, message_id, 422)


def handle_get_all(data, message_id):
    tenants = [tenant.to_dict() for tenant in Tenant.objects.all()]
    logger.warn(F'Found {len(tenants)} entries')
    return tenants, 200


def handle_delete(data, message_id):
    email = data['email']
    tenant = Tenant.objects.raw({'email': email})
    if not list(tenant):
        logger.warn(F'Not found {data}')
        return {}, 404
    else:
        tenant.delete()
        logger.warn(F'{data} deleted')
        return {}, 204


def handle_devices(data, message_id):
    pass


ALLOWED_MESSAGE_TYPES = ['CREATE', 'GET_ALL', 'DELETE', 'DEVICES']
METHOD_MAPPING = {'CREATE': handle_create,
                  'GET_ALL': handle_get_all,
                  'DELETE': handle_delete,
                  'DEVICES': handle_devices}


@handle_kafka_errors
def handle_message(message):
    data, command_type, message_id = parse_message(message, ALLOWED_MESSAGE_TYPES)
    response_data, status_code = METHOD_MAPPING[command_type](data, message_id)
    produce_data({'data': response_data, 'status_code': status_code, 'id': message_id})
