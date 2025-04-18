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

    [Generation Notes]
        - When generating an image prompt, be detailed and enhance the prompt as necessary.
        - You can add additional stylistic details to the prompt if the user desires.
        - Use the defintions specified in [PARAMETERS] to guide the generation.

    [Parameters]
    prompt: Detailed text description of the image to generate. Be specific about subject, setting, lighting, mood, style, and composition.

    aspect_ratio: Image dimensions
    - "1:1" (square) - Best for portraits, icons, or symmetrical compositions
    - "16:9" (landscape) - Ideal for scenic views, cinematic shots (DEFAULT)
    - "9:16" (portrait) - Perfect for mobile wallpapers or vertical compositions
    - "4:3" - Standard display format for many devices
    - "3:4" - Alternative portrait orientation
    - "21:9" - Ultra-wide cinematic format
    - "9:21" - Ultra-tall format for specialized vertical content

    model:
    - "photon-1" - Higher quality with more detailed rendering (DEFAULT)
    - "photon-flash-1" - Faster generation with slightly reduced detail

    reference_options:
    - image_ref: Up to 8 reference images with weights (0.1-1.0) to influence overall generation
    - style_ref: Single reference image with weight to influence artistic style only
    - character_ref: Up to 4 character references to maintain consistent character appearance
    - modify_image_ref: Single source image to enhance or modify while preserving core elements

    [Usage Guidelines]
    1. ALWAYS use character_ref when user requests specific characters or consistent character appearance.
    2. Use style_ref when user wants to match a particular artistic style but not copy specific content.
    3. Use image_ref when user wants to influence both content and style of generation.
    4. Use modify_image_ref when enhancing or altering an existing image while maintaining its core elements.
    5. For best results, encourage detailed prompts with specific visual descriptions.
    6. When appropriate, enhance user prompts with additional details about lighting, composition, and atmosphere.
    7. As required based on what is user asking for, you can also use multiple reference images at once.

    [Returns]
        List containing triplets of [image_data, image_url, generation_id] for each image:
        - image_data: Image object that can be displayed directly in the MCP interface
        - image_url: String with URL to the generated image on Luma CDN
        - generation_id: Unique ID that can be used for referencing in future operations
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

    [Generation Notes]
        - When generating a video prompt, be detailed and enhance the prompt as necessary.
        - You can add additional stylistic details to the prompt if the user desires.
        - Use the defintions specified in [PARAMETERS] to guide the generation.
        - If the user asks for 10s video or a longer video, default to 9s.

    [Parameters]
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

    [Returns]
        List containing quartets of [thumbnail_image, video_url, image_url, generation_id] for each video:
        - thumbnail_image: Image object that can be displayed directly in the MCP interface
        - video_url: String with URL to the generated video on Luma CDN
        - image_url: String with URL to the thumbnail image on Luma CDN
        - generation_id: Unique ID that can be used for referencing in future operations
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
