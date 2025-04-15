from pydantic import BaseModel


class ImageRef(BaseModel):
    url: str
    weight: float = 1.0


class ModifyImageRef(BaseModel):
    url: str
    weight: float = 1.0


class CreateImage(BaseModel):
    prompt: str
    aspect_ratio: str = "16:9"
    model: str = "photon-1"
    image_ref: list[ImageRef] | None = None
    style_ref: list[ImageRef] | None = None
    character_ref: list[str] | None = None
    modify_image_ref: ModifyImageRef | None = None


class CreateVideo(BaseModel):
    prompt: str
    aspect_ratio: str = "16:9"
    model: str = "ray-2"
    loop: bool = False
    resolution: str = "720p"
    duration: str = "5s"
    frame0_image: str | None = None
    frame1_image: str | None = None
    frame0_id: str | None = None
    frame1_id: str | None = None
