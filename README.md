from CameraLoader import CamLoader, CamLoader_Q

resize_fn = ResizePadding(inp_dets, inp_dets)
if type(source) is str and os.path.isfile(source):
    cam = CamLoader_Q(source, queue_size=1000, preprocess=preproc).start()
else:
    cam = CamLoader(source, preprocess=preproc).start()

#......
#ret = cam.grabbed()
while cam.grabbed():
 frame = cam.getitem()

cam.stop()
cv2.destroyAllWindows()
