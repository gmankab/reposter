import reposter.core.types
import typing


async def parse_targets(
    target_any: reposter.core.types.target,
    to_call: typing.Callable,
) -> None:
    if isinstance(target_any, list):
        for subtarget in target_any:
            assert isinstance(subtarget, (str, int))
            await to_call(
                target=subtarget,
            )
    elif isinstance(target_any, (str, int)):
        await to_call(
            target=target_any,
        )
    else:
        raise AssertionError

