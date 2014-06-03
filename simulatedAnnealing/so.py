import ctypes
lib = ctypes.CDLL("./libsa.so.1.0")

lib.solve("../gt/12.gt")