#! /usr/bin/env python3

# Copyright(c) 2017 Intel Corporation.
# License: MIT See LICENSE file in root directory.
# NPS

# pulls images from video device and places them in a Queue or starts an inference for them on a network processor

import cv2
import threading
import time
from log import logging
from queue import Queue
import settings


frame_queue = Queue(1)
class VideoProcessor:
    def __init__(self,
                 video_file: str,
                 request_video_width: int = 640,
                 request_video_height: int = 480,
                 output_queue: Queue = None):

        self._video_file = video_file
        self._request_video_width = request_video_width
        self._request_video_height = request_video_height
        self._pause_mode = False

        # create the video device
        self._video_device = cv2.VideoCapture(self._video_file)

        self._fps = self._video_device.get(settings.CV_CAP_PROP_FPS)
        logging.debug('camera fps: ' + str(self._fps))
        # Request the dimensions
        self._video_device.set(cv2.CAP_PROP_FRAME_WIDTH,
                               self._request_video_width)
        self._video_device.set(cv2.CAP_PROP_FRAME_HEIGHT,
                               self._request_video_height)

        # save the actual dimensions
        self._actual_video_width = self._video_device.get(
            cv2.CAP_PROP_FRAME_WIDTH)
        self._actual_video_height = self._video_device.get(
            cv2.CAP_PROP_FRAME_HEIGHT)
        logging.info('actual video resolution: ' +
                     str(self._actual_video_width) + ' x ' +
                     str(self._actual_video_height))

        self._output_queue = output_queue

        self._worker_thread = None  #threading.Thread(target=self._do_work, args=())

        self.lock = threading.Lock()

    def start_processing(self):
        self._end_flag = False

        if (self._worker_thread == None):
            self._worker_thread = threading.Thread(
                target=self._do_work_queue, args=())

        self._worker_thread.start()

    def stop_processing(self):
        if (self._end_flag == True):
            # Already stopped
            return

        self._end_flag = True

    def get_latest_frame(self):
        self.lock.acquire()
        if self._output_queue.empty():
            frame = None
        else:
            frame = self._output_queue.get_nowait()
        self.lock.release()
        return frame

    def get_fps(self):
        return self._fps

    def read(self):
        ret_val, input_image = self._video_device.read()
        return ret_val, input_image

    # Thread target.  When call start_processing and initialized with an output queue,
    # this function will be called in its own thread.  it will keep working until stop_processing is called.
    # or an error is encountered.
    def _do_work_queue(self):
        frame_drop_count = 0
        while (not self._end_flag):
            try:
                ret_val, input_image = self._video_device.read()

                if (not ret_val):
                    continue
                self.lock.acquire()
                if not self._output_queue.empty():
                    self._output_queue.get_nowait()
                    frame_drop_count = frame_drop_count + 1
                else:
                    logging.debug("frame drop count:" + str(frame_drop_count))
                    frame_drop_count = 0
                self._output_queue.put(input_image)
                self.lock.release()

            except queue.Full:
                # the video device is probably way faster than the processing
                # so if our output queue is full sleep a little while before
                # trying the next image from the video.
                logging.debug('queue is full')

        print('exiting video_processor worker thread for queue')

    def cleanup(self):
        """Should be called once for each class instance when the class consumer is finished with it.

        :return: None
        """
        # wait for worker thread to finish if it still exists
        if (not (self._worker_thread is None)):
            # self._worker_thread.join()
            self._worker_thread = None

        self._video_device.release()

if __name__ == '__main__':
    vp = VideoProcessor('rtsp://admin:admin123@192.168.1.224/cam/realmonitor?channel=1&subtype=0',output_queue=frame_queue)
    vp.start_processing()
    while True:
        frame = vp.get_latest_frame()
        if frame is None:
            continue
        cv2.imshow('test',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
