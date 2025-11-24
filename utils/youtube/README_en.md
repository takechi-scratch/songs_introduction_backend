# "MIMI's Complete Song Introduction" ("MIMIさん全曲紹介") YouTube API Implementation Documentation

## Client Overview

"MIMI's Complete Song Introduction" is a web application operated by an individual as a hobby, aimed at promoting the activities of artist [MIMI](https://www.youtube.com/@MIMI...official).
The application provides features to record and display a list of songs composed by MIMI. Additionally, it offers song recommendations based on song analysis data manually created by the developer.

## Purpose of Using YouTube API

The application leverages the YouTube API to provide the following features:

1. **Video Metadata Retrieval**: Retrieves titles, descriptions, durations, and thumbnails, which are used in song list displays and detailed information pages.
2. **Video Embedding**: On video detail pages, embedding allows users to immediately play songs they're interested in.
3. **Automatic Playlist Generation**: Automatically creates YouTube playlists based on user preferences.

For details on actual usage scenarios, please refer to [this video](https://www.youtube.com/watch?v=81pjSTETDxQ).

## Code Details

The client's source code is publicly available on GitHub:

- Frontend: https://github.com/takechi-scratch/songs_introduction_www
- Backend: https://github.com/takechi-scratch/songs_introduction_backend

Here, we introduce the code that uses the YouTube Data API in the backend.


### 1. `api.py` - Core API Client

**Source Code**: https://github.com/takechi-scratch/songs_introduction_backend/blob/main/utils/youtube/api.py

**Purpose**: Manages all direct interactions with the YouTube Data API v3

**Key Classes and Functions**:

- **`OAuthClient`**: OAuth 2.0 authentication and token lifecycle management
  - Manages access token refresh using refresh tokens
  - Implements automatic token renewal using APScheduler
  - Provides methods for playlist creation and video insertion

- **`list_videos(video_ids: list[str])`**: Retrieves video metadata in batches
  - Fetches video information using API key
  - Divides API requests into batches of 50 videos to minimize quota consumption

**OAuth 2.0 Flow Implementation**:
```
1. Initial Setup: Store refresh_token in environment variables
2. Token Refresh: Obtain and store access_token using refresh_token
3. Scheduling: Schedule next refresh 60 seconds before expiration
4. API Calls: Use a valid access_token for all authenticated requests
```

### 2. `playlists.py` - Playlist Management Layer

**Source Code**: https://github.com/takechi-scratch/songs_introduction_backend/blob/main/utils/youtube/playlists.py

**Key Classes**:

- **`PlaylistManager`**: Efficient playlist creation and management with caching
  - Implements a 3-day cache for identical video sets to reduce API calls
  - Implements HTTP error handling

**Cache Strategy**:
- Key: Set of video IDs
- Value: `YoutubePlaylist` object with metadata and creation time
- TTL: 3 days

## YouTube Data API Usage Details

### 1. Video Metadata Retrieval

**Use Case**: Retrieve video information to create song lists

**API Endpoint**: `GET /youtube/v3/videos`

**Quota Cost**: 1 unit per request

**Frequency**:
Periodic cache updates: Once per day, approximately 10 requests maximum

### 2. Playlist Creation

**Use Case**: Generate public playlists in response to user requests

**API Endpoint**: `POST /youtube/v3/playlists`

**Quota Cost**: 50 units per request

**Frequency**:
- Current: Approximately 5 requests per day (limited to developer testing)
- Future goal: 50 users accessing per day, 1 request per user, total of 50 requests

### 3. Playlist Item Insertion

**Use Case**: Add videos to created playlists

**API Endpoint**: `POST /youtube/v3/playlistItems`

**Quota Cost**: 50 units per video

**Frequency**:
Currently, it is only available to the developer, so experiments are conducted within the range of up to 200 requests (10000 / 50 = 200) to avoid exceeding quota costs.

Future goals:

- Maximum 50 videos per playlist creation
- Daily total: 50 (users/day) * 50 (videos/user) = 2500 video insertions


### Integration with Frontend (Backend API Details)

Backend API: https://mimi-api.takechi.f5.si/docs/

1. **POST `/playlists/create`**:
   - Creates a playlist from user requests
   - Returns the playlist URL
   - Implements caching feature to reduce API calls

2. **GET `/songs/{song_id}`**:
   - Returns cached YouTube video data
   - Used for displaying detailed song information

3. **Background Jobs**:
   - Video data updates (daily)
   - Quota usage monitoring and notifications (planned for implementation)
