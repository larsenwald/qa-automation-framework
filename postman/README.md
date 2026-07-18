# Postman / Newman

The collection mirrors the pytest API suite, so the API can also be checked by hand in Postman or from CI
with Newman.

**In Postman:** import both JSON files, select the *ShopLite local* environment, and run the collection
in order. `Token - valid` stores `{{token}}` for the authenticated folder.

**From the command line:**

```bash
flask --app wsgi seed && flask --app wsgi run &
npx newman@6 run postman/ShopLite.postman_collection.json \
  -e postman/local.postman_environment.json \
  --reporters cli,junit --reporter-junit-export reports/newman.xml
```

The demo credentials in the environment file are seeded test data, not real secrets.
