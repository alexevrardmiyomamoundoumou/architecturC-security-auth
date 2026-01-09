import time
from services.alert_service import get_rules
from pymongo import MongoClient
from elasticsearch import Elasticsearch
from datetime import datetime

client = MongoClient("mongodb://user:password@localhost:27017/logsdb")
db = client.logsdb
es = Elasticsearch("http://localhost:9200")

def check_rules():
    rules = get_rules()
    for rule in rules:
        {
  "aggs": {
    "groupAgg": {
      "terms": {
        "field": "source_ip.keyword",
        "size": 1
      },
      "aggs": {
        "conditionSelector": {
          "bucket_selector": {
            "buckets_path": {
              "compareValue": "_count"
            },
            "script": "params.compareValue > 5L"
          }
        }
      }
    },
    "groupAggCount": {
      "stats_bucket": {
        "buckets_path": "groupAgg._count"
      }
    }
  },
  "fields": [
    {
      "field": "@timestamp",
      "format": "date_time"
    },
    {
      "field": "timestamp",
      "format": "date_time"
    }
  ],
  "script_fields": {},
  "stored_fields": [
    "*"
  ],
  "runtime_mappings": {},
  "_source": {
    "excludes": []
  },
  "query": {
    "bool": {
      "must": [],
      "filter": [
        {
          "range": {
            "@timestamp": {
              "format": "strict_date_optional_time",
              "gte": "2026-01-07T22:51:48.140Z",
              "lte": "2026-01-07T23:06:48.141Z"
            }
          }
        }
      ],
      "should": [],
      "must_not": []
    }
  }
}
        alert = {
            "rule_id": rule["_id"],
            "triggered_at": datetime.utcnow(),
            "matches": 120,
            "status": "sent",
            "channels": ["email"]
        }
        db.alert_history.insert_one(alert)
        # Envoi notification (email, webhook)...

if __name__ == "__main__":
    while True:
        check_rules()
        time.sleep(300)  # toutes les 5 minutes
