# Sports Instagram Auto-Poster

Posts soccer match updates (live scores, upcoming fixtures, results) to Instagram automatically, once every 10–20 minutes (randomized).

## Leagues covered
- Premier League
- MLS
- Bundesliga
- La Liga
- Serie A
- Ligue 1
- Champions League

## Setup

1. **Get a free football-data.org API key**
   Sign up at https://www.football-data.org/client/register
   Free tier gives 10 requests/min across all competitions.

2. **Copy and fill in `.env`**
   ```
   cp .env.example .env
   # edit .env with your Instagram username/password and API key
   ```

3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Run**
   ```
   python scheduler.py
   ```

## Files

| File | Purpose |
|------|---------|
| `scheduler.py` | Main loop — runs forever, posts on random interval |
| `fetcher.py` | Pulls match data from football-data.org API |
| `content.py` | Generates caption text and 1080x1080 image card |
| `poster.py` | Instagram login (session-cached) and photo upload |

## Notes

- Instagram session is cached in `session.json` (gitignored) so you only log in once.
- 2FA is supported — prompted in terminal on first login.
- Posting interval controlled by `POST_INTERVAL_MIN` / `POST_INTERVAL_MAX` in `.env`.
- Image cards use league colors (purple for PL, navy for MLS, red for Bundesliga, etc.).
