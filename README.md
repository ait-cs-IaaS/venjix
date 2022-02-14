# Venjix

Venjix is an attack Framework for Security Trainings.

## Get list of Things

`GET /`

```bash
curl -i -H 'Authorization: Bearer 53CR3T' http://localhost:5000/
```

```json
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 24
Server: Werkzeug/2.0.2 Python/3.10.0

[
  "ping",
  "fail"
]
```

## Execute script

`POST /<script>`

```bash
curl -i -H 'Authorization: Bearer 53CR3T' http://localhost:5000/ping
```

```json
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 61
Server: Werkzeug/2.0.2 Python/3.10.0

{
  "response": "script started",
  "script_name": "ping"
}
```

## Execute script with JSON Body

`POST /<script>`

```bash
curl -i -H 'Content-Type: application/json' -d '{"callback":"http://localhost:9000/callback","args":"10.0.0.1"}' http://localhost:5000/ping
```

```json
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 61
Server: Werkzeug/2.0.2 Python/3.10.0

{
  "response": "script started",
  "script_name": "ping"
}
```

## Execute script with parameters

`POST /<script>`

```bash
curl -X POST -i http://localhost:5000/ping?callback=http://10.0.0.1/post
```

```json
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 61
Server: Werkzeug/2.0.2 Python/3.10.0

{
  "response": "script started",
  "script_name": "ping"
}
```
