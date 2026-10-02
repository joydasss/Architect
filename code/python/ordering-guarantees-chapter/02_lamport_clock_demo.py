"""Show Lamport-clock propagation and the limit of scalar ordering."""


class LamportClock:
    def __init__(self, process_id: str) -> None:
        self.process_id = process_id
        self.value = 0

    def local_event(self) -> tuple[int, str]:
        self.value += 1
        return self.value, self.process_id

    def send(self) -> tuple[int, str]:
        return self.local_event()

    def receive(self, message: tuple[int, str]) -> tuple[int, str]:
        remote_value, _ = message
        self.value = max(self.value, remote_value) + 1
        return self.value, self.process_id


def main() -> None:
    service_a = LamportClock("service-a")
    service_b = LamportClock("service-b")

    created = service_a.local_event()
    sent = service_a.send()
    received = service_b.receive(sent)
    dependent_update = service_b.local_event()

    print("A created event:", created)
    print("A sent message:", sent)
    print("B received message:", received)
    print("B dependent update:", dependent_update)
    print("Known causal order:", sent[0] < received[0] < dependent_update[0])

    independent_a = service_a.local_event()
    independent_b = service_b.local_event()
    stable_total_order = sorted(
        [independent_a, independent_b], key=lambda stamp: (stamp[0], stamp[1])
    )
    print("Independent events:", independent_a, independent_b)
    print("Deterministic tie-break order:", stable_total_order)
    print("The tie-break is not evidence that one event caused the other.")


if __name__ == "__main__":
    main()