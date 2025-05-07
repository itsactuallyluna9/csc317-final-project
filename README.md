# YOUTUBE (please don't C&D google)

A "recreation" of YouTube for CSC 317's Final Project, made completely in Python (plus ffmpeg).

## Features

* Account Authentication
    * Includes database-side password hashing
* Video Uploading
* Video Streaming (in multiple qualities)

## Installation / Running

For easiest installation, make sure you have UV installed.

Additionally, if you're running the server, make sure you have a recent version of ffmpeg on your PATH. (If you're running the client, this should be handled for you.)

```sh
$ uv run final_client
$ uv run final_server
```

## Video Methodology

When a video is uploaded, it first gets re-encoded with ffmpeg to a more compatable (and efficient) format (x264 video and AAC audio), and re-encoded into different "qualities", all lower or equal to the inital upload. (The server also stores a thumbnail, also generated using ffmpeg. This thumbnail isn't actually used anywhere as of writing this readme.)

When a client wants to stream a video, it requests a segment in an appropriate quality. It downloads the segment, and starts displaying it. While it displays this segment, it keeps downloading further segments in the background, switching the segment being displayed when needed, effectively streaming the video. This emulates YouTube's solution, with a little more simplicity (YouTube can stream the inital segment, where our client cannot at the moment).

(Note that, unlike YouTube, we also don't have logic to automatically lower the quality on slow network connections. Even YouTube struggles with this at times, so...)

### Protocol

The client and server use a JSON-based protocol, with the exception of file data (which are sent as raw bytes).

The server may return an error response (`type` being `ERROR` in the response) as a response to a request, with some message.

Some responses may be paginated (taking a `page_num` parameter). These responses return a "page result", containing a `result` (a list of results), `current_page` (equivalent to the `page_num`), the `max_page`, the `items_per_page`, and the total `number_of_items`.

The client can close the connection via closing their socket. No teardown handshake is needed.

All requests should have a `type` corresponding to the following:

#### Authentication

* `LOGIN` - (Requires a `username` and `password`.) Authencates an existing user. Will return the first page of the list of users on success to save a request. (Equivalent to `USERS` with `page_num` of 0.) Will return an error on an invalid username or password.
* `REGISTER` - (Requires a `username` and `password`.) Creates (and then authencates) a new user. Will return the first page of the list of users on success to save a request. (Equivalent to `USERS` with `page_num` of 0.) Will return an error if the user exists.
* `LOGOUT` - Logs out. Will never return an error, even if the client is already logged out.

#### Listing

* `USERS` - (Requires a `page_num`.) Returns a paginated list of users, containing their `username`, `joined_at` time, and the time of their `last_login`.
* `VIDEO_PAGE` - (Requires a `page_num` and an optional `author`.) Returns a paginated list of videos (by the author, if specified). Only returns the `title`, `id`, and `author` for the video. Will *not* return any videos that are still being processed by the server.

#### Videos

* `VIDEO_INFO` - (Requires a `video_id`.) Returns more information for a specified `video_id`, if it exists. (Returns the `id`, `title`, `author`, `duration`, `num_segments`, `max_quality`, and the `uploaded_date`.)
* `VIDEO` - (Requires a `video_id`, `quality`, and a `segment_id`.) "Streams" a video (grabbing the segment of `segment_id`) with the specified `quality`. The server will send the `file_size`, and then wait for an acknowlegement (`type` = `ACK`) before sending the file as raw bytes. Will return an error if the file does not exist, or if the client does not properly complete the handshake.
* `UPLOAD` - (Requires the `title`, the `file_size`, and the original filename as `target`.) Uploads a video, processing it in the background. If the client is logged in, the server will send an acknowlegement (`type` = `ACK`), and then the client should send the video as raw bytes. The server will then return the `video_id` if the upload is successful. If something goes wrong, the server will return the appropriate error.
* `DELETE` - (Requires a `video_id`.) Deletes the specified video, if you are the author *and* if the video exists.

#### Debug

These commands are only for debugging, and are not accessible in the client.

* `DBG_REPROCESS_VIDEO` - (Requires a `video_id`.) Instructs the server to reprocess the video asynchronously. (Recomputing the thumbnail and all quality segments and the database contents of the `duration`, `num_segments`, and `max_quality`. Approximately equivalent to reuploading the video, but without physically removing and reuploading the video.)

## Credits

* Luna (@itsactuallyluna9) - Server, Protocol
* Justin (@ringoldj) - Client, Interop between GUI and Server, Protocol
* Arjay (@arjay464) - GUI, Protocol
* Trey (@saturnwillbemine) - Database Help, Protocol
* Aras (@Arasyilmaz1) - Client's Delete Function
