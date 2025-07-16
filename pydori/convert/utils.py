import gzip
import hashlib
import json
from collections.abc import Callable
from functools import lru_cache
from os import PathLike
from pathlib import Path
from typing import NamedTuple
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from sonolus.script.level import Level, LevelData
from sonolus.script.metadata import Tag


# Prefix added to item names
PREFIX = "pydori"

# Directory for caching downloaded content
CACHE_DIR = Path(__file__).parent.parent.parent / ".cache"


@lru_cache
def get_bytes(url: str) -> bytes:
    """Fetch bytes from URL with caching.

    Downloads content from the given URL and caches it locally to avoid repeated network requests.
    Uses a hash of the URL as the cache key.
    """
    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()
    if (CACHE_DIR / url_hash).exists():
        return (CACHE_DIR / url_hash).read_bytes()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }
    request = Request(url, headers=headers)
    with urlopen(request) as response:
        data = response.read()
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / url_hash).write_bytes(data)
    return data


def get_str(url: str) -> str:
    """Fetch URL content as a UTF-8 string."""
    return get_bytes(url).decode("utf-8")


def get_json(url: str) -> dict | list:
    """Fetch and parse JSON from URL."""
    return json.loads(get_str(url))


def get_json_gzip(url: str) -> dict | list:
    """Fetch and parse gzip-compressed JSON from URL."""
    data = get_bytes(url)
    return json.loads(gzip.decompress(data).decode("utf-8"))


def make_relative(path: str) -> str:
    """Convert absolute path to relative by removing leading slash."""
    if path and path[0] == "/":
        return path[1:]
    return path


def _ensure_dict(data: dict | list) -> dict:
    if isinstance(data, dict):
        return data
    raise TypeError("Expected a dict.")


class EntityData(NamedTuple):
    archetype: str
    data: dict[str, int | float]


def parse_entities(data: list[dict]) -> list[EntityData]:
    indexes_by_name = {e["name"]: i for i, e in enumerate(data) if "name" in e}
    return [
        EntityData(
            archetype=e["archetype"],
            data={d["name"]: d["value"] if "value" in d else indexes_by_name.get(d["ref"], 0) for d in e["data"]},
        )
        for e in data
    ]


def get_sonolus_level_item(name: str, base_url: str) -> dict:
    """Fetch a specific Sonolus level item by name."""
    data = get_json(urljoin(urljoin(base_url, "sonolus/levels/"), name + "?localization=en"))
    return _ensure_dict(data)["item"]


def get_level_items(base_url: str) -> list[dict]:
    """Fetch all level items from a Sonolus server."""
    levels_url = urljoin(base_url, "sonolus/levels/list?localization=en")
    page = 0
    results = []
    while True:
        data = _ensure_dict(get_json(levels_url + f"&page={page}"))
        results.extend(data["items"])
        page += 1
        if page >= data["pageCount"]:
            break
    return results


def get_playlist_items(base_url: str) -> list[dict]:
    """Fetch all playlist items from a Sonolus server."""
    playlist_url = urljoin(base_url, "sonolus/playlists/list?localization=en")
    page = 0
    results = []
    while True:
        data = _ensure_dict(get_json(playlist_url + f"&page={page}"))
        results.extend(data["items"])
        page += 1
        if page >= data["pageCount"]:
            break
    return results


def write_playlist_items(path: PathLike, tag: str | None, items: list[dict]):
    """Write playlist items to disk.

    Args:
        path: Directory where playlists will be written.
        tag: Optional tag to add to all playlists.
        items: List of playlist item dictionaries to write.
    """
    for item in items:
        pl_path = Path(path) / f"{PREFIX}-{item['name']}"
        pl_path.mkdir(parents=True, exist_ok=True)
        item = {
            "version": item["version"],
            "title": {"en": item["title"]},
            "subtitle": {"en": item["subtitle"]},
            "author": {"en": item["author"]},
            "levels": [f"{PREFIX}-{level_item['name']}" for level_item in item["levels"]],
            "tags": [Tag(title=tag["title"], icon=tag.get("icon")).as_dict() for tag in item["tags"]],
        }
        if tag:
            item["tags"].append(Tag(title=tag).as_dict())
        (pl_path / "item.json").write_text(json.dumps(item, ensure_ascii=False), encoding="utf-8")


def convert_sonolus_level_item(
    item: dict, base_url: str, tag: str | None, data_converter: Callable[[dict], LevelData]
) -> Level:
    """Download and convert a Sonolus item to a LevelData object.

    Args:
        item: Raw level item from Sonolus server.
        base_url: URL of the Sonolus server for downloading assets.
        tag: Optional tag to add to the level.
        data_converter: Function to convert level data.

    Returns:
        Converted level data.
    """
    tags = [Tag(title=tag["title"], icon=tag.get("icon")) for tag in item["tags"]]
    if tag:
        tags.append(Tag(title=tag))
    return Level(
        name=f"{PREFIX}-{item['name']}",
        rating=item["rating"],
        title=item["title"],
        artists=item["artists"],
        author=item["author"],
        description=item.get("description"),
        tags=tags,
        cover=get_bytes(urljoin(base_url, item["cover"]["url"].replace(" ", "%20"))),
        bgm=get_bytes(urljoin(base_url, item["bgm"]["url"].replace(" ", "%20"))),
        preview=get_bytes(urljoin(base_url, item["preview"]["url"].replace(" ", "%20")))
        if item.get("preview")
        else None,
        data=data_converter(
            _ensure_dict(get_json_gzip(urljoin(base_url, make_relative(item["data"]["url"].replace(" ", "%20")))))
        ),
    )
