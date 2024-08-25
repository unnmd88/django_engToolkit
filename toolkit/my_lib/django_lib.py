
class ProcessingDataFromRequest:
    def __init__(self, request):
        self.request = request
        print(self.request.GET)

data