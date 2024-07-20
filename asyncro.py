from threading import Thread

statuses = {}

def wrapper(func): # TODO: Better name
    def func2(name, *args, **kwargs):
        statuses[name] = {"State": 'STARTING'}
        def updatef(**news):
            statuses[name] = news
            statuses[name].update({"State": 'PROGRESS'})
        def runWhile():
            try:
                ret = func(updatef, *args, **kwargs)
            except Exception as e:
                statuses[name] = {"State": 'ERROR', "Error": str(e)}
                return
            if ret is None:
                ret = {}
            statuses[name] = {"State": 'FINISHED'}
            statuses[name].update(ret)
        Thread(target=runWhile, daemon=True).start()
    return func2
