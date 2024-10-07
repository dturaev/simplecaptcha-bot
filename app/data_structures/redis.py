from dataclasses import dataclass


@dataclass
class RedisBaseKey:
    # This should probably be an abstract base class
    @property
    def prefix(self) -> str:
        raise NotImplementedError

    def pack(self) -> str:
        attrs = [getattr(self, attr) for attr in self.__annotations__]
        return f"{self.prefix}:{':'.join(str(attr) for attr in attrs)}"

    @classmethod
    def parse(cls, key: str) -> "RedisBaseKey":
        parts = key.split(":")
        if parts[0] != cls.prefix:
            raise ValueError(f"Invalid key prefix: {parts[0]}")
        # print(dict(zip(cls.__annotations__, parts[1:])))
        return cls(**dict(zip(cls.__annotations__, parts[1:])))
