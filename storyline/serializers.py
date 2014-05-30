# -*- coding: utf-8 -*-
"""storyline.serializers
"""
import collections
from . import states


class StateSerializer(object):
    @classmethod
    def loads(cls, plot, serialized):
        """Load state from a serialized string.
        """
        raise NotImplementedError()

    @classmethod
    def dumps(cls, state):
        """Dump state to a serialized string.
        """
        raise NotImplementedError()


class MsgPackStateSerializer(object):
    """MsgPack serializer/deserializer.

    http://msgpack.org/
    """
    @staticmethod
    def _encode_object(obj):
        if isinstance(obj, collections.Iterable) and not isinstance(obj, collections.Mapping):
            return list(obj)
        else:  # pragma: no cover
            return obj

    @classmethod
    def loads(cls, plot, serialized):
        """Load state from a msgpack-serialized string.
        """
        import msgpack
        data = msgpack.unpackb(serialized)
        return states.PlotState(plot, data)

    @classmethod
    def dumps(cls, state):
        """Load state from a msgpack-serialized string.
        """
        import msgpack
        return msgpack.packb(state, default=cls._encode_object)
