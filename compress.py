from io import BytesIO

def zlib_compress(data: bytearray, chunk_size: int = 1048576, level: int = 6) -> bytearray:
    import zlib

    if not data:
        return bytearray()

    buffer = BytesIO()
    compressor = zlib.compressobj(level=level)

    data_view = memoryview(data)
    data_len = len(data)
    index = 0

    while index < data_len:
        end = min(index + chunk_size, data_len)
        chunk = data_view[index:end]
        compressed = compressor.compress(chunk)
        if compressed:
            buffer.write(compressed)
        index = end

    final = compressor.flush()
    if final:
        buffer.write(final)

    return bytearray(buffer.getvalue())

def zlib_decompress(data, chunk_size: int = 1048576) -> bytearray:
    import zlib

    if not data:
        return bytearray()

    buffer = BytesIO()
    decompressor = zlib.decompressobj()

    data_view = memoryview(data)
    data_len = len(data)
    index = 0

    while index < data_len:
        end = min(index + chunk_size, data_len)
        chunk = data_view[index:end]
        decompressed = decompressor.decompress(chunk)
        if decompressed:
            buffer.write(decompressed)
        index = end

    final = decompressor.flush()
    if final:
        buffer.write(final)

    return bytearray(buffer.getvalue())

def bz2_compress(data: bytearray, chunk_size: int = 1048576, level: int = 6) -> bytearray:
    import bz2

    if not data:
        return bytearray()

    buffer = BytesIO()
    compressor = bz2.BZ2Compressor(level)

    data_view = memoryview(data)
    data_len = len(data)
    index = 0

    while index < data_len:
        end = min(index + chunk_size, data_len)
        chunk = data_view[index:end]
        compressed = compressor.compress(chunk)
        if compressed:
            buffer.write(compressed)
        index = end

    final = compressor.flush()
    if final:
        buffer.write(final)

    return bytearray(buffer.getvalue())

def bz2_decompress(data, chunk_size: int = 1048576) -> bytearray:
    import bz2

    if not data:
        return bytearray()

    buffer = BytesIO()
    decompressor = bz2.BZ2Decompressor()

    data_view = memoryview(data)
    data_len = len(data)
    index = 0

    while index < data_len:
        end = min(index + chunk_size, data_len)
        chunk = data_view[index:end]
        try:
            decompressed = decompressor.decompress(chunk)
            if decompressed:
                buffer.write(decompressed)
        except Exception:
            return bytearray()
        index = end

    return bytearray(buffer.getvalue())

def lzma_compress(data: bytearray, chunk_size: int = 1048576, level: int = 6) -> bytearray:
    import lzma

    if not data:
        return bytearray()

    buffer = BytesIO()
    filters = [{"id": lzma.FILTER_LZMA2, "preset": level}]
    compressor = lzma.LZMACompressor(format=lzma.FORMAT_RAW, filters=filters)

    data_view = memoryview(data)
    data_len = len(data)
    index = 0

    while index < data_len:
        end = min(index + chunk_size, data_len)
        chunk = data_view[index:end]
        compressed = compressor.compress(chunk)
        if compressed:
            buffer.write(compressed)
        index = end

    final = compressor.flush()
    if final:
        buffer.write(final)

    return bytearray(buffer.getvalue())

def lzma_decompress(data, chunk_size: int = 1048576) -> bytearray:
    import lzma

    if not data:
        return bytearray()

    buffer = BytesIO()
    decompressor = lzma.LZMADecompressor(format=lzma.FORMAT_RAW, filters=[{"id": lzma.FILTER_LZMA2}])

    data_view = memoryview(data)
    data_len = len(data)
    index = 0

    while index < data_len:
        end = min(index + chunk_size, data_len)
        chunk = data_view[index:end]
        try:
            decompressed = decompressor.decompress(chunk)
            if decompressed:
                buffer.write(decompressed)
        except Exception:
            return bytearray()
        index = end

    return bytearray(buffer.getvalue())
