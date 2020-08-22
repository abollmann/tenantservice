from pymodm import fields, MongoModel
from pymodm.errors import ValidationError


class Tenant(MongoModel):
    first_name = fields.CharField(required=True)
    last_name = fields.CharField(required=True)
    email = fields.EmailField(required=True)
    devices = fields.ListField(field=fields.ObjectIdField(required=False), required=False)

    def clean(self):
        if list(Tenant.objects.raw({'email': self.email})):
            raise ValidationError('eMail already in use.')

    def to_dict(self):
        as_dict = self.to_son().to_dict()
        del as_dict['_cls']
        return as_dict
