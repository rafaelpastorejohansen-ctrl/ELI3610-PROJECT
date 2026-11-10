import socket
import time

CAMERA_IP = "192.168.12.85"
CAMERA_PORT = 2115
REFERENCE_IDS = range(13)  # Endre til indeksene fra SOPAS
FIRST_REFERENCE = REFERENCE_IDS[0]


"""
Function to set the camera back to the first reference object.
Call this once at the start of main.py, in case an earlier run
was stopped before it could reset the camera.
"""
def reset_camera():
    buffer = b""

    with socket.create_connection((CAMERA_IP, CAMERA_PORT), timeout=5) as camera:
        camera.sendall(f"sINT 1 {FIRST_REFERENCE}".encode("ascii"))
        deadline = time.monotonic() + 3

        while True:
            start = buffer.find(b"\x02")
            end = buffer.find(b"\x03", start + 1) if start >= 0 else -1

            if end >= 0:
                reply = buffer[start + 1:end].decode("ascii")
                print("Kamera tilbakestilt:", repr(reply))
                return reply

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("Ingen respons ved tilbakestilling av kameraet")

            camera.settimeout(remaining)
            data = camera.recv(4096)
            if not data:
                raise ConnectionError("Kameraet lukket forbindelsen")
            buffer += data


"""
Function to read a card from the camera using the SOPAS protocol.
Returns the card value if a card is detected, otherwise returns None.
The camera is always left on the first reference object afterwards.
"""
def read_card():
    card_value = None
    buffer = b""

    with socket.create_connection((CAMERA_IP, CAMERA_PORT), timeout=30) as camera:

        #Function to send a command to the camera and receive a reply.
        def command(text):
            nonlocal buffer
            camera.sendall(text.encode("ascii"))
            deadline = time.monotonic() + 3

            while True:
                start = buffer.find(b"\x02")
                end = buffer.find(b"\x03", start + 1) if start >= 0 else -1

                if end >= 0:
                    reply = buffer[start + 1:end].decode("ascii")
                    buffer = buffer[end + 1:]
                    return reply

                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("Ingen komplett respons fra kameraet")

                camera.settimeout(remaining)
                data = camera.recv(4096)
                if not data:
                    raise ConnectionError("Kameraet lukket forbindelsen")
                buffer += data

        """
        Function to get the result from the camera after triggering a capture.
        Returns a tuple of (value, reference, image, decision) if a result is available, otherwise returns None.
        """
        def result():
            deadline = time.monotonic() + 5

            while True:
                reply = command("gRES")
                print("Svar på gRES:", repr(reply))

                if reply.split()[:2] != ["rgRES", "8005"]:
                    break

                if time.monotonic() >= deadline:
                    raise TimeoutError("Kameraet var opptatt i over 5 sekunder")

                time.sleep(0.1)

            if reply.strip() == "rgRES 0 No result available.":
                return None

            if not reply.startswith("rgRES 0 "):
                raise RuntimeError(f"gRES feilet: {reply!r}")

            start = reply.find("BEGIN;")
            if start < 0:
                print("Ukjent resultatformat, ignorerer:", repr(reply))
                return None

            start += len("BEGIN;")
            end = reply.find(";END", start)
            if end < 0:
                raise ValueError(
                    f"Resultatet mangler ';END': {reply!r}"
                    )

            fields = reply[start:end].split(";")
            if len(fields) != 4:
                raise ValueError(
                    f"Forventet 4 resultatfelt, fikk {len(fields)}: {reply!r}"
                    )

            value, reference, image, decision = fields
            return value, int(reference), int(image), int(decision)

        try:
            for reference_id in REFERENCE_IDS:
                text = f"sINT 1 {reference_id}"
                print("Sender:", repr(text))

                reply = command(text)
                print("Mottar:", repr(reply))

                if reply.split() != ["rsINT", "1", "0"]:
                    raise RuntimeError(reply)

                deadline = time.monotonic() + 5
                while command("gINT 1").split() != [
                    "rgINT", "1", "0", str(reference_id)
                ]:
                    if time.monotonic() >= deadline:
                        raise TimeoutError("Referansebyttet tok for lang tid")
                    time.sleep(0.1)

                time.sleep(1)

                previous_result = result()
                previous_image = (
                    previous_result[2] if previous_result is not None else None
                )

                print("Modus:", repr(command("gMOD")))
                print("Aktiv referanse:", repr(command("gINT 1")))

                reply = command("TRIG")
                print("Triggersvar:", repr(reply))

                if reply.split() != ["rTRIG", "0"]:
                    raise RuntimeError(reply)

                deadline = time.monotonic() + 5

                while True:
                    time.sleep(0.1)
                    current_result = result()

                    if current_result is not None:
                        value, reference, image, decision = current_result

                        print(
                            f"Forventer ref={reference_id}, "
                            f"forrige bilde={previous_image} | "
                            f"Mottatt ref={reference}, "
                            f"bilde={image}, decision={decision}"
                        )

                        if (
                            reference == reference_id
                            #and image != previous_image
                        ):
                            break

                    if time.monotonic() >= deadline:
                        raise TimeoutError("Ingen nytt bilderesultat")

                if decision == 2:
                    card_value = value
                    break

        finally:
            # Always leave the camera on the first reference object,
            # also if a card was found early or an error occurred.
            try:
                reply = command(f"sINT 1 {FIRST_REFERENCE}")
                print("Tilbake til første referanse:", repr(reply))
            except (TimeoutError, ConnectionError, OSError) as error:
                print("Kunne ikke tilbakestille referansen:", error)

    print(f"Card value: {card_value}")
    return card_value