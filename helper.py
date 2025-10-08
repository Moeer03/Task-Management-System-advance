# --- Helpers ---
def dict_from_row(row):
    return {
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "completion_flag": bool(row[3])
    }
