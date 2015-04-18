class Scene(object):
    screen = None

    def draw(self):
        raise NotImplementedError()

    def handle(self, key_store):
        raise NotImplementedError()

    def update(self):
        raise NotImplementedError()