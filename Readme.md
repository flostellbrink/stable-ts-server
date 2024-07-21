# Server for Stable Timestamps for Whisper

Exposes [stable-ts](https://github.com/jianfch/stable-ts) align api as a service.

See [OpenAPI Documentation](https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/flostellbrink/stable-ts-server/main/openapi.json) for more information.

## Usage

Model is one of: 'tiny', 'tiny.en', 'base', 'base.en', 'small', 'small.en', 'medium', 'medium.en', 'large-v1', 'large-v2', 'large-v3', or 'large'

```bash
docker run -e MODEL="large-v3" -v /app/.cache/whisper -p 8080:8080 flostellbrink/stable-ts-server
```

## Build

```bash
pipenv install
pipenv run dev
```
