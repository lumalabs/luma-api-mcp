# Luma MCP

## Setup & Run

1. Install Claude Desktop App or any MCP client
2. Get API Key from https://lumalabs.ai/api/keys
3. Run `sh setup.sh`, here it will ask the API Key - paste it from 2.

## Run

Open Claude Desktop or any MCP client

## Features

### Create Image

-   `prompt`: text
-   `aspect_ratio`: "1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21" (default: "16:9")
-   `model`: "photon-1", "photon-flash-1" (default: "photon-1")
-   `image_ref`: list of image URLs with weights to influence generation (optional), max 8
-   `style_ref`: single image URL with weight to influence style (optional), max 1
-   `character_ref`: list of character image URLs (optional), max 4
-   `modify_image_ref`: single image URL to modify with weight (optional), max 1

### Create Video

-   `prompt`: text
-   `aspect_ratio`: "1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21" (default: "16:9")
-   `model`: "ray-2", "ray-flash-2", "ray-1-6" (default: "ray-2")
-   `loop`: boolean (default: false)
-   `resolution`: "540p", "720p", "1080p", "4k" (default: "720p")
-   `duration`: "5s", "9s" (default: "5s")
-   `frame0_image`: image URL (optional)
-   `frame1_image`: image URL (optional)
-   `frame0_id`: generation ID (optional)
-   `frame1_id`: generation ID (optional)
