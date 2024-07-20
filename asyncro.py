from threading import Thread

statuses = {}

def wrapper(func): # TODO: Better name
    def func2(name):
        statuses[name] = {"State": 'STARTING'}
        def updatef(**news):
            statuses[name] = news
        def runWhile():
            ret = func(updatef)
            statuses[name] = {"State": 'FINISHED'}
            statuses[name].update(ret)
        Thread(target=runWhile, daemon=True).start()
    return func2
