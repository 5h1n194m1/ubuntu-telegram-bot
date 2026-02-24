def is_allowed(user_id, allowed_ids):
    return user_id in allowed_ids

def format_size(size_bytes):
    """Mengubah bytes ke format yang manusiawi (MB, GB)."""
    if size_bytes == 0: return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"