# cloudflare-access-network-location

Container to update the Cloudflare Access Gateway Location based on current public ip


## Limitations

Only works with Cloudflare Access Network Locations with a Single IP Address

## NOTICE

This utilizes the AWS IP Check URL: checkip.amazonaws.com

## Requirements

| Env Variable | Value |
|:---:|:---:|
| EMAIL | Cloudflare Email |
| API_KEY |Cloudflare API Key or API Token |
| ACCOUNT_ID|Cloudflare Account ID |
| NETWORK_NAME | Precreated Cloudflare Zero Trust Gateway Location |
| LOG_LEVEL | Default: INFO |

Envrionment Variables Example File - `.env.example`

## Running

Schedule a CRON Job to run via docker run on single host

For Kubernetes, schedule pod as a CRON Job 