from controller.control import MainController
import pygame


def main():
    pygame.init()
    controller = MainController()
    controller.run()


if __name__ == '__main__':
    main()
