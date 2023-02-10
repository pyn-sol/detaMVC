import datetime
import os
import re
from typing import Optional, Union, List

import pydantic
import ujson
from deta import Deta
from pydantic import Field, BaseModel, ValidationError

from odetam.field import DetaField
from odetam.query import DetaQuery, DetaQueryStatement, DetaQueryList


class DetaError(BaseException):
    pass


class ItemNotFound(DetaError):
    pass


class NoProjectKey(DetaError):
    pass


class InvalidDetaQuery(DetaError):
    pass


DETA_BASIC_TYPES = [dict, list, str, int, float, bool]
DETA_OPTIONAL_TYPES = [Optional[type_] for type_ in DETA_BASIC_TYPES]
DETA_BASIC_LIST_TYPES = [
    List[type_] for type_ in DETA_BASIC_TYPES + DETA_OPTIONAL_TYPES
]
DETA_TYPES = DETA_BASIC_TYPES + DETA_OPTIONAL_TYPES + DETA_BASIC_LIST_TYPES


class Alert:
    """Use this class to make alerts on any page"""
    def __init__(self, message = None, alert_type = 'danger'):
        self.type = alert_type
        self.message = message


def handle_db_property(cls, deta_class):
    if cls._db:
        return cls._db
    try:
        # changed to 'DETA_PROJECT_KEY' because Deta SDK searches for it by default
        # https://github.com/deta/deta-python/blob/master/deta/utils.py
        deta = deta_class(os.getenv("DETA_PROJECT_KEY"))
    except (AttributeError, AssertionError, ValueError):
        raise NoProjectKey(
            "Ensure that the 'DETA_PROJECT_KEY' environment variable is set to your "
            "project key and then restart the server."
        )
    cls._db = deta.Base(cls.__db_name__)
    return cls._db


class DetaModelMetaClass(pydantic.main.ModelMetaclass):
    def __new__(mcs, name, bases, dct):
        cls = super().__new__(mcs, name, bases, dct)
        cls.Config.arbitrary_types_allowed = True  # but, be careful if you use them!
        if getattr(cls.Config, "table_name", None):
            cls.__db_name__ = cls.Config.table_name
        else:
            cls.__db_name__ = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
        cls._db = None

        for name, field in cls.__fields__.items():
            setattr(cls, name, DetaField(field=field))
        return cls

    @property
    def __db__(cls):
        return handle_db_property(cls, Deta)


class BaseDetaModel(BaseModel):
    __db__ = None
    key: Optional[str] = Field(
        None, title="Key", description="Primary key in the database"
    )

    # overwriting odetam's implementation
    def _serialize(self, exclude=None):
        if not exclude:
            exclude = []
        as_dict = {}
        for field_name, field in self.__class__.__fields__.items():
            if field_name == "key" and not self.key:
                continue
            if field_name in exclude:
                continue
            # this originally failed when 0, 0.0, or False. Now we only check for None instances
            if getattr(self, field_name, None) is None:
                as_dict[field_name] = None
                continue
            if field.type_ in DETA_TYPES:
                as_dict[field_name] = getattr(self, field_name)
            elif field.type_ == datetime.datetime:
                as_dict[field_name] = getattr(self, field_name).timestamp()
            elif field.type_ == datetime.date:
                as_dict[field_name] = int(getattr(self, field_name).strftime("%Y%m%d"))
            elif field.type_ == datetime.time:
                as_dict[field_name] = int(
                    getattr(self, field_name).strftime("%H%M%S%f")
                )
            else:
                as_dict[field_name] = ujson.loads(self.json(include={field_name}))[
                    field_name
                ]
        return as_dict

    # overwriting odetam's implementation
    @classmethod
    def _deserialize(cls, data):
        as_dict = {}
        for field_name, field in cls.__fields__.items():
            # this originally failed when 0, 0.0, or False. Now we only check for None instances
            if field_name not in data:
                as_dict[field_name] = field.type_()
            elif field.type_ in DETA_TYPES:
                as_dict[field_name] = data[field_name]
            elif field.type_ == datetime.datetime:
                as_dict[field_name] = datetime.datetime.fromtimestamp(data[field_name])
            elif field.type_ == datetime.date:
                as_dict[field_name] = datetime.datetime.strptime(
                    str(data[field_name]), "%Y%m%d"
                ).date()
            elif field.type_ == datetime.time:
                as_dict[field_name] = datetime.datetime.strptime(
                    str(data[field_name]), "%H%M%S%f"
                ).time()
            else:
                try:
                    as_dict[field_name] = ujson.loads(data.get(field_name))
                except (TypeError, ValueError):
                    as_dict[field_name] = data.get(field_name, None)
        return cls.parse_obj(as_dict)

    @classmethod
    def _return_item_or_raise(cls, item):
        if item is None or item.get("key") == "None":
            raise ItemNotFound("Could not find item matching that key")
        try:
            return cls._deserialize(item)
        except ValidationError:
            raise ItemNotFound("Could not find item matching that key")


class DetaModel(BaseDetaModel, metaclass=DetaModelMetaClass):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.key = self.key or None

    @classmethod
    def get(cls, key):
        """
        Get a single instance
        :param key: Deta database key
        :return: object found in database serialized into its pydantic object

        :raises ItemNotFound: No matching item was found
        """
        item = cls.__db__.get(key)
        return cls._return_item_or_raise(item)

    @classmethod
    def get_all(cls):
        """Get all the records from the database"""
        records = cls.__db__.fetch().items
        return [cls._deserialize(record) for record in records]

    @classmethod
    def query(
        cls, query_statement: Union[dict, DetaQuery, DetaQueryStatement, DetaQueryList]
    ):
        """Get items from database based on the query."""
        if any(isinstance(query_statement, d) 
                          for d in [DetaQuery, DetaQueryStatement, DetaQueryList]):
            query_statement = query_statement.as_query()
        found = cls.__db__.fetch(query_statement).items
        return [cls._deserialize(item) for item in found]

    @classmethod
    def delete_key(cls, key):
        """Delete an item based on the key"""
        cls.__db__.delete(key)

    @classmethod
    def put_many(cls, items):
        """Put multiple instances at once

        :param items: List of pydantic objects to put in the database
        :returns: List of items successfully added, serialized with pydantic
        """
        records = []
        processed = []
        for item in items:
            exclude = set()
            if item.key is None:
                exclude = {"key"}
            # noinspection PyProtectedMember
            records.append(item._serialize(exclude=exclude))
            if len(records) == 25:
                result = cls.__db__.put_many(records)
                processed.extend(result["processed"]["items"])
                records = []
        if records:
            result = cls.__db__.put_many(records)
            processed.extend(result["processed"]["items"])
        return [cls._deserialize(rec) for rec in processed]

    # overwriting odetam's 'save/put' implementation
    # to include extra arguments supported by Deta
    @classmethod
    def _db_put(cls, data, expire_in, expire_at):
        return cls.__db__.put(data, expire_in=expire_in, expire_at=expire_at)
    
    def save(self, expire_in: int or None = None, expire_at: int or None = None):
        """Saves the record to the database. Behaves as upsert, will create
        if not present. Database key will then be set on the object."""
        saved = self._db_put(self._serialize(), expire_in, expire_at)
        self.key = saved["key"]

    def update(self, data: dict):
        """Updates the record in the database with the provided data."""
        for k, v in data.items():
            if k in self.__dict__:
                setattr(self, k, v)
        self.save()

    def delete(self):
        """Delete the open object from the database. The object will still exist in
        python, but will be deleted from the database and the key attribute will be
        set to None."""
        if not self.key:
            raise DetaError("Item does not have key for deletion")
        self.delete_key(self.key)
        self.key = None

    def get_attribute_value(self, index=1):
        d = self.__dict__
        return d[list(d.keys())[index]]