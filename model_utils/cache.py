import os
import json
import threading
import diskcache
import tqdm

current_dir = os.path.dirname(os.path.realpath(__file__))
cache_filename = os.path.join(current_dir, "cache.json")
cache_dir = os.path.join(current_dir, ".cache")
caches = {}
cache_lock = threading.Lock()


def make_cache(subsection: str) -> diskcache.Cache:
    return diskcache.Cache(
        os.path.join(cache_dir, subsection),
        size_limit=2**32,  # 4 GB, culling oldest first
        disk_min_file_size=2**18,  # keep up to 256KB in Sqlite
    )


def convert_old_cached_data():
    try:
        with open(cache_filename, "r", encoding="utf8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return
    except Exception:
        print("[ERROR] issue occurred while trying to read cache.json")
        return

    total_count = sum(len(keyvalues) for keyvalues in data.values())

    with tqdm.tqdm(total=total_count, desc="converting cache") as progress:
        for subsection, keyvalues in data.items():
            cache_obj = caches.get(subsection)
            if cache_obj is None:
                cache_obj = make_cache(subsection)
                caches[subsection] = cache_obj

            for key, value in keyvalues.items():
                cache_obj[key] = value
                progress.update(1)


def cache_fn(subsection):
    """
    Retrieves or initializes a cache for a specific subsection.

    Parameters:
        subsection (str): The subsection identifier for the cache.

    Returns:
        diskcache.Cache: The cache data for the specified subsection.
    """

    cache_obj = caches.get(subsection)
    if not cache_obj:
        with cache_lock:
            if not os.path.exists(cache_dir) and os.path.isfile(cache_filename):
                convert_old_cached_data()

            cache_obj = caches.get(subsection)
            if not cache_obj:
                cache_obj = make_cache(subsection)
                caches[subsection] = cache_obj

    return cache_obj


def cached_data_for_file(subsection, title, filename, func):
    """
    Retrieves or generates data for a specific file, using a caching mechanism.

    Parameters:
        subsection (str): The subsection of the cache to use.
        title (str): The title of the data entry in the subsection of the cache.
        filename (str): The path to the file to be checked for modifications.
        func (callable): A function that generates the data if it is not available in the cache.

    Returns:
        dict or None: The cached or generated data, or None if data generation fails.

    The `cached_data_for_file` function implements a caching mechanism for data stored in files.
    It checks if the data associated with the given `title` is present in the cache and compares the
    modification time of the file with the cached modification time. If the file has been modified,
    the cache is considered invalid and the data is regenerated using the provided `func`.
    Otherwise, the cached data is returned.

    If the data generation fails, None is returned to indicate the failure. Otherwise, the generated
    or cached data is returned as a dictionary.
    """

    existing_cache = cache_fn(subsection)
    ondisk_mtime = os.path.getmtime(filename)

    entry = existing_cache.get(title)
    if entry:
        cached_mtime = entry.get("mtime", 0)
        if ondisk_mtime > cached_mtime:
            entry = None

    if not entry or "value" not in entry:
        value = func()
        if value is None:
            return None

        entry = {"mtime": ondisk_mtime, "value": value}
        existing_cache[title] = entry

    return entry["value"]