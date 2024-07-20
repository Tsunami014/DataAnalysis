from threading import Thread

statuses = {}

def wrapper(func): # TODO: Better name
    def func2(name):
        statuses[name] = {"State": 'STARTING'}
        def updatef(**news):
            statuses[name] = news
            statuses[name].update({"State": 'PROGRESS'})
        def runWhile():
            try:
                ret = func(updatef)
            except Exception as e:
                statuses[name] = {"State": 'ERROR', "Error": str(e)}
                return
            statuses[name] = {"State": 'FINISHED'}
            statuses[name].update(ret)
        Thread(target=runWhile, daemon=True).start()
    return func2
