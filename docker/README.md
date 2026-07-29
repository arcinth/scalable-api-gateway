# docker/

Supporting Docker assets that don't belong at the repository root (service
configs, entrypoint scripts, per-service Dockerfiles if the services ever
split into separate images).

The primary `Dockerfile` and `docker-compose.yml` for local/dev use live at
the repository root so they work with default `docker build .` /
`docker compose up` invocations without extra flags.
