"""
Class to represent JSON submitted in a request to create an image file.
    {
        "image-base64": "image"
    }

Created by https://app.quicktype.io/ and then tweaked
"""

# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = image_content_from_dict(json.loads(json_string))

from typing import Any, TypeVar, Type, cast


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class ImageContent:
    image_base64: str

    def __init__(self, image_base64: str) -> None:
        self.image_base64 = image_base64

    @staticmethod
    def from_dict(obj: Any) -> 'ImageContent':
        assert isinstance(obj, dict)
        image_base64 = obj.get("image-base64")
        return ImageContent(image_base64)

    def to_dict(self) -> dict:
        result: dict = {}
        result["image-base64"] = self.image_base64
        return result


def image_content_from_dict(s: Any) -> ImageContent:
    return ImageContent.from_dict(s)


def image_content_to_dict(x: ImageContent) -> Any:
    return to_class(ImageContent, x)
