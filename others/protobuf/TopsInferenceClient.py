import grpc
import TopsInference_pb2
import TopsInference_pb2_grpc

if __name__ == '__main__':
    #连接rpc服务器
    channel = grpc.insecure_channel('localhost:50051')
    #调用rpc服务
    TopsInference = TopsInference_pb2_grpc.TopsInferenceStub(channel)
    #server OK?
    TopsInference.serverLive(TopsInference_pb2.LiveRequest()) ==> bool
    #server Ready?
    TopsInference.serverReady(TopsInference_pb2.ReadyRequest()) ==> bool
    #model Config?
    TopsInference.modelConfig(TopsInference_pb2.ConfigRequest(name=, version=)) ==> bool
    #constrct input
    getInput <== fill value
    #infer
    infer
    #getOutput
    getoutput