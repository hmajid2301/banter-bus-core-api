def validate(model, error_callback, *error_args):
    def outer(func):
        async def inner(sid, data, **kwargs):
            try:
                m = model(**data)
                return await func(sid, m, **kwargs)
            except Exception:
                return await error_callback(sid, *error_args)

        return inner

    return outer
