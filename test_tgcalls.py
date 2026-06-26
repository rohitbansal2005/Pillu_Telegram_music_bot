from pytgcalls import GroupCallFactory
import inspect

class Dummy:
    def invoke(self):
        pass

gc = GroupCallFactory(Dummy()).get_group_call()
print(inspect.signature(gc.join))
print(inspect.signature(gc.start_audio))
print(inspect.signature(gc.play))
