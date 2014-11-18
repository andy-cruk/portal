from threading import Thread


def async(gen):
    def func(*args, **kwargs):
        it = gen(*args, **kwargs)
        result = next(it)
        Thread(target=lambda: list(it)).start()
        return result
    return func