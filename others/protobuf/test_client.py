import grpc
import test_pb2
import test_pb2_grpc

def run():
    #连接rpc服务器
    channel = grpc.insecure_channel('localhost:50051')
    #调用rpc服务
    stub = test_pb2_grpc.GreeterStub(channel)
    response = stub.SayHello(test_pb2.HelloRequest(name='yangna'))
    print("Greeter client received: " + response.message)
    response = stub.SayHelloAgain(test_pb2.HelloRequest(name='natasha'))
    print("Greeter client received: " + response.message)

if __name__ == '__main__':
    run()