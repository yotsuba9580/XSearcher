# XSearcher

A Twitter crawler tool based on `twikit` that supports:
- Iterative traversal of followers and followings starting from seed users to collect user information.
- Fetching historical tweets of a specific user.
- Polling to check for new tweets from a specified user.

## Requirements

- Python 3.12
- Miniconda environment

Dependencies are listed in `requirements.txt`.

## Setup

1. Create a Miniconda environment:
   ```bash
   conda create -n twitter_crawler python=3.12
   conda activate twitter_crawler
   pip install -r requirements.txt
   ```

2. Configure login credentials by running `login.py`:
   ```bash
   python login.py
   ```
   Input your username, email, and password. This will generate a `cookies.json` file for authentication.

## Usage

### XUserSearch
`XUserSearch.py` supports iterating through followers and followings of seed users to collect user information.

#### Configuration
Modify the `CONFIG` dictionary in `XUserSearch.py`:
```python
CONFIG = {
    "follow_limit": 20,  # Number of followers/followings fetched per request
    "depth_limit": 2,  # Recursive depth for traversal
    "delay_min": 5,  # Minimum random delay (seconds)
    "delay_max": 10,  # Maximum random delay (seconds)
}
```

Set the seed users by assigning values to the `USER_SCREEN_NAMES` list:
```python
USER_SCREEN_NAMES = ["seed_user1", "seed_user2"]
```

#### Output
The results will be saved to a CSV file (e.g., `user_data.csv`).

Run the script:
```bash
python XUserSearch.py
```

### XBeholder
`XBeholder.py` supports fetching historical tweets and polling for new tweets from a specific user.

#### Configuration
Modify the `CONFIG` dictionary in `XBeholder.py`:
```python
CONFIG = {
    "delay_min": 3,  # Minimum random delay (seconds)
    "delay_max": 8,  # Maximum random delay (seconds)
    "max_tweets": 30,  # Maximum number of tweets to fetch
    "target_screen_name": "elonmusk",  # Target user's screen_name
    "check_interval": 300,  # Time interval for checking new tweets (seconds)
    "check_offset": 30,  # Offset time for checking tweets (seconds)
    "history_tweets": True,  # Fetch historical tweets
    "realtime_tweets": True,  # Fetch new tweets in real-time
    "tweet_check_num": 10  # Number of tweets to check per interval
}
```

#### Output
The results will be saved to a CSV file (e.g., `elonmusk_tweets.csv`).

Run the script:
```bash
python XBeholder.py
```

## Sample Outputs

### XUserSearch
An example output file: [users_data.csv](./users_data.csv)

### XBeholder
An example output file: [elonmusk_tweets.csv](./elonmusk_tweets.csv)

## Notes
- Ensure `cookies.json` is valid and updated for successful authentication.
- Adjust configuration parameters based on your requirements.
