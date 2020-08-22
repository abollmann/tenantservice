from bson import ObjectId
from json import JSONEncoder


class ImprovedJSONEncoder(JSONEncoder):
    """ ObjectIds are not encoded by default so we must extend the JSONEncoder. """

    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return JSONEncoder.default(self, obj)


def encode_json(data):
    return ImprovedJSONEncoder().encode(data)
