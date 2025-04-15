import os
import re
import tempfile

import aiohttp
from mcp.server.fastmcp import Image

from utils.api import (
    get_completed_image,
    get_completed_video,
    submit_image,
    submit_video,
)
from utils.types import CreateImage, CreateVideo


async def create_mcp_image(image: str, session: aiohttp.ClientSession) -> Image:
    async with session.get(image) as response:
        temp_dir = tempfile.gettempdir()
        temp_str = str(image)
        path = os.path.join(temp_dir, re.sub(r"[^a-zA-Z0-9]", "_", temp_str))
        with open(path, "wb") as f:
            f.write(await response.read())
        return Image(path=path, format="png")


async def create_mcp_image_set(
    params: CreateImage, session: aiohttp.ClientSession
) -> list[Image | str]:
    body = {
        "prompt": params.prompt,
        "aspect_ratio": params.aspect_ratio,
        "model": params.model,
    }
    if params.image_ref:
        body["image_ref"] = [
            {"url": image_ref.url, "weight": image_ref.weight}
            for image_ref in params.image_ref
        ]
    if params.style_ref:
        body["style_ref"] = [
            {
                "url": params.style_ref.url,
                "weight": params.style_ref.weight,
            }
        ]
    if params.character_ref:
        body["character_ref"] = {
            "identity0": {
                "images": params.character_ref,
            }
        }
    if params.modify_image_ref:
        body["modify_image_ref"] = {
            "url": params.modify_image_ref.url,
            "weight": params.modify_image_ref.weight,
        }
    generation = await submit_image(
        body=body,
        session=session,
    )
    id = generation.get("id")
    if not id:
        raise Exception("No id found in generation")
    image_url = await get_completed_image(
        id=id,
        session=session,
    )
    image = await create_mcp_image(image=image_url, session=session)
    return [
        image,
        f"image_url: {image_url}",
        f"generation_id: {id}",
    ]


async def create_mcp_video_set(
    params: CreateVideo, session: aiohttp.ClientSession
) -> list[Image | str]:
    body = {
        "prompt": params.prompt,
        "aspect_ratio": params.aspect_ratio,
        "model": params.model,
    }

    keyframes = {}
    if params.frame0_image:
        keyframes["frame0"] = {
            "type": "image",
            "url": params.frame0_image,
        }
    if params.frame1_image:
        keyframes["frame1"] = {
            "type": "image",
            "url": params.frame1_image,
        }
    if params.frame0_id:
        keyframes["frame0"] = {
            "type": "generation",
            "id": str(params.frame0_id).lower(),
        }
    if params.frame1_id:
        keyframes["frame1"] = {
            "type": "generation",
            "id": str(params.frame1_id).lower(),
        }

    if bool(keyframes):
        body["keyframes"] = keyframes

    generation = await submit_video(
        body=body,
        session=session,
    )
    id = generation.get("id")
    if not id:
        raise Exception("No id found in generation")
    video_object = await get_completed_video(
        id=id,
        session=session,
    )
    video_url = video_object.get("video", None)
    image_url = video_object.get("image", None)
    image = await create_mcp_image(image=image_url, session=session)
    return [
        image,
        "above image is the thumbnail of the video",
        f"video_url: {video_url}",
        f"image_url: {image_url}",
        f"generation_id: {id}",
    ]
