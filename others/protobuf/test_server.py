from concurrent import futures
import time
import grpc
import test_pb2
import test_pb2_grpc

#实现proto文件中定义的GreeterServicer
class Greeter(test_pb2.GreeterServicer):
    #实现proto文件中定义的rpc调用
    def SayHello(self, request, context):
        return test_pb2.HelloReply(message = 'hello {msg}'.format(msg = request.name))

    def SayHelloAgain(self, request, context):
        return test_pb2.HelloReply(message='hello again {msg}'.format(msg = request.name))

def serve():
    #启动rpc服务
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    test_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(60*60*24) # one day in seconds
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
