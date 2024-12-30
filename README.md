# Wealthsimple AutoUploader

## Pre-requisites
1. Create a .env file with data for multiple users a sample .env is added:
2. <s>Set up python venv. There are 100s of tutorials on how to setup venv so I will not get into that. We only need requests module.</s> No more required as its dockerized now.

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
- Step 6: Run for the next account

#### Note:
The transactions are tracked in a temporary file that gets created during execution that maintains order hashes. If the order is found in user1 that matches hash or order found in user2 the order is not duplicated.

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

### TO DO
- Optimize multi user environment
- WIP on renewing ws access token in an automated way