import pyrogram.methods.advanced.save_file
import pyrogram.session.session
import reposter.tg.chunk_gen
import pyrogram.client
import typing
import math


async def save_file_custom_wrapper(
    self: pyrogram.client.Client,
    path: str | typing.BinaryIO | reposter.tg.chunk_gen.ChunkGen,
    file_id: int | None = None,
    file_part: int = 0,
    progress: typing.Callable | None = None,
    progress_args: tuple = (),
):
    if isinstance(path, reposter.tg.chunk_gen.ChunkGen):
        # runs custom function if got async bytes generator
        return await save_file_from_bytes_gen(
            self=self,
            chunk_gen=path,
        )
    else:
        # runs default pyrofork's save_file function if got something else
        return await pyrogram.methods.advanced.save_file.SaveFile.save_file( # type: ignore
            self=self,
            path=path,
            file_id=file_id,
            file_part=file_part,
            progress=progress,
            progress_args=progress_args,
        )


async def save_file_from_bytes_gen(
    self: pyrogram.client.Client,
    chunk_gen: reposter.tg.chunk_gen.ChunkGen,
):
    '''
    - custom save_file variant that accepts async bytes generator
    - can be used only with big files
    - file size should be more than 10 * 1024 * 1024 bytes (10 megabytes)
    - can resend big file without using disk and without writing while file to disk
    - useful when file size is more then ram size
    '''
    assert self.me
    file_size_limit_mib = 4000 if self.me.is_premium else 2000
    session = pyrogram.session.session.Session(
        self,
        await self.storage.dc_id(), # type: ignore
        await self.storage.auth_key(), # type: ignore
        await self.storage.test_mode(), # type: ignore
        is_media=True,
    )
    await session.start()
    file_id = self.rnd_id()
    max_chunk_size = 512 * 1024
    file_total_parts: int = math.ceil(
        chunk_gen.total / max_chunk_size
    )
    chunk_index: int = 0
    file_size: int = 0
    async for chunk in chunk_gen:
        assert len(chunk) <= max_chunk_size
        assert chunk_index < file_total_parts
        if chunk_index + 1 != file_total_parts:
            assert len(chunk) % 1024 == 0
            assert max_chunk_size % len(chunk) == 0
        file_size += len(chunk)
        if file_size > file_size_limit_mib * 1024 * 1024:
            raise ValueError(f"can't upload files bigger than {file_size_limit_mib} MiB")
        rpc = pyrogram.raw.functions.upload.SaveBigFilePart( # type: ignore
            file_id=file_id,
            file_part=chunk_index,
            file_total_parts=file_total_parts,
            bytes=chunk
        )
        await session.invoke(rpc)
        chunk_index += 1
    await session.stop()
    return pyrogram.raw.types.input_file_big.InputFileBig(
        id=file_id,
        parts=file_total_parts,
        name=chunk_gen.name,
    )

