# API examples

## Create

```bash
curl -X POST http://127.0.0.1:8000/api/plans \
  -H "Content-Type: application/json" \
  -d '{
    "username": "Alex",
    "user_id": "alex01",
    "age": 28,
    "weight": 72,
    "goal": "muscle gain",
    "intensity": "medium"
  }'
```

## Feedback

```bash
curl -X POST http://127.0.0.1:8000/api/plans/alex01/feedback \
  -H "Content-Type: application/json" \
  -d '{"feedback":"Add more cardio and another recovery day."}'
```

## List

```bash
curl http://127.0.0.1:8000/api/users
```
