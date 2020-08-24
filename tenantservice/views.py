import json

from flask import request
from pymodm.errors import ValidationError

from tenantservice import app, logger
from tenantservice.model import Tenant
from tenantservice.shared.json_encoder import encode_json

DEVICES_BASE_PATH = '/api/tenants'


@app.route(DEVICES_BASE_PATH, methods=['GET'])
def get_all():
    tenants = [tenants.to_dict() for tenants in Tenant.objects.all()]
    logger.warn(F'Found {len(tenants)} entries')
    return encode_json(tenants), 200


@app.route(DEVICES_BASE_PATH, methods=['POST'])
def create():
    data = json.loads(request.data.decode('utf-8'))
    try:
        tenant = Tenant(**data).save().to_dict()
        logger.warn(F'Created {tenant}')
        return encode_json(tenant), 200
    except ValidationError as error:
        logger.error(error.message)
        return error.message, 422

