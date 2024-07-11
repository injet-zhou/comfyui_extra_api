import enum
import os
from .cache import cached_data_for_file
import re
import folder_paths as fp

available_networks = {}
available_network_aliases = {}
loaded_networks = []
loaded_bundle_embeddings = {}
networks_in_memory = {}
available_network_hash_lookup = {}
forbidden_network_aliases = {}


def read_metadata_from_safetensors(filename):
    import json

    with open(filename, mode="rb") as file:
        metadata_len = file.read(8)
        metadata_len = int.from_bytes(metadata_len, "little")
        json_start = file.read(2)

        assert metadata_len > 2 and json_start in (
            b'{"',
            b"{'",
        ), f"{filename} is not a safetensors file"
        json_data = json_start + file.read(metadata_len - 2)
        json_obj = json.loads(json_data)

        res = {}
        for k, v in json_obj.get("__metadata__", {}).items():
            res[k] = v
            if isinstance(v, str) and v[0:1] == "{":
                try:
                    res[k] = json.loads(v)
                except Exception:
                    pass

        return res


class SdVersion(enum.Enum):
    Unknown = 1
    SD1 = 2
    SD2 = 3
    SDXL = 4


metadata_tags_order = {
    "ss_sd_model_name": 1,
    "ss_resolution": 2,
    "ss_clip_skip": 3,
    "ss_num_train_images": 10,
    "ss_tag_frequency": 20,
}


class NetworkOnDisk:
    def __init__(self, name, filename):
        self.name = name
        self.filename = filename
        self.metadata = {}
        self.is_safetensors = os.path.splitext(filename)[1].lower() == ".safetensors"

        def read_metadata():
            metadata = read_metadata_from_safetensors(filename)

            return metadata

        if self.is_safetensors:
            try:
                self.metadata = cached_data_for_file(
                    "safetensors-metadata", "lora/" + self.name, filename, read_metadata
                )
            except Exception as e:
                print(e, f"reading lora {filename}")

        if self.metadata:
            m = {}
            for k, v in sorted(
                self.metadata.items(), key=lambda x: metadata_tags_order.get(x[0], 999)
            ):
                m[k] = v

            self.metadata = m

        self.alias = self.metadata.get("ss_output_name", self.name)

        self.hash = None
        self.shorthash = None
        # self.set_hash(
        #     self.metadata.get('sshs_model_hash') or
        #     hashes.sha256_from_cache(self.filename, "lora/" + self.name, use_addnet_hash=self.is_safetensors) or
        #     ''
        # )

        self.sd_version = self.detect_version()

    def detect_version(self):
        if str(self.metadata.get("ss_base_model_version", "")).startswith("sdxl_"):
            return SdVersion.SDXL
        elif str(self.metadata.get("ss_v2", "")) == "True":
            return SdVersion.SD2
        elif len(self.metadata):
            return SdVersion.SD1

        return SdVersion.Unknown

    # def set_hash(self, v):
    #     self.hash = v
    #     self.shorthash = self.hash[0:12]

    #     if self.shorthash:
    #         import networks
    #         networks.available_network_hash_lookup[self.shorthash] = self

    # def read_hash(self):
    #     if not self.hash:
    #         self.set_hash(hashes.sha256(self.filename, "lora/" + self.name, use_addnet_hash=self.is_safetensors) or '')

    def get_alias(self):
        if self.alias.lower() in forbidden_network_aliases:
            return self.name
        else:
            return self.alias


def natural_sort_key(s, regex=re.compile("([0-9]+)")):
    return [int(text) if text.isdigit() else text.lower() for text in regex.split(s)]


def walk_files(path, allowed_extensions=None):
    if not os.path.exists(path):
        return

    if allowed_extensions is not None:
        allowed_extensions = set(allowed_extensions)

    items = list(os.walk(path, followlinks=True))
    items = sorted(items, key=lambda x: natural_sort_key(x[0]))

    for root, _, files in items:
        for filename in sorted(files, key=natural_sort_key):
            if allowed_extensions is not None:
                _, ext = os.path.splitext(filename)
                if ext.lower() not in allowed_extensions:
                    continue

            if "/." in root or "\\." in root:
                continue

            yield os.path.join(root, filename)


def list_available_networks():
    available_networks.clear()
    available_network_aliases.clear()
    forbidden_network_aliases.clear()
    available_network_hash_lookup.clear()
    forbidden_network_aliases.update({"none": 1, "Addams": 1})

    lora_paths = fp.get_folder_paths("loras")

    candidates = []
    for lora_dir in lora_paths:
        candidates += list(
            walk_files(lora_dir, allowed_extensions=[".pt", ".ckpt", ".safetensors"])
        )
    for filename in candidates:
        if os.path.isdir(filename):
            continue

        name = os.path.splitext(os.path.basename(filename))[0]
        try:
            entry = NetworkOnDisk(name, filename)
        except OSError:  # should catch FileNotFoundError and PermissionError etc.
            print(f"Failed to load network {name} from {filename}", exc_info=True)
            continue

        available_networks[name] = entry

        if entry.alias in available_network_aliases:
            forbidden_network_aliases[entry.alias.lower()] = 1

        available_network_aliases[name] = entry
        available_network_aliases[entry.alias] = entry


def create_lora_json(obj, include_metadata=False):
    rt = {
        "name": obj.name,
        "alias": obj.alias,
        "path": obj.filename,
    }
    if include_metadata:
        rt["metadata"] = obj.metadata
    return rt


list_available_networks()
