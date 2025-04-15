import asyncio
import ssl
from mcp.server.fastmcp import FastMCP
import aiohttp
import traceback
from io import StringIO


from utils.file import create_mcp_image_set, create_mcp_video_set
from utils.types import CreateImage, CreateVideo, ImageRef


mcp = FastMCP("Luma MCP")
count = 1


@mcp.tool()
async def create_image(
    prompt: str,
    aspect_ratio: str = "16:9",
    model: str = "photon-1",
    image_ref: list[ImageRef] | None = None,
    style_ref: ImageRef | None = None,
    character_ref: list[str] | None = None,
    modify_image_ref: ImageRef | None = None,
):
    """Generates AI images using Luma API based on the provided parameters.

    Parameters:
        prompt: Text description of the image to generate
        aspect_ratio: Image dimensions - "1:1" (square), "16:9" (landscape), "9:16" (portrait),
                     "4:3", "3:4", "21:9", "9:21" (default: "16:9")
        model: AI model to use - "photon-1" (higher quality), "photon-flash-1" (faster) (default: "photon-1")
        image_ref: Up to 8 reference images with weights to influence generation (optional)
        style_ref: A single reference image with weight to influence style (optional)
        character_ref: Up to 4 character references as image URLs (optional)
        modify_image_ref: Single image to modify/enhance (optional)

    Returns:
        List containing triplets of [image_data, image_url, generation_id] for each image:
        - image_data: Image object that can be displayed directly in the MCP interface
        - image_url: String with URL to the generated image on Luma CDN
        - generation_id: Unique ID that can be used for referencing in future operations

    Technical Notes:
        - Performance: Uses parallel processing with asyncio.gather() for concurrent generation
        - Error Handling: All exceptions include detailed stack traces for debugging
        - Response Time: Typical generation takes 5-15 seconds depending on model complexity
        - For the prompt please as specific as possible and enhance the prompt as needed.
    """
    try:
        ssl_context = ssl._create_unverified_context()
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            params = CreateImage(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                model=model,
                image_ref=image_ref,
                style_ref=style_ref,
                character_ref=character_ref,
                modify_image_ref=modify_image_ref,
            )
            result = await create_mcp_image_set(params=params, session=session)
            return result
    except Exception as e:
        str_io = StringIO()
        traceback.print_exc(file=str_io)
        stack_trace_str = str_io.getvalue()
        return f"error in create_image: {str(e)}\n\nStack trace:\n{stack_trace_str}"


@mcp.tool()
async def create_video(
    prompt: str,
    aspect_ratio: str = "16:9",
    model: str = "ray-2",
    loop: bool = False,
    resolution: str = "720p",
    duration: str = "5s",
    frame0_image: str | None = None,
    frame1_image: str | None = None,
    frame0_id: str | None = None,
    frame1_id: str | None = None,
):
    """Generates AI videos using Luma API based on the provided parameters.

    Parameters:
        prompt: Text description of the video to generate
        aspect_ratio: Video dimensions - "1:1" (square), "16:9" (landscape), "9:16" (portrait),
                     "4:3", "3:4", "21:9", "9:21" (default: "16:9")
        model: AI model to use - "ray-2" (standard), "ray-flash-2" (faster), "ray-1-6" (legacy) (default: "ray-2")
        loop: Whether the video should loop seamlessly (default: False)
        resolution: Video quality - "4k", "1080p", "720p", "540p" (default: "720p")
        duration: Video length - "5s" or "9s" (default: "5s")
        frame0_image: URL of image to use as first frame (optional)
        frame1_image: URL of image to use as last frame (optional)
        frame0_id: Generation ID for first frame (UUID v4) (optional)
        frame1_id: Generation ID for last frame (UUID v4) (optional)

    Returns:
        List containing quartets of [thumbnail_image, video_url, image_url, generation_id] for each video:
        - thumbnail_image: Image object that can be displayed directly in the MCP interface
        - video_url: String with URL to the generated video on Luma CDN
        - image_url: String with URL to the thumbnail image on Luma CDN
        - generation_id: Unique ID that can be used for referencing in future operations

    Technical Notes:
        - Performance: Uses parallel processing with asyncio.gather() for concurrent generation
        - Error Handling: All exceptions include detailed stack traces for debugging
        - Keyframes: Providing frame0_image/frame1_image gives more control over video start/end points
        - Response Time: Typical video generation takes 15-60 seconds depending on duration and resolution
        - For the prompt please as specific as possible and enhance the prompt as needed.
    """
    try:
        ssl_context = ssl._create_unverified_context()
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            params = CreateVideo(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                model=model,
                loop=loop,
                resolution=resolution,
                duration=duration,
                frame0_image=frame0_image,
                frame1_image=frame1_image,
                frame0_id=frame0_id,
                frame1_id=frame1_id,
            )
            result = await create_mcp_video_set(params=params, session=session)
            return result
    except Exception as e:
        str_io = StringIO()
        traceback.print_exc(file=str_io)
        stack_trace_str = str_io.getvalue()
        return f"error in create_video: {str(e)}\n\nStack trace:\n{stack_trace_str}"
