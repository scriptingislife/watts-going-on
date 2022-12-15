# watts-going-on

Ingest Strava activities in Datadog using [IFTTT](https://ifttt.com/strava/triggers/new_activity_by_you) and AWS SAM.

## Get started

Create a [SSM Parameter](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) named `DDApiKey` containing a [Datadog API key](https://app.datadoghq.com/organization-settings/api-keys). If a different name is used for the parameter, update the `DDParamName` parameter in `template.yaml`

```
git clone https://github.com/scriptingislife/watts-going-on.git
cd watts-going-on
sam build
sam deploy --guided
```

## To do
- [ ] Separate API Gateway stages for `production` and `staging`
- [ ] SSM Parameter defined as code
- [ ] Pull additional data from Strava API