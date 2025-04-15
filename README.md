# Luma MCP

## Setup

1. Install Claude Desktop App
2. Get API Key from https://lumalabs.ai/api/keys
3. Run `sh setup.sh`, here it will ask the API Key - paste it

It will automatically open Claude Desktop (restart if needed)

## Run

Just open and use Claude Desktop or any MCP client.

## Functionality

### Image Generation
- Generate AI images with detailed text prompts
- Customize aspect ratio (1:1, 16:9, 9:16, 4:3, 3:4, 21:9, 9:21)
- Choose AI models (photon-1 for higher quality, photon-flash-1 for faster generation)
- Provide reference images to influence generation (up to 8 images with weights)
- Apply style references to control the artistic style
- Include character references (up to 4)
- Modify or enhance existing images

### Video Generation
- Create AI videos with detailed text prompts
- Customize aspect ratio (1:1, 16:9, 9:16, 4:3, 3:4, 21:9, 9:21)
- Select different AI models (ray-2, ray-flash-2, ray-1-6)
- Create seamlessly looping videos
- Set video resolution (4k, 1080p, 720p, 540p)
- Control duration (5s or 9s)
- Provide custom images for first and last frames for more control

## Technical Notes
- Performance: Uses parallel processing for concurrent generation
- Keyframes: Providing frame0_image/frame1_image gives more control over video start/end points
- Video Response Time: Typical video generation takes 15-60 seconds depending on duration and resolution
- Image Response Time: Typical generation takes 5-15 seconds depending on model complexity

