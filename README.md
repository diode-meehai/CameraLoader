from CameraLoader import CamLoader, CamLoader_Q

resize_fn = ResizePadding(inp_dets, inp_dets)
def preproc(image):
    """preprocess function for CameraLoader.
    """
    image = resize_fn(image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


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
