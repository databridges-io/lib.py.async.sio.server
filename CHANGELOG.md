# Changelog

## Version 2.0.3

* Initial Release.

## Version 2.0.4 (2025-11-07)

### Fixed
- Fixed dependency version conflicts causing installation failures
- Removed `asyncio` dependency (Python standard library)
- Pinned `aiohttp` to compatible versions (`<3.13.0`)
- Added `tornado` as explicit dependency

### Dependencies
```
python-socketio==3.1.2
python-engineio==3.14.0
aiohttp>=3.8.1,<3.13.0
websocket-client>=1.0.0
tornado==6.5.2
```

## Version 2.0.5 (2025-11-07)

### Fixed

- Fixed dependency version conflicts causing installation failures
- Added `requests` as explicit dependency

### Dependencies

```
requests==2.32.5
```

