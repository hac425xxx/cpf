import os


def is_empty(dir):
    if os.path.isdir(dir) and len(os.listdir(dir)) == 0:
        return True

    return False


print is_empty("/tmpxxx/")
