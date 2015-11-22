class NetworkEvent(object):
    def _doNothing():
        return

    def __lt__(self, other):
        selfPriority = self.actionTime
        otherPriority = other.actionTime
        return selfPriority < otherPriority

    def __init__(self, creationTime, actionTime, callback=_doNothing, callbackArgs=[]):
        self.creationTime = creationTime
        self.actionTime = actionTime
        self.callback = callback
        self.callbackArgs = callbackArgs
        self.valid = True

    def action(self):
        return

    def act(self):
        self.action()
        self.callback(*self.callbackArgs)


class ComputerEvent(NetworkEvent):
    def __init__(self, computer, *args):
        super(ComputerEvent, self).__init__(*args)
        self.computer = computer


class BufferPacket(NetworkEvent):
    def __init__(self, destinations, packet, *args):
        super(BufferPacket, self).__init__(*args)
        self.destinations = destinations
        self.packet = packet


class SenseMedium(NetworkEvent):
    def __init__(self, *args):
        super(SenseMedium, self).__init__(*args)


class StartService(ComputerEvent):
    def action(self):
        self.computer.startService()


class DetectCollision(ComputerEvent):
    def action(self):
        self.computer.detectCollision()


class FinishTransmission(ComputerEvent):
    def action(self):
        self.computer.finishTransmission()


class StartTransmission(ComputerEvent):
    def action(self):
        self.computer.startTransmission()


class WaitSlot(ComputerEvent):
    pass
