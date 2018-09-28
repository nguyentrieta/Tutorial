import threading
import ctypes
import time
import inspect
import traceback

#https://gist.github.com/liuw/2407154
#http://code.activestate.com/recipes/496960-thread2-killable-threads/
 
def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble, 
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class Thread(threading.Thread):
    def _get_my_tid(self):
        """determines this (self's) thread id"""
        if not self.isAlive():
            raise threading.ThreadError("the thread is not active")
        
        # do we have it cached?
        if hasattr(self, "_thread_id"):
            return self._thread_id
        
        # no, look for it in the _active dict
        for tid, tobj in threading._active.items():
            if tobj is self:
                self._thread_id = tid
                return tid
        
        raise AssertionError("could not determine the thread's id")
    
    def raise_exc(self, exctype):
        """raises the given exception type in the context of this thread"""
        _async_raise(self._get_my_tid(), exctype)
    
    def terminate(self):
        """raises SystemExit in the context of the given thread, which should 
        cause the thread to exit silently (unless caught)"""
        self.raise_exc(Exception)

class GraceThread(Thread):
    class mpGraceExit(Exception): pass

    def terminate(self):
        self.raise_exc(self.mpGraceExit)

    def cleanup(self):
        """to be overide by subclass, can be a long cleanup"""
        pass

    def run(self):
        try:
            self.run_actual()
        except self.mpGraceExit as e:
            self.cleanup()
        finally:
            self.cleanup()


class f(GraceThread):
    def __init__(self, sl, c):
        self.sl = sl
        self.c = c

        super().__init__()

    def cleanup(self):
        'long cleanup'
        for i in range(3):
            print('cleanup', i)
            time.sleep(1)

    def run(self):
        print('tid:', self._get_my_tid(),  )
        try:
             while True:

                 print(self.c)
                 time.sleep(self.sl)
        except Exception as e:
            print('Exception!!')
            print(e)
            traceback.print_stack()
        finally:
            self.cleanup()
            print("outta here")


if __name__ == '__main__':
    t = f(10, '.')
    t.start()
    t.isAlive()



    t2 = f(0.5, '!')
    t2.start()

    time.sleep(2)

    t.terminate()

    t.join()
    t.isAlive()


    print('DOne')

    import pdb; pdb.set_trace()

    t2.terminate()

