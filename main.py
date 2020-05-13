from tello import TelloController, TelloVideoReceiver
import gbvision as gbv


def main():
    controller = TelloController()
    controller.connect()
    controller.start_stream()
    receiver = TelloVideoReceiver()
    win = gbv.StreamWindow('win', wrap_object=receiver)




if __name__ == '__main__':
    main()