# Wealthsimple AutoUploader

## Pre-requisites
1. Create a .env file with following data:
    1. USERNAME=**wealthsimple user name**
    2. PASSWORD=**wealthsimple password**
    3. CLIENT_ID=**welthsimple client id**

    4. WS_TOKEN_URL=https://api.production.wealthsimple.com/v1/oauth/v2/token
    5. WS_WEB_URL=https://my.wealthsimple.com
    6. WS_OTP_CLAIM=**your otp claim**
    7. WS_USER_SESSION_ID=**your session id**
    8. WS_DEVICE_ID=**your device id**

    9. GHOSTFOLIO_USER_TOKEN=**your ghost folio user token**

    
    10. GHOSTFOLIO_URL=**http://localhost:3333/api/v1**

2. Set up python venv. There are 100s of tutorials on how to setup venv so I will not get into that. We only need requests module.

### How to get wealthsimple credentials:
1. Log in to wealthsimple account
2. Open browser developer tab and look for header section in network calls.
3. You can find client id, otp claim, user session id and device id.

### Create a map.json file in the root folder your schema should be:
```json
{
    "markets": {
        "include": {
            "TSX": "TO",
            "AEQUITAS NEO EXCHANGE": "NE"
        },
        "exclude": {
            "BATS": "",
            "NYSE": ""
        }
    },
    "symbols": {
        "CASH": "HSAV.TO"
    }
}
```

- Map markets that you want symbols to include suffixes and those where you do not want suffixes.
- The symbols branch will lookup any **CASH** symbol in WS transactions. If there are multiple I have not dealt with this situation. So as the code is opensource feel free to change this.

### Execution steps
- Step 1: Get wealthsimple data for the given range. Ideally we can keep this to one day e.g. 2024-12-01T00:00:00.999Z to 2024-12-01T23:59:59.999Z
- Step 2: Parse this information to get the accounts created in wealthsimple segregating cash transactions and orders
- Step 3: Once parsing is done we get additional information like stock exchange data for the symbol in orders.
- Step 4: Prepare the data for posting into ghostfolio
- Step 5: Post data to ghostfolio

### How to run
within your venv: 
```bash
python main.py
```

### How to run with docker
```bash
docker build -t wealthsimple-autouploader -f Dockerfile $PWD
docker run wealthsimple-autouploader
```
