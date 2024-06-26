#!/usr/bin/env python
from queue import Queue
from threading import Thread, Lock
import cv2
import time
import numpy as np

class CamLoader :
    def __init__(self, camera = 1, width = 320, height = 240) :
        self.stream = cv2.VideoCapture(camera)
        # self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        # self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        (self.ret, self.frame) = self.stream.read()
        self.started = False
        self.read_lock = Lock()

    def start(self) :
        if self.started:
            print ("already started!!")
            return None
        self.started = True
        self.thread = Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self) :
        while self.started :
            (ret, frame) = self.stream.read()
            self.read_lock.acquire()
            self.ret, self.frame = ret, frame
            self.read_lock.release()

    def grabbed(self):
        return self.ret

    def getitem(self) :
        self.read_lock.acquire()
        frame = self.frame.copy()
        self.read_lock.release()
        return frame

    def stop(self) :
        self.started = False
        self.thread.join()

    def __exit__(self, exc_type, exc_value, traceback) :
        self.stream.release()

class CamLoader_Q:
    """Use threading and queue to capture a frame and store to queue for pickup in sequence.
    Recommend for video file.

    Args:
        camera: (int, str) Source of camera or video.,
        batch_size: (int) Number of batch frame to store in queue. Default: 1,
        queue_size: (int) Maximum queue size. Default: 256,
        preprocess: (Callable function) to process the frame before return.
    """
    def __init__(self, camera, batch_size=1, queue_size=256, preprocess=None):
        self.stream = cv2.VideoCapture(camera)
        assert self.stream.isOpened(), 'Cannot read camera source!'
        self.fps = self.stream.get(cv2.CAP_PROP_FPS)
        self.frame_size = (int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)),
                           int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        # Queue for storing each frames.
        self.stopped = False
        self.batch_size = batch_size
        self.Q = Queue(maxsize=queue_size)

        self.preprocess_fn = preprocess

    def start(self):
        t = Thread(target=self.update, args=(), daemon=True).start()
        time.sleep(0.5)
        return self

    def update(self):
        while not self.stopped:
            if not self.Q.full():
                frames = []
                for k in range(self.batch_size):
                    ret, frame = self.stream.read()
                    if not ret:
                        self.stop()
                        return

                    if self.preprocess_fn is not None:
                        frame = self.preprocess_fn(frame)

                    frames.append(frame)
                    frames = np.stack(frames)
                    self.Q.put(frames)
            else:
                with self.Q.mutex:
                    self.Q.queue.clear()
            #time.sleep(0.05)

    def grabbed(self):
        """Return `True` if can read a frame."""
        return self.Q.qsize() > 0

    def getitem(self):
        return self.Q.get().squeeze()

    def stop(self):
        if self.stopped:
            return
        self.stopped = True
        #self.stream.release()

    def __len__(self):
        return self.Q.qsize()

    def __del__(self):
        if self.stream.isOpened():
            self.stream.release()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.stream.isOpened():
            self.stream.release()

# if __name__ == "__main__" :
#     vs = CamLoader().start()
#     while True :
#         frame = vs.getitem()
#         cv2.imshow('webcam', frame)
#         if cv2.waitKey(1) == 27 :
#             break
#
#     vs.stop()
#     cv2.destroyAllWindows()

    # # CamLoader_Q(cam_name, queue_size=1000, preprocess=None).start()
    # vs = CamLoader_Q(r'C:\Diode_Thonglor\Thonglor\Count pills\DataVDO\Rice_.mp4',queue_size=1000, preprocess=None).start()
    # while True :
    #     frame = vs.getitem()
    #     cv2.imshow('webcam', frame)
    #     if cv2.waitKey(1) == 27 :
    #         break
    #
    # vs.stop()
    # cv2.destroyAllWindows()