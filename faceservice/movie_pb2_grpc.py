# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import movie_pb2 as movie__pb2


class FaceServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RecognizeFace = channel.unary_unary(
                '/movie.FaceService/RecognizeFace',
                request_serializer=movie__pb2.FaceRecognitionRequest.SerializeToString,
                response_deserializer=movie__pb2.FaceRecognitionResponse.FromString,
                )


class FaceServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def RecognizeFace(self, request, context):
        """unary API
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_FaceServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'RecognizeFace': grpc.unary_unary_rpc_method_handler(
                    servicer.RecognizeFace,
                    request_deserializer=movie__pb2.FaceRecognitionRequest.FromString,
                    response_serializer=movie__pb2.FaceRecognitionResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'movie.FaceService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class FaceService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def RecognizeFace(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/movie.FaceService/RecognizeFace',
            movie__pb2.FaceRecognitionRequest.SerializeToString,
            movie__pb2.FaceRecognitionResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class MovieServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.AddMovie = channel.unary_unary(
                '/movie.MovieService/AddMovie',
                request_serializer=movie__pb2.Movie.SerializeToString,
                response_deserializer=movie__pb2.AddMovieResponse.FromString,
                )
        self.AddMultipleMovies = channel.stream_unary(
                '/movie.MovieService/AddMultipleMovies',
                request_serializer=movie__pb2.Movie.SerializeToString,
                response_deserializer=movie__pb2.AddMultipleMoviesResponse.FromString,
                )
        self.MovieChat = channel.stream_stream(
                '/movie.MovieService/MovieChat',
                request_serializer=movie__pb2.Movie.SerializeToString,
                response_deserializer=movie__pb2.MovieNote.FromString,
                )


class MovieServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def AddMovie(self, request, context):
        """unary API
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddMultipleMovies(self, request_iterator, context):
        """client streaming API
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def MovieChat(self, request_iterator, context):
        """bidirectional streaming API
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MovieServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'AddMovie': grpc.unary_unary_rpc_method_handler(
                    servicer.AddMovie,
                    request_deserializer=movie__pb2.Movie.FromString,
                    response_serializer=movie__pb2.AddMovieResponse.SerializeToString,
            ),
            'AddMultipleMovies': grpc.stream_unary_rpc_method_handler(
                    servicer.AddMultipleMovies,
                    request_deserializer=movie__pb2.Movie.FromString,
                    response_serializer=movie__pb2.AddMultipleMoviesResponse.SerializeToString,
            ),
            'MovieChat': grpc.stream_stream_rpc_method_handler(
                    servicer.MovieChat,
                    request_deserializer=movie__pb2.Movie.FromString,
                    response_serializer=movie__pb2.MovieNote.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'movie.MovieService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class MovieService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def AddMovie(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/movie.MovieService/AddMovie',
            movie__pb2.Movie.SerializeToString,
            movie__pb2.AddMovieResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def AddMultipleMovies(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_unary(request_iterator, target, '/movie.MovieService/AddMultipleMovies',
            movie__pb2.Movie.SerializeToString,
            movie__pb2.AddMultipleMoviesResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def MovieChat(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(request_iterator, target, '/movie.MovieService/MovieChat',
            movie__pb2.Movie.SerializeToString,
            movie__pb2.MovieNote.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
