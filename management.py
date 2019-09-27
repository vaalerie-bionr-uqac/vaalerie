"""
created on friday September 27 2019

@author: William Begin <william.begin2@uqac.ca>
    M. Sc. (C) Sciences cliniques et biomediacles, UQAC
    Office: H2-1180

project: V.A.A.L.E.R.I.E. <vaalerie.uqac@gmail.com>
"""

from communication.publisher import Publisher


class Management:

    # Create new publisher instance
    publisher = Publisher()

    def do_stuff(self):
        self.publisher.general_publish(12.5)


# Initializing sequence code
if __name__ == '__main__':
    manager = Management()
    manager.do_stuff()
