__author__ = 'tstrinity'

def get_result_dic(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


def timer(f):
    def _timer(*args, **kwargs):
        import time
        t = time.time()
        result = f(*args, **kwargs)
        print f.__name__ + " Time: %f" % (time.time()-t)
        return result
    return _timer