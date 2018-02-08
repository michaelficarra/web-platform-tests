import traceback
from abc import ABCMeta, abstractmethod


class Protocol(object):
    __metaclass__ = ABCMeta

    implements = []

    def __init__(self, executor, browser):
        self.executor = executor
        self.browser = browser

        for cls in self.implements:
            name = cls.name
            assert not hasattr(self, name)
            setattr(self, name, cls(self))

    @property
    def logger(self):
        return self.executor.logger

    @property
    def is_alive(self):
        return True

    def setup(self, runner):
        msg = None
        try:
            msg = "Failed to start protocol connection"
            self.connect()

            msg = None

            for cls in self.implements:
                getattr(self, cls.name).setup()

            msg = "Post-connection steps failed"
            self.after_connect()
        except Exception:
            if msg is not None:
                self.logger.warning(msg)
            self.logger.error(traceback.format_exc())
            self.executor.runner.send_message("init_failed")
            return
        else:
            self.executor.runner.send_message("init_succeeded")

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def after_connect(self):
        pass

    def teardown(self):
        for cls in self.implements:
            getattr(self, cls.name).teardown()


class ProtocolPart(object):
    __metaclass__ = ABCMeta

    name = None

    def __init__(self, parent):
        self.parent = parent

    @property
    def logger(self):
        return self.parent.logger

    def setup(self):
        pass

    def teardown(self):
        pass


class BaseProtocolPart(ProtocolPart):
    __metaclass__ = ABCMeta

    name = "base"

    @abstractmethod
    def execute_script(self, script, async=False):
        pass

    @abstractmethod
    def set_timeout(self, timeout):
        pass

    @abstractmethod
    def wait(self):
        pass

    @property
    def current_window(self):
        pass

    @abstractmethod
    def set_window(self, handle):
        pass


class TestharnessProtocolPart(ProtocolPart):
    __metaclass__ = ABCMeta

    name = "testharness"

    @abstractmethod
    def load_runner(self, timeout):
        pass

    @abstractmethod
    def close_old_windows(self, url_protocol):
        pass

    @abstractmethod
    def get_test_window(self, window_id, parent):
        pass


class PrefsProtocolPart(ProtocolPart):
    __metaclass__ = ABCMeta

    name = "prefs"

    @abstractmethod
    def set(self, name, value):
        pass

    @abstractmethod
    def get(self, name):
        pass

    @abstractmethod
    def clear(self, name):
        pass


class StorageProtocolPart(ProtocolPart):
    __metaclass__ = ABCMeta

    name = "storage"

    @abstractmethod
    def clear_origin(self, name, url):
        pass


class SelectorProtocolPart(ProtocolPart):
    __metaclass__ = ABCMeta

    name = "select"

    @abstractmethod
    def elements_by_selector(self, selector):
        pass


class ClickProtocolPart(ProtocolPart):
    __metaclass__ = ABCMeta

    name = "click"

    @abstractmethod
    def element(self, element):
        pass


class TestDriverProtocolPart(ProtocolPart):
    __metaclass__ = ABCMeta

    name = "testdriver"

    @abstractmethod
    def send_message(self, message_type, status, message=None):
        pass
