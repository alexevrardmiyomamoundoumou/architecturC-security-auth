Key: errors:auth-service
Type: STRING
Value: 7
Description: Nombre d’erreurs détectées pour le service auth-service
TTL: 3600 secondes

Key: errors:payment-service
Type: STRING
Value: 3
Description: Nombre d’erreurs détectées pour le service payment-service
TTL: 3600 secondes


# historique de recherche list

Key: recent_searches:Alex
Type: LIST
Value:
[
  "failed login",
  "payment timeout",
  "database connection error"
]
TTL: 1800 secondes

# cache d'evenements recents

Key: event:123456
Type: STRING (JSON)
TTL: 300 secondes
Value:
{
  "@timestamp": "2026-01-07T21:45:00Z",
  "level": "ERROR",
  "service": "auth-service",
  "message": "Failed login attempt"
}
