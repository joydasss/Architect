"""Local gRPC demo; generate order_service_pb2 modules before running."""

from concurrent import futures
from threading import Thread

import grpc

import order_service_pb2 as messages
import order_service_pb2_grpc as service_bindings


class OrderService(service_bindings.OrderServiceServicer):
    def GetOrder(self, request, context):
        if request.order_id != "order-1042":
            context.set_trailing_metadata((("error-reason", "ORDER_NOT_FOUND"),))
            context.abort(grpc.StatusCode.NOT_FOUND, "Order does not exist")
        return messages.GetOrderResponse(
            order=messages.Order(
                order_id=request.order_id,
                status=messages.ORDER_STATUS_ALLOCATING,
                created_at_unix_ms=1_790_000_000_000,
            )
        )

    def UploadOrderEvents(self, request_iterator, context):
        accepted = 0
        for event in request_iterator:
            if not context.is_active():
                break
            if event.order_id:
                accepted += 1
        return messages.UploadSummary(accepted_count=accepted)

    def WatchOrder(self, request, context):
        events = (
            (1, messages.ORDER_STATUS_ACCEPTED),
            (2, messages.ORDER_STATUS_ALLOCATING),
            (3, messages.ORDER_STATUS_SHIPPED),
        )
        for sequence, status in events:
            if not context.is_active():
                return
            if sequence > request.after_sequence:
                yield messages.OrderEvent(
                    order_id=request.order_id,
                    sequence=sequence,
                    status=status,
                    occurred_at_unix_ms=1_790_000_000_000 + sequence,
                )

    def SyncInventory(self, request_iterator, context):
        for update in request_iterator:
            if not context.is_active():
                return
            accepted = bool(update.sku) and update.available_units >= 0
            yield messages.InventoryAck(
                update_id=update.update_id,
                accepted=accepted,
                reason="" if accepted else "Invalid SKU or quantity",
            )


def serve(server):
    server.start()
    server.wait_for_termination()


def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    service_bindings.add_OrderServiceServicer_to_server(OrderService(), server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    channel = grpc.insecure_channel(f"127.0.0.1:{port}")
    stub = service_bindings.OrderServiceStub(channel)

    try:
        response = stub.GetOrder(
            messages.GetOrderRequest(order_id="order-1042"),
            timeout=2.0,
            metadata=(("x-request-id", "demo-001"),),
        )
        print("unary:", response.order.order_id)

        uploaded = stub.UploadOrderEvents(
            iter(
                messages.OrderEvent(order_id="order-1042", sequence=sequence)
                for sequence in (10, 11, 12)
            ),
            timeout=2.0,
        )
        print("client stream accepted:", uploaded.accepted_count)

        watched = stub.WatchOrder(
            messages.WatchOrderRequest(order_id="order-1042", after_sequence=1),
            timeout=2.0,
        )
        print("server stream sequences:", [event.sequence for event in watched])

        acknowledgements = stub.SyncInventory(
            iter(
                messages.InventoryUpdate(
                    sku=sku,
                    available_units=units,
                    update_id=update_id,
                )
                for sku, units, update_id in (
                    ("SKU-RED-42", 18, "inv-001"),
                    ("SKU-BLUE-7", 0, "inv-002"),
                )
            ),
            timeout=2.0,
        )
        print("bidirectional acknowledgements:", [ack.accepted for ack in acknowledgements])

        try:
            stub.GetOrder(messages.GetOrderRequest(order_id="missing"), timeout=2.0)
        except grpc.RpcError as error:
            print("structured failure:", error.code().name, error.details())
            print("trailing metadata:", error.trailing_metadata())
    finally:
        channel.close()
        server.stop(grace=0).wait()


if __name__ == "__main__":
    main()