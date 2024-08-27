import random

def add(a):
    b = a*2
    return b


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def random_split_preserved_order(s, min_chunk=1, max_chunk=3):
    """
    Randomly split a string into chunks with preserved order.
    Each chunk will have a random length between min_chunk and max_chunk.

    Parameters:
    - s: The string to be split.
    - min_chunk: Minimum number of characters in a chunk.
    - max_chunk: Maximum number of characters in a chunk.

    Returns:
    A list of string chunks.
    """
    chunks = []
    i = 0
    while i < len(s):
        # Determine the size of the next chunk
        chunk_size = random.randint(min_chunk, max_chunk)
        # Slice the string to get the chunk
        chunk = s[i:i + chunk_size]
        chunks.append(chunk)
        # Update the index
        i += chunk_size
    return chunks