import os
import requests


THREAT_TYPES = {
    0: "THREAT_TYPE_UNSPECIFIED",
    1: "MALWARE",
    2: "SOCIAL_ENGINEERING",
    3: "UNWANTED_SOFTWARE",
    4: "POTENTIALLY_HARMFUL_APPLICATION",
}


class ProtobufDecodeError(ValueError):
    """Raised when a Safe Browsing protobuf response cannot be decoded."""

def check_url_safety(urls_to_check):
    """
    Checks a list of URLs against the Google Safe Browsing API v5.
    
    :param api_key: Your Google Safe Browsing API key.
    :param urls_to_check: A list of URL strings to check (max 50).
    :return: Dict containing threat matches and cache duration.
    """
    # Safe Browsing v5 uses a GET request on /v5/urls:search
    url = "https://safebrowsing.googleapis.com/v5/urls:search"
    
    # Pass the URLs as repeating 'urls' query parameters
    api_key = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")
    if not api_key:
        print("GOOGLE_SAFE_BROWSING_API_KEY is not set")
        return {}

    params = {
        "key": api_key,
        "urls": urls_to_check
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        return _decode_search_urls_response(response.content)
        
    except requests.exceptions.HTTPError as http_err:
        status_code = http_err.response.status_code if http_err.response else "unknown"
        print(f"Safe Browsing API returned HTTP {status_code}: {http_err}")
    except requests.exceptions.Timeout:
        print("The request to the Safe Browsing API timed out after 10 seconds.")
    except requests.exceptions.ConnectionError as connection_err:
        print(f"Could not connect to the Safe Browsing API: {connection_err}")
    except ProtobufDecodeError as decode_err:
        print(f"Could not decode the Safe Browsing API response: {decode_err}")
    except requests.exceptions.RequestException as request_err:
        print(f"The Safe Browsing API request failed: {request_err}")
    
    return {}


def _decode_search_urls_response(data: bytes) -> dict:
    """Decode the protobuf response returned by Safe Browsing v5."""

    if not data:
        raise ProtobufDecodeError("the response body was empty")

    threats = []
    cache_duration = None
    for field_number, wire_type, value in _read_fields(data):
        if wire_type != 2:
            raise ProtobufDecodeError("unexpected top-level protobuf field")
        if field_number == 1:
            threats.append(_decode_threat_url(value))
        elif field_number == 2:
            cache_duration = _decode_duration(value)

    result = {"threats": threats}
    if cache_duration is not None:
        result["cacheDuration"] = cache_duration
    return result


def _decode_threat_url(data: bytes) -> dict:
    """Decode a v5 ThreatUrl message."""

    url = ""
    threat_types = []
    for field_number, wire_type, value in _read_fields(data):
        if field_number == 1 and wire_type == 2:
            try:
                url = value.decode("utf-8")
            except UnicodeDecodeError as error:
                raise ProtobufDecodeError("threat URL was not valid UTF-8") from error
        elif field_number == 2 and wire_type == 0:
            threat_types.append(THREAT_TYPES.get(value, f"UNKNOWN_{value}"))

    return {"url": url, "threatTypes": threat_types}


def _decode_duration(data: bytes) -> str:
    """Decode a google.protobuf.Duration message into Google's JSON form."""

    seconds = 0
    nanos = 0
    for field_number, wire_type, value in _read_fields(data):
        if wire_type != 0:
            raise ProtobufDecodeError("unexpected duration field")
        if field_number == 1:
            seconds = value
        elif field_number == 2:
            nanos = value

    if nanos == 0:
        return f"{seconds}s"
    fraction = f"{nanos:09d}".rstrip("0")
    return f"{seconds}.{fraction}s"


def _read_fields(data: bytes):
    """Yield ``(field number, wire type, value)`` tuples from protobuf data."""

    position = 0
    while position < len(data):
        key, position = _read_varint(data, position)
        field_number = key >> 3
        wire_type = key & 0x07
        if field_number == 0:
            raise ProtobufDecodeError("protobuf field number cannot be zero")

        if wire_type == 0:
            value, position = _read_varint(data, position)
        elif wire_type == 1:
            end = position + 8
            if end > len(data):
                raise ProtobufDecodeError("truncated fixed64 field")
            value = data[position:end]
            position = end
        elif wire_type == 2:
            length, position = _read_varint(data, position)
            end = position + length
            if end > len(data):
                raise ProtobufDecodeError("truncated length-delimited field")
            value = data[position:end]
            position = end
        elif wire_type == 5:
            end = position + 4
            if end > len(data):
                raise ProtobufDecodeError("truncated fixed32 field")
            value = data[position:end]
            position = end
        else:
            raise ProtobufDecodeError(f"unsupported protobuf wire type {wire_type}")

        yield field_number, wire_type, value


def _read_varint(data: bytes, position: int) -> tuple[int, int]:
    """Read one protobuf varint and return its value and next position."""

    value = 0
    shift = 0
    while position < len(data):
        byte = data[position]
        position += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, position
        shift += 7
        if shift >= 64:
            raise ProtobufDecodeError("protobuf varint is too long")

    raise ProtobufDecodeError("truncated protobuf varint")

